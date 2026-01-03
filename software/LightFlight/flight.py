import random
from typing import Dict, List, Any, Tuple
from pathlib import Path
import yaml

import sys
from pathlib import Path

WORK_DIR = Path('.').__str__()
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)


from software.utils.core import OSConnector
from software.utils.time import TimeMachine

CORPUS_PATH = Path("software") / "LightFlight" / "corpus"


class FlightSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.rng = random.Random(seed)
        self.os = OSConnector(session_id=os_cfg["session_id"], url=os_cfg["url"])
        self.time_machine = TimeMachine(rng=self.rng)

        with open(CORPUS_PATH / "flight.yaml") as f:
            info = yaml.safe_load(f)

        self.airlines = {a["code"]: a for a in info.get("airlines", [])}
        self.airports = {a["code"]: a for a in info.get("airports", [])}
        self.fares = info.get("fare_classes", [])
        self.sample_flights = info.get("sample_flights", [])
        self.promos = {p["code"]: p for p in info.get("promo_codes", [])}

        # persistent session state
        self.bookings: Dict[str, Dict[str, Any]] = {}
        self.holds: Dict[str, Dict[str, Any]] = {}
        self.wallet_balance = round(self.rng.uniform(200, 20000), 2)
        self.loyalty_accounts = {}
        self.preferences = {}

        # Pre-generate deterministic catalog and state for read-only endpoints
        self.flight_catalog: Dict[str, Dict[str, Any]] = {}
        self.routes_index: Dict[Tuple[str, str], List[str]] = {}
        self.seat_maps: Dict[str, Dict[str, str]] = {}
        self.operational_status: Dict[str, str] = {}
        self.delay_estimates: Dict[str, int] = {}
        self.baggage_info: Dict[str, Dict[str, Any]] = {}
        self._generate_catalog()

    def uuid(self) -> str:
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(self.rng.choices(alphabet, k=12))

    def _generate_catalog(self):
        # add explicit sample flights
        for f in self.sample_flights:
            fn = f.get("flight_no")
            price = round(f.get("base_price", 200) * (1 + self.rng.uniform(-0.2, 0.5)), 2)
            self.flight_catalog[fn] = {**f, "price": price}
            key = (f.get("origin"), f.get("dest"))
            self.routes_index.setdefault(key, []).append(fn)

            # seat map
            seats = {f"{r}{c}": "available" for r in range(1, 31) for c in ["A","B","C","D","E","F"]}
            booked = self.rng.sample(list(seats.keys()), k=int(len(seats) * 0.1))
            for s in booked:
                seats[s] = "booked"
            self.seat_maps[fn] = seats

            self.operational_status[fn] = self.rng.choice(["on_time", "delayed", "cancelled"])
            self.delay_estimates[fn] = self.rng.randint(0, 180) if self.operational_status[fn] != "on_time" else 0
            self.baggage_info[fn] = {"allowance": "1 checked + 1 carry-on", "fee_per_extra_kg": 30}

        # generate additional synthetic flights for common origin/dest pairs
        codes = list(self.airports.keys())
        for i in range(min(10, max(0, len(codes) - 1))):
            o = codes[self.rng.randrange(len(codes))]
            d = codes[self.rng.randrange(len(codes))]
            if o == d:
                continue
            fn = f"FL{self.uuid()}"
            duration = self.rng.randint(60, 900)
            price = round(self.rng.uniform(100, 1500), 2)
            airline = self.rng.choice(list(self.airlines.keys())) if self.airlines else "XX"
            self.flight_catalog[fn] = {"flight_no": fn, "airline": airline, "origin": o, "dest": d, "duration_min": duration, "price": price}
            self.routes_index.setdefault((o, d), []).append(fn)
            seats = {f"{r}{c}": "available" for r in range(1, 31) for c in ["A","B","C","D","E","F"]}
            booked = self.rng.sample(list(seats.keys()), k=int(len(seats) * 0.08))
            for s in booked:
                seats[s] = "booked"
            self.seat_maps[fn] = seats
            self.operational_status[fn] = self.rng.choice(["on_time", "delayed"])
            self.delay_estimates[fn] = 0 if self.operational_status[fn] == "on_time" else self.rng.randint(5, 240)
            self.baggage_info[fn] = {"allowance": "1 checked + 1 carry-on", "fee_per_extra_kg": 25}

    def get_session_dict(self):
        return {
            "bookings": list(self.bookings.values()),
            "holds": list(self.holds.values()),
            "wallet_balance": self.wallet_balance,
            "preferences": list(self.preferences.values())
        }

    def list_airlines(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.airlines.values())}

    def list_airports(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.airports.values())}

    def search_flights(self, origin: str, dest: str, date: str, passengers: int = 1) -> Dict[str, Any]:
        key = (origin, dest)
        flight_nos = self.routes_index.get(key, [])
        results = []
        for fn in flight_nos:
            f = self.flight_catalog[fn]
            results.append({"flight_no": fn, "airline": f.get("airline"), "duration_min": f.get("duration_min"), "price": round(f.get("price", 0) * passengers, 2)})
        return {"status": "ok", "output": results}

    def get_flight_details(self, flight_no: str) -> Dict[str, Any]:
        f = self.flight_catalog.get(flight_no)
        if not f:
            return {"status": "failed", "output": f"Flight {flight_no} not found"}
        return {"status": "ok", "output": f}

    def hold_seat(self, flight_no: str, seat_class: str, hold_minutes: int = 15) -> Dict[str, Any]:
        hid = f"hold_{self.uuid()}"
        self.holds[hid] = {"flight_no": flight_no, "seat_class": seat_class, "expires_in_min": hold_minutes}
        return {"status": "ok", "output": {"hold_id": hid, "expires_in_min": hold_minutes}}

    def confirm_payment(self, hold_id: str, amount: float, method: str = "card") -> Dict[str, Any]:
        if hold_id not in self.holds:
            return {"status": "failed", "output": "Hold not found"}
        if amount > self.wallet_balance:
            return {"status": "failed", "output": "Insufficient balance"}
        self.wallet_balance -= amount
        bid = f"booking_{self.uuid()}"
        hold = self.holds.pop(hold_id)
        self.bookings[bid] = {"booking_id": bid, "flight_no": hold["flight_no"], "seat_class": hold["seat_class"], "paid": amount, "status": "confirmed"}
        return {"status": "ok", "output": self.bookings[bid]}

    def book_flight(self, flight_no: str, passenger_info: Dict[str, Any], seat_class: str, promo: str | None = None) -> Dict[str, Any]:
        # quick book without hold
        price = round(self.rng.uniform(100, 2000), 2)
        if promo and promo in self.promos:
            promo_cfg = self.promos[promo]
            if "discount_pct" in promo_cfg:
                price = price * (1 - promo_cfg["discount_pct"]/100)
            elif "discount_amt" in promo_cfg:
                price = max(0, price - promo_cfg["discount_amt"]) 
        if price > self.wallet_balance:
            return {"status": "failed", "output": "Insufficient balance"}
        self.wallet_balance -= price
        bid = f"booking_{self.uuid()}"
        self.bookings[bid] = {"booking_id": bid, "flight_no": flight_no, "passenger": passenger_info, "seat_class": seat_class, "paid": price, "status": "confirmed"}
        return {"status": "ok", "output": self.bookings[bid]}

    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        # simple refund model
        refund = round(b.get("paid", 0) * self.rng.uniform(0, 1), 2)
        self.wallet_balance += refund
        b["status"] = "cancelled"
        b["refund"] = refund
        return {"status": "ok", "output": b}

    def list_bookings(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.bookings.values())}

    def get_booking(self, booking_id: str) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        return {"status": "ok", "output": b}

    def upgrade_seat(self, booking_id: str, target_class: str) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        extra = round(self.rng.uniform(20, 500), 2)
        if extra > self.wallet_balance:
            return {"status": "failed", "output": "Insufficient balance for upgrade"}
        self.wallet_balance -= extra
        b["seat_class"] = target_class
        b.setdefault("upgrades", []).append({"amount": extra, "to": target_class})
        return {"status": "ok", "output": b}

    def get_fare_rules(self, flight_no: str) -> Dict[str, Any]:
        return {"status": "ok", "output": {"flight_no": flight_no, "rules": "Mock fare rules: refundable conditions vary."}}

    def get_seat_map(self, flight_no: str) -> Dict[str, Any]:
        seats = self.seat_maps.get(flight_no)
        if not seats:
            return {"status": "failed", "output": f"Flight {flight_no} not found"}
        return {"status": "ok", "output": {"flight_no": flight_no, "seats": seats}}

    def check_in(self, booking_id: str) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        b["checked_in"] = True
        b["boarding_pass"] = f"BP-{booking_id}-{self.uuid()}"
        return {"status": "ok", "output": b}

    def get_boarding_pass(self, booking_id: str) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b or not b.get("boarding_pass"):
            return {"status": "failed", "output": "Boarding pass not available"}
        return {"status": "ok", "output": {"boarding_pass": b["boarding_pass"]}}

    def list_promotions(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.promos.values())}

    def apply_promo(self, promo_code: str, booking_id: str) -> Dict[str, Any]:
        p = self.promos.get(promo_code)
        b = self.bookings.get(booking_id)
        if not p:
            return {"status": "failed", "output": "Promo not found"}
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        # naive application: reduce paid
        old = b.get("paid", 0)
        if "discount_pct" in p:
            new = old * (1 - p["discount_pct"]/100)
        elif "discount_amt" in p:
            new = max(0, old - p["discount_amt"])
        else:
            new = old
        diff = round(old - new, 2)
        self.wallet_balance += diff
        b["paid"] = new
        b.setdefault("applied_promos", []).append(promo_code)
        return {"status": "ok", "output": b}

    def get_wallet_balance(self) -> Dict[str, Any]:
        return {"status": "ok", "output": self.wallet_balance}

    def add_funds(self, amount: float) -> Dict[str, Any]:
        self.wallet_balance += amount
        return {"status": "ok", "output": self.wallet_balance}

    def refund(self, booking_id: str) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        refund = b.get("refund") or 0
        self.wallet_balance += refund
        return {"status": "ok", "output": {"refunded": refund, "balance": self.wallet_balance}}

    def estimate_travel_time(self, origin: str, dest: str) -> Dict[str, Any]:
        # return heuristic
        return {"status": "ok", "output": {"origin": origin, "dest": dest, "est_hours": round(self.rng.uniform(1, 20),1)}}

    def suggest_connections(self, origin: str, dest: str) -> Dict[str, Any]:
        # suggest a connection via a random airport
        via = self.rng.choice(list(self.airports.keys()))
        return {"status": "ok", "output": [{"via": via, "total_duration": self.rng.randint(200, 1200)}]}

    def report_issue(self, booking_id: str, issue: str) -> Dict[str, Any]:
        ticket = f"ticket_{self.uuid()}"
        return {"status": "ok", "output": {"ticket": ticket, "booking_id": booking_id, "issue": issue}}

    def get_operational_status(self, flight_no: str) -> Dict[str, Any]:
        status = self.operational_status.get(flight_no, "unknown")
        return {"status": "ok", "output": {"flight_no": flight_no, "status": status}}

    def get_delay_estimate(self, flight_no: str) -> Dict[str, Any]:
        d = self.delay_estimates.get(flight_no, 0)
        return {"status": "ok", "output": {"flight_no": flight_no, "delay_min": d}}

    def get_baggage_info(self, flight_no: str) -> Dict[str, Any]:
        return {"status": "ok", "output": self.baggage_info.get(flight_no, {"allowance": "1 checked + 1 carry-on", "fee_per_extra_kg": 30})}

    def add_baggage(self, booking_id: str, kg: int) -> Dict[str, Any]:
        b = self.bookings.get(booking_id)
        if not b:
            return {"status": "failed", "output": "Booking not found"}
        fee = kg * 30
        if fee > self.wallet_balance:
            return {"status": "failed", "output": "Insufficient balance"}
        self.wallet_balance -= fee
        b.setdefault("baggage", 0)
        b["baggage"] += kg
        return {"status": "ok", "output": {"booking": b, "charged": fee}}

    def set_preference(self, key: str, value: Any) -> Dict[str, Any]:
        self.preferences[key] = value
        return {"status": "ok", "output": self.preferences}

    def get_preference(self, key: str) -> Dict[str, Any]:
        return {"status": "ok", "output": self.preferences.get(key)}

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "output": "ok"}
