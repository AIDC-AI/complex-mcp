from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import random
import yaml
import math

import sys
from pathlib import Path

WORK_DIR = Path('.').__str__()
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)

from software.utils.time import TimeMachine
from software.utils.core import OSConnector, DummyOSConnector, uuid_rng

@dataclass
class Flight:
    fid: str
    departure: str
    arrival: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: int  # 分钟
    price: float
    seat_count: Dict[str, int] = field(default_factory=dict)  # 舱等: 剩余座位数

@dataclass
class Airport:
    aid: str
    name: str
    city: str
    code: str
    _coord: Tuple[int, int]
    star: bool = field(default=False)

@dataclass
class BookingItem:
    bid: str
    fid: str
    seat_class: str
    passenger_count: int
    total_price: float

@dataclass
class BookingRecord:
    timestamp: str
    brid: str
    total: float
    flights: Dict[str, Dict[str, int]] = field(default_factory=dict)  # {fid: {seat_class: passenger_count}}


CORPUS_PATH = Path("software") / "LightFlight" / "corpus"

class FlightSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.rng = random.Random(seed)
        self.time_machine = TimeMachine(rng=self.rng)
        self.os = OSConnector(
            session_id=os_cfg["session_id"],
            url=os_cfg["url"]
        ) if os_cfg else DummyOSConnector()

        self.airports, self.airports_in_cities = self.init_airports()
        self.flights, self.flights_by_arrival, self.flights_by_departure = self.init_flights()

        self.my_balance = self.rng.randint(5000, 50000)
        self.bookings_wait_for_checkout: List[BookingItem] = []
        self.current_bookings: List[BookingItem] = []
        self.booking_history: List[BookingRecord] = []
        self.__mock_booking()

        self.my_starred_flights = set()
        self.my_starred_airports = set()

        self.enter_password = False
    
    def uuid(self, prefix: str):
        return f"{prefix}_{uuid_rng(self.rng)}"

    def get_session_dict(self) -> Dict[str, Any]:
        return {
            "my_balance": self.my_balance,
            "bookings": self.current_bookings,
            "history": self.booking_history
        }

    def init_airports(self) -> Tuple[List[Airport], Dict[str, str]]:
        airports_list = []
        airports_in_cities = defaultdict(list)
        with open(CORPUS_PATH / "airports.yaml") as f:
            airports = yaml.safe_load(f)["airports"]
            for airport in airports:
                aid = airport["aid"]
                name = airport["name"]
                city = airport["city"]
                code = airport["code"]
                _coord = airport["_coord"]

                airport_item = Airport(
                    aid=aid,
                    name=name,
                    city=city,
                    code=code,
                    _coord=_coord
                )
                airports_list.append(airport_item)
                airports_in_cities[city].append(name)
        
        return airports_list, airports_in_cities

    def init_flights(self) -> Tuple[Dict[str, Flight], Dict[str, List[Flight]], Dict[str, List[Flight]]]:
        def __mock_dura_price(
            coord_1: Tuple[float, float],
            coord_2: Tuple[float, float]
        ) -> Tuple[int, float]:
            lat1, lon1 = coord_1
            lat2, lon2 = coord_2
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            distance_km = 111 * math.sqrt(dlat**2 + (math.cos(math.radians(lat1)) * dlon)**2)
            
            flight_hours = distance_km / 800
            total_minutes = int(round(flight_hours * 60 + 45))  # 飞行时间+起降
            
            total_minutes = int(total_minutes * self.rng.uniform(0.9, 1.1))
            total_minutes = max(60, total_minutes)
            
            price_per_km = self.rng.uniform(0.8, 1.2)  # 每公里 0.8-1.2 元
            price = distance_km * price_per_km
            
            # 简单调节
            if total_minutes < 120:  # 短途
                price *= 1.5
            elif total_minutes > 360:  # 长途
                price *= 0.9
            
            # 随机波动
            price *= self.rng.uniform(0.3, 1.2)
            
            price = max(300, min(10000, price))
            price = round(price / 10) * 10
            
            return total_minutes, price

        flights: Dict[str, Flight] = {}
        flights_by_arrival: Dict[str, List[Flight]] = defaultdict(list)
        flights_by_departure: Dict[str, List[Flight]] = defaultdict(list)
        for airport in self.airports:
            target_airports = self.rng.sample(self.airports, k=self.rng.randint(5, 50))
            target_airports = self.rng.choices(target_airports, k=4 * len(target_airports))
            for target_airport in target_airports:
                dura, price = __mock_dura_price(airport._coord, target_airport._coord)
                departure_time = self.time_machine.add_secs(
                    timestamp=self.os.now(),
                    min_secs=3600 * 4, max_secs= 3600 * 10 * 24
                )
                flight = Flight(
                    fid=self.uuid("flight"),
                    departure=airport.city,
                    arrival=target_airport.city,
                    departure_airport=airport.name,
                    arrival_airport=target_airport.name,
                    departure_time=departure_time,
                    arrival_time=self.time_machine.add_secs(
                        departure_time,
                        min_secs=dura * 60, max_secs=dura * 60
                    ),
                    duration=dura,
                    price=price, # economy
                    seat_count={
                        "economy": self.rng.randint(10, 50),
                        "business": self.rng.randint(0, 20),
                        "first": self.rng.randint(0, 7)
                    }
                )
                flights[flight.fid] = flight
                flights_by_arrival[flight.arrival].append(flight)
                flights_by_departure[flight.departure].append(flight)
        
        return flights, dict(flights_by_arrival), dict(flights_by_departure)

    def __mock_booking(self):
        if self.rng.uniform(0, 1) > 0.5:
            return
        
    def list_all_cities(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "output": list(self.airports_in_cities.keys())
        }

    def list_airports_by_city(self, city: str) -> Dict[str, Any]:
        if city not in self.airports_in_cities:
            return {
                "status": "failed",
                "output": f"City '{city}' not found"
            }
        return {
            "status": "ok",
            "output": self.airports_in_cities[city]
        }

    def __get_flight(self, fid: str) -> Tuple[Optional[Flight], Optional[Dict]]:
        if fid not in self.flights:
            return None, {
                "status": "failed",
                "output": f"Flight ID with {fid} not found"
            }
        
        return self.flights[fid], None

    def get_flight_details(self, fid: str) -> Dict[str, Any]:
        flight, err = self.__get_flight(fid)
        if err: return err

        flight_info = {
            "fid": flight.fid,
            "departure": f"{flight.departure}, {flight.departure_airport}",
            "arrival": f"{flight.arrival}, {flight.arrival_airport}",
            "depature_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "duration": f"{flight.duration} min",
            "price": {
                "ecomony": flight.price,
                "business": flight.price * 2,
                "first": flight.price * 4.5
            },
            "seat_count": flight.seat_count
        }

        return {
            "status": "ok",
            "output": flight_info
        }

    def search_flights(self, departure: str, arrival: str, date: str) -> Dict[str, Any]:
        # parse input date (accept "YYYY-MM-DD" or full timestamp)
        try:
            if len(date.strip()) == 10:
                target_date = datetime.strptime(date.strip(), "%Y-%m-%d").date()
            else:
                target_date = datetime.strptime(date.strip(), "%Y-%m-%d %H:%M:%S").date()
        except Exception:
            return {
                "status": "failed",
                "output": f"Invalid date format: {date}. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'"
            }

        matched = []
        for flight in self.flights_by_departure.get(departure, []):
            try:
                dep_time = datetime.strptime(flight.departure_time, "%Y-%m-%d %H:%M:%S")
            except Exception:
                # skip malformed timestamps
                continue

            if dep_time.date() != target_date:
                continue

            if flight.arrival == arrival:
                matched.append(flight.fid)

        if not matched:
            return {
                "status": "failed",
                "output": f"No flights found for {departure} -> {arrival} on {date}"
            }

        return {
            "status": "ok",
            "output": matched
        }

    def check_seat_availability(self, fid: str, seat_class: str) -> Dict[str, Any]:
        flight, err = self.__get_flight(fid)
        if err: return err

        if seat_class not in flight.seat_count:
            return {
                "status": "failed",
                "output": f"Seat class `{seat_class}` not found"
            }
        
        return {
            "status": "ok",
            "output": f"remain {flight.seat_count[seat_class]}"
        }

    def add_to_booking(self, fid: str, seat_class: str, passenger_count: int) -> Dict[str, Any]:
        pass

    def remove_from_booking(self, bid: str) -> Dict[str, Any]:
        pass

    def get_booking_summary(self) -> Dict[str, Any]:
        pass

    def check_balance(self) -> Dict[str, Any]:
        pass

    def checkout_booking(self) -> Dict[str, Any]:
        pass

    def get_booking_history(self) -> Dict[str, Any]:
        pass

    def get_booking_details(self, brid: str) -> Dict[str, Any]:
        pass

    def cancel_booking(self, brid: str) -> Dict[str, Any]:
        pass

    def search_airports(self, airport_name: str) -> Dict[str, Any]:
        pass

    def fuzzy_search_airports(self, airport_name: str) -> Dict[str, Any]:
        pass

    def star_airport(self, aid: str) -> Dict[str, Any]:
        pass

    def unstar_airport(self, aid: str) -> Dict[str, Any]:
        pass

    def get_my_starred_airports(self) -> Dict[str, Any]:
        pass

    def wait_payment_password(self) -> Dict[str, Any]:
        pass

    def get_recommended_flights(self) -> Dict[str, Any]:
        pass

    def filter_flights_by_price_range(self, min_price: float, max_price: float) -> Dict[str, Any]:
        pass

    def filter_flights_by_duration(self, max_duration: int) -> Dict[str, Any]:
        pass

if __name__ == "__main__":
    flight_session = FlightSession(seed=1, os_cfg=None)
    from pprint import pprint

    pprint(flight_session.search_flights(
        departure="Dubai",
        arrival="Seattle",
        date="2026-01-02"
    ))

    fid1 = "flight_o4fKmMQTr2CnDMKSwwV5Qh"
    fid2 = "flight_QgtC5UJAHYFZA2oZuiSijw"

    pprint(flight_session.get_flight_details(fid1))
    pprint(flight_session.get_flight_details(fid2))

