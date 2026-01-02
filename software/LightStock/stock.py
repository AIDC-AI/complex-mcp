import random
from typing import Dict, List, Any
from pathlib import Path
import yaml

import sys
from pathlib import Path

WORK_DIR = Path('.').__str__()
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)

from software.utils.core import OSConnector
from software.utils.time import TimeMachine

CORPUS_PATH = Path("software") / "LightStock" / "corpus"


class StockSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.rng = random.Random(seed)
        self.os = OSConnector(session_id=os_cfg["session_id"], url=os_cfg["url"])
        self.time_machine = TimeMachine(rng=self.rng)

        with open(CORPUS_PATH / "stock.yaml") as f:
            info = yaml.safe_load(f)

        self.markets = {m["code"]: m for m in info.get("markets", [])}
        self.companies = {c["symbol"]: c for c in info.get("companies", [])}
        self.news = {n["symbol"]: n for n in info.get("sample_news", [])}
        self.ratings = {r["symbol"]: r for r in info.get("analyst_ratings", [])}
        self.dividends = {d["symbol"]: d for d in info.get("dividends", [])}

        self.portfolio: Dict[str, int] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.watchlist: List[str] = []
        self.cash = round(self.rng.uniform(1000, 100000), 2)
        self.alerts: Dict[str, Dict[str, Any]] = {}

    def uuid(self) -> str:
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(self.rng.choices(alphabet, k=12))

    def get_session_dict(self):
        return {"portfolio": self.portfolio, "orders": self.orders, "watchlist": self.watchlist, "cash": self.cash}

    def list_markets(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.markets.values())}

    def list_companies(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.companies.values())}

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        c = self.companies.get(symbol)
        if not c:
            return {"status": "failed", "output": "Symbol not found"}
        price = round(self.rng.uniform(5, 3500), 2)
        change = round(self.rng.uniform(-5, 5), 2)
        return {"status": "ok", "output": {"symbol": symbol, "price": price, "change": change}}

    def get_historical(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        if symbol not in self.companies:
            return {"status": "failed", "output": "Symbol not found"}
        data = []
        for d in range(days):
            data.append({"date": self.time_machine.gen(), "close": round(self.rng.uniform(5, 3500),2)})
        return {"status": "ok", "output": data}

    def place_order(self, symbol: str, side: str, qty: int, price: float | None = None) -> Dict[str, Any]:
        if symbol not in self.companies:
            return {"status": "failed", "output": "Symbol not found"}
        cost = (price or round(self.rng.uniform(5, 3500),2)) * qty
        if side.lower() == "buy" and cost > self.cash:
            return {"status": "failed", "output": "Insufficient cash"}
        oid = f"order_{self.uuid()}"
        order = {"order_id": oid, "symbol": symbol, "side": side, "qty": qty, "price": price or None, "status": "filled"}
        self.orders[oid] = order
        # Update portfolio and cash
        if side.lower() == "buy":
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) + qty
            self.cash -= cost
        else:
            self.portfolio[symbol] = max(0, self.portfolio.get(symbol, 0) - qty)
            self.cash += cost
        return {"status": "ok", "output": order}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        o = self.orders.get(order_id)
        if not o:
            return {"status": "failed", "output": "Order not found"}
        if o.get("status") != "filled":
            o["status"] = "cancelled"
            return {"status": "ok", "output": o}
        return {"status": "failed", "output": "Cannot cancel filled order"}

    def list_orders(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.orders.values())}

    def get_order(self, order_id: str) -> Dict[str, Any]:
        o = self.orders.get(order_id)
        if not o:
            return {"status": "failed", "output": "Order not found"}
        return {"status": "ok", "output": o}

    def get_portfolio(self) -> Dict[str, Any]:
        total_value = 0
        for s, qty in self.portfolio.items():
            price = round(self.rng.uniform(5, 3500),2)
            total_value += price * qty
        return {"status": "ok", "output": {"positions": self.portfolio, "cash": self.cash, "est_value": round(total_value + self.cash,2)}}

    def deposit_funds(self, amount: float) -> Dict[str, Any]:
        self.cash += amount
        return {"status": "ok", "output": self.cash}

    def withdraw_funds(self, amount: float) -> Dict[str, Any]:
        if amount > self.cash:
            return {"status": "failed", "output": "Insufficient cash"}
        self.cash -= amount
        return {"status": "ok", "output": self.cash}

    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        c = self.companies.get(symbol)
        if not c:
            return {"status": "failed", "output": "Symbol not found"}
        return {"status": "ok", "output": c}

    def search_stocks(self, keyword: str) -> Dict[str, Any]:
        results = [c for c in self.companies.keys() if keyword.upper() in c or keyword.lower() in self.companies[c]["name"].lower()]
        return {"status": "ok", "output": results}

    def get_watchlist(self) -> Dict[str, Any]:
        return {"status": "ok", "output": self.watchlist}

    def add_watch(self, symbol: str) -> Dict[str, Any]:
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
        return {"status": "ok", "output": self.watchlist}

    def remove_watch(self, symbol: str) -> Dict[str, Any]:
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
        return {"status": "ok", "output": self.watchlist}

    def dividend_history(self, symbol: str) -> Dict[str, Any]:
        d = self.dividends.get(symbol)
        if not d:
            return {"status": "failed", "output": "No dividend data"}
        return {"status": "ok", "output": d}

    def analyst_rating(self, symbol: str) -> Dict[str, Any]:
        r = self.ratings.get(symbol)
        if not r:
            return {"status": "failed", "output": "No rating"}
        return {"status": "ok", "output": r}

    def market_news(self, symbol: str) -> Dict[str, Any]:
        n = self.news.get(symbol, {})
        return {"status": "ok", "output": n.get("headlines", [])}

    def set_alert(self, symbol: str, target_price: float) -> Dict[str, Any]:
        aid = f"alert_{self.uuid()}"
        self.alerts[aid] = {"symbol": symbol, "target": target_price}
        return {"status": "ok", "output": {"alert_id": aid}}

    def list_alerts(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.alerts.values())}

    def delete_alert(self, alert_id: str) -> Dict[str, Any]:
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return {"status": "ok", "output": "deleted"}
        return {"status": "failed", "output": "alert not found"}

    def get_trade_history(self, symbol: str = None) -> Dict[str, Any]:
        history = []
        for o in self.orders.values():
            if symbol and o["symbol"] != symbol:
                continue
            history.append(o)
        return {"status": "ok", "output": history}

    def get_market_status(self) -> Dict[str, Any]:
        return {"status": "ok", "output": {"open": True, "server_time": self.time_machine.gen()}}

    def simulate_trade(self, symbol: str, side: str, qty: int) -> Dict[str, Any]:
        price = round(self.rng.uniform(5,3500),2)
        return {"status": "ok", "output": {"symbol": symbol, "side": side, "qty": qty, "sim_price": price}}

    def get_order_book(self, symbol: str) -> Dict[str, Any]:
        bids = [[round(self.rng.uniform(5,3500),2), self.rng.randint(1,1000)] for _ in range(5)]
        asks = [[round(self.rng.uniform(5,3500),2), self.rng.randint(1,1000)] for _ in range(5)]
        return {"status": "ok", "output": {"bids": bids, "asks": asks}}

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "output": "ok"}
