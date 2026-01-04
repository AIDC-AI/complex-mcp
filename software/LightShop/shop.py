from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from collections import defaultdict
import random
import yaml

import sys
from pathlib import Path

WORK_DIR = Path('.').__str__()
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)

from software.utils.time import TimeMachine
from software.utils.dist import lev_sim

@dataclass
class Item:
    tid: str
    name: str
    price: float
    star: bool = field(default=False)

@dataclass
class Shop:
    sid: str
    name: str
    category: str
    items: Dict[str, Item] = field(default_factory=dict)
    count: Dict[str, int] = field(default_factory=dict)
    star: bool = field(default=False)

@dataclass
class CartItem:
    caid: str
    sid: str
    tid: str
    count: int

@dataclass
class Transaction:
    timestamp: str
    trid: str
    total: float
    info: Dict[str, Dict[str, int]] = field(default_factory=dict) # {sid: {cid: cnt}}

from software.utils.core import OSConnector, DummyOSConnector

class ShopSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.rng = random.Random(seed)
        self.time_machine = TimeMachine(rng=self.rng)
        self.os = OSConnector(
            session_id=os_cfg["session_id"],
            url=os_cfg["url"]
        ) if os_cfg else DummyOSConnector()
        self.shops = self.init_shops()

        self.my_balance = self.rng.randint(8000, 100000)
        self.cart: List[CartItem] = []
        self.trans_history: List[Transaction] = []
        self.__mock_cart()

        self.my_starred_shops = set()
        self.my_starred_items = set()

        self.enter_password = False

    def get_session_dict(self):
        shops = {sid: asdict(shop) for sid, shop in self.shops.items()}
        cart = sorted([asdict(item) for item in self.cart], key=lambda x: x["caid"])
        trans_history = [asdict(trans) for trans in self.trans_history]

        return {
            "shops": shops,
            "cart": cart,
            "trans_history": trans_history
        }

    def init_shops(self):
        mock_shops_path = Path("software") / "LightShop" / "corpus" / "shop.yaml"
        shops: Dict[str, Shop] = {}
        with open(mock_shops_path) as f:
            mock_shops = yaml.safe_load(f)
        for shop_cfg in mock_shops["shops"]:
            cnt_of_cate: int = self.rng.randint(0, 3)
            category: str = shop_cfg["category"]
            shop_names: List[str] = shop_cfg["shop_names"]
            items: List[str] = shop_cfg["items"]
            
            sel_shop_names = self.rng.sample(shop_names, k=cnt_of_cate)
            for sel_shop_name in sel_shop_names:
                sel_items = self.rng.sample(items, k=self.rng.randint(5, len(items)))
                sel_items_dict = {}
                sel_items_count = {}
                for sel_item in sel_items:
                    item_name, price = sel_item.split("=")
                    item_name = item_name.strip()
                    price = float(price.strip()) * self.rng.uniform(0.6, 1.2)
                    price = int(100 * price) / 100
                    item = Item(
                        tid=f"item_{self.uuid()}",
                        name=item_name,
                        price=price
                    )
                    sel_items_dict[item.tid] = item
                    sel_items_count[item.tid] = self.rng.randint(0, 100)
                shop = Shop(
                    sid=f"shop_{self.uuid()}",
                    name=sel_shop_name,
                    category=category,
                    items=sel_items_dict,
                    count=sel_items_count
                )
                shops[shop.sid] = shop
        
        return shops
    
    def __mock_cart(self):
        if self.rng.uniform(0, 1) < 0.4:
            return
        shop: Shop = self.rng.choice(list(self.shops.values()))
        items: List[Item] = self.rng.sample(list(shop.items.values()), k=self.rng.randint(1, 5))
        for item in items:
            self.add_to_cart(shop.sid, item.tid, cnt=1)
    
    def uuid(self):
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(self.rng.choices(alphabet, k=22))
    
    def list_all_shop_categories(self):
        shop_category = set()
        for shop in self.shops.values():
            shop_category.add(shop.category)
        
        return {
            "status": "ok",
            "output": sorted(list(shop_category))
        }
    
    def list_all_shops_by_category(self, category: str):
        shops_list = []
        for shop in self.shops.values():
            if shop.category == category:
                shops_list.append(shop.name)
        
        return {
            "status": "ok",
            "output": sorted(shops_list)
        }
    
    def __get_shop(self, sid: str):
        shop = self.shops.get(sid)
        if shop:
            return shop, None
        return None, {
            "status": "failed",
            "output": f"Shop with ID {sid} not found."
        }
    
    def get_shop_id_by_name(self, name: str):
        for shop in self.shops.values():
            if shop.name == name:
                return {
                    "status": "ok",
                    "output": shop.sid
                }
        return {
            "status": "failed",
            "output": f"Shop named {name} not found."
        }
    
    def list_items(self, sid: str):
        shop, err = self.__get_shop(sid)
        if err: return err
        items_list = [asdict(item) for item in shop.items.values()]

        return {
            "status": "ok",
            "output": sorted(items_list, key=lambda x: x.get("name", ""))
        }
    
    def add_to_cart(self, sid: str, tid: str, cnt: int):
        shop, err = self.__get_shop(sid)
        if err: return err

        item = shop.items.get(tid)
        if item is None:
            return {
                "status": "failed",
                "output": f"Item with ID {tid} not found in shop '{shop.name}' (ID: {shop.sid})."
            }

        if shop.count[tid] < cnt:
            return {
                "status": "failed",
                "output": f"Shop '{shop.name}' (ID: {shop.sid}) has {shop.count[tid]} of '{item.name}' (ID: {tid}), which is less than the requested {cnt}."
            }

        shop.count[tid] -= cnt
        self.cart.append(
            CartItem(
                caid=f"cart_{self.uuid()}",
                sid=sid,
                tid=tid,
                count=cnt
            )
        )

        return {
            "status": "ok",
            "output": f"Added {cnt} × '{item.name}' (ID: {tid}) to your cart."
        }

    def delete_item_in_cart(self, caid: str):
        for i, cart_item in enumerate(self.cart):
            if cart_item.caid == caid:
                shop = self.shops[cart_item.sid]
                shop.count[cart_item.tid] += cart_item.count
                self.cart.pop(i)
                return {
                    "status": "ok",
                    "output": f"Removed item (ID: {caid}) from your cart."
                }
        
        return {
            "status": "failed",
            "output": f"Item with ID {caid} not found in your cart."
        }
    
    def get_item_info(self, sid: str, tid: str):
        shop, err = self.__get_shop(sid)
        if err: return err

        item = shop.items.get(tid)
        if item is None:
            return {
                "status": "failed",
                "output": f"Item with ID {tid} not found in shop '{shop.name}' (ID: {sid})"
            }
        
        return {
            "status": "ok",
            "output": {
                "name": item.name,
                "price": item.price,
                "count": shop.count[tid]
            }
        }
    
    def check_balance(self):
        return {
            "status": "ok",
            "output": self.my_balance
        }

    def checkout_all(self):
        if not self.enter_password:
            return {
                "status": "failed",
                "output": "This operation requires the user to enter their payment password first."
            }
        self.enter_password = False

        if len(self.cart) == 0:
            return {
                "status": "failed",
                "output": "Your cart is empty."
            }

        total_price = 0
        info = defaultdict(dict)

        for cart_item in self.cart:
            sid = cart_item.sid
            tid = cart_item.tid
            count = cart_item.count

            info[sid][tid] = count

            shop = self.shops[sid]
            item = shop.items[tid]

            total_price += item.price * count
        
        if total_price > self.my_balance:
            return {
                "status": "failed",
                "output": "Insufficient balance."
            }

        self.my_balance -= total_price
        trans = Transaction(
            timestamp=self.os.step(),
            trid=f"trans_{self.uuid()}",
            total=total_price,
            info=dict(info)
        )

        self.trans_history.append(trans)
        self.cart.clear()

        return {
            "status": "ok",
            "output": f"Checkout successful. Transaction ID: {trans.trid}."
        }
    
    def get_trans_history(self):

        return {
            "status": "ok",
            "output": [asdict(trans) for trans in self.trans_history]
        }
    
    def get_cart_summary(self):
        summary = []
        for cart_item in self.cart:
            summary.append(asdict(cart_item))

        return {
            "status": "ok",
            "output": summary
        }
    
    def search_shops(self, shop_name: str):
        results = []
        for shop in self.shops.values():
            if shop_name.lower() in shop.name.lower():
                results.append(f"{shop.name} ({shop.sid})")
        
        return {
            "status": "ok",
            "results": results
        }
    
    def fuzzy_search_shops(self, shop_name: str):
        results = []
        shop_name = shop_name.lower()
        for shop in self.shops.values():
            _shop_name = shop.name.lower()
            if shop_name in _shop_name or lev_sim(_shop_name, shop_name) > 0.6:
                results.append(f"{shop.name} ({shop.sid})")
        
        return {
            "status": "ok",
            "output": results
        }

    def search_items(self, item_name: str):
        results = []
        item_name = item_name.lower()

        for shop in self.shops.values():
            for item in shop.items.values():
                if item_name in item.name.lower():
                    results.append(
                        {
                            "tid": item.tid,
                            "name": item.name,
                            "price": item.price,
                            "shop": shop.name
                        }
                    )
        
        return {
            "status": "ok",
            "output": results
        }

    def fuzzy_search_items(self, item_name: str):
        results = []
        item_name = item_name.lower()

        for shop in self.shops.values():
            for item in shop.items.values():
                if item_name in item.name.lower() or lev_sim(item_name, item.name.lower()) > 0.6:
                    results.append(
                        {
                            "tid": item.tid,
                            "name": item.name,
                            "price": item.price,
                            "shop": shop.name
                        }
                    )
        
        return {
            "status": "ok",
            "output": results
        }
    
    def search_items_in_shop(self, sid: str, item_name: str):
        results = []
        shop, err = self.__get_shop(sid)
        if err: return err

        item_name = item_name.lower()
        for item in shop.items.values():
            if item_name in item.name.lower():
                results.append(
                    {
                        "tid": item.tid,
                        "name": item.name,
                        "price": item.price
                    }
                )
        
        return {
            "status": "ok",
            "output": results
        }
    
    def fuzzy_search_items_in_shop(self, sid: str, item_name: str):
        results = []
        shop, err = self.__get_shop(sid)
        if err: return err

        item_name = item_name.lower()
        for item in shop.items.values():
            if item_name in item.name.lower() or lev_sim(item_name, item.name.lower()) > 0.6:
                results.append(
                    {
                        "tid": item.tid,
                        "name": item.name,
                        "price": item.price
                    }
                )
        
        return {
            "status": "ok",
            "output": results
        }
    
    def get_trans_info(self, trid: str):
        for trans in self.trans_history:
            if trans.trid == trid:
                return {
                    "status": "ok",
                    "output": asdict(trans)
                }
        

        return {
            "status": "failed",
            "output": f"Transaction with ID ({trid}) not found"
        }
    
    def delete_trans_history(self, trid: str):
        for i, trans in enumerate(self.trans_history):
            if trans.trid == trid:
                self.trans_history.pop(i)
                return {
                    "status": "ok",
                    "output": f"You have successfully deleted one transaction history (TRID={trid})"
                }
        
        return {
            "status": "failed",
            "output": f"Transaction history with TRID={trid} not found"
        }

    def star_shop(self, sid: str):
        shop, err = self.__get_shop(sid)
        if err: return err

        if shop.star:
            return {
                "status": "failed",
                "output": f"You have already starred the shop {shop.name} ({shop.sid})"
            }
        shop.star = True
        self.my_starred_shops.add(shop.sid)

        return {
            "status": "ok",
            "output": f"You have successfully starred the shop {shop.name} ({shop.sid})"
        }

    def unstar_shop(self, sid: str):
        shop, err = self.__get_shop(sid)
        if err: return err

        if not shop.star:
            return {
                "status": "failed",
                "output": f"The shop {shop.name} ({shop.sid}) is not starred."
            }
        shop.star = False
        self.my_starred_shops.discard(shop.sid)

        return {
            "status": "ok",
            "output": f"You have successfully unstarred the shop {shop.name} ({shop.sid})"
        }

    def star_item(self, sid: str, tid: str):
        shop, err = self.__get_shop(sid)
        if err: return err

        item = shop.items.get(tid)
        if item is None:
            return {
                "status": "failed",
                "output": f"Item with ID {tid} not found in shop '{shop.name}' (ID: {shop.sid})."
            }

        if item.star:
            return {
                "status": "failed",
                "output": f"You have already starred the item '{item.name}' (ID: {tid}) in shop '{shop.name}' (ID: {shop.sid})."
            }
        item.star = True
        self.my_starred_items.add((sid, tid))

        return {
            "status": "ok",
            "output": f"You have successfully starred the item '{item.name}' (ID: {tid}) in shop '{shop.name}' (ID: {shop.sid})."
        }

    def unstar_item(self, sid: str, tid: str):
        shop, err = self.__get_shop(sid)
        if err: return err

        item = shop.items.get(tid)
        if item is None:
            return {
                "status": "failed",
                "output": f"Item with ID {tid} not found in shop '{shop.name}' (ID: {shop.sid})."
            }

        if not item.star:
            return {
                "status": "failed",
                "output": f"The item '{item.name}' (ID: {tid}) in shop '{shop.name}' (ID: {shop.sid}) is not starred."
            }
        item.star = False
        self.my_starred_items.discard((sid, tid))

        return {
            "status": "ok",
            "output": f"You have successfully unstarred the item '{item.name}' (ID: {tid}) in shop '{shop.name}' (ID: {shop.sid})."
        }
    
    def get_my_starred_shops(self):
        starred_shops = []
        for sid in self.my_starred_shops:
            shop = self.shops[sid]
            assert shop # TODO: delete
            starred_shops.append(
                {
                    "sid": shop.sid,
                    "shop_name": shop.name,
                    "category": shop.category,
                }
            )
        return {
            "status": "ok",
            "output": starred_shops
        }

    def get_my_starred_items(self):
        starred_items = []
        for sid, tid in self.my_starred_items:
            shop = self.shops[sid]
            assert shop # TODO: delete
            item = shop.items[tid]
            assert item # TODO: delete
            starred_items.append(
                {
                    "sid": sid,
                    "tid": tid,
                    "item_name": item.name,
                    "price": item.price
                }
            )

        return {
            "status": "ok",
            "output": starred_items
        }
    
    def wait_payment_password(self):
        if self.rng.uniform(0, 1) < 0.1:
            return {
                "status": "internal error",
                "output": "Incorrect password, please try again."
            }
        self.enter_password = True
        return {
            "status": "ok",
            "output": "The user has entered the correct payment password."
        }


if __name__ == "__main__":
    shop_session = ShopSession(seed=42, os_cfg=None)

    from pprint import pprint

    pprint(shop_session.get_session_dict())
