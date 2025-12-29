from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from collections import defaultdict
import random
import yaml

from pathlib import Path

@dataclass
class Item:
    tid: str
    name: str
    price: float

@dataclass
class Shop:
    sid: str
    name: str
    category: str
    items: Dict[str, Item] = field(default_factory=dict)
    count: Dict[str, int] = field(default_factory=dict)

@dataclass
class CartItem:
    caid: str
    sid: str
    tid: str
    count: int

@dataclass
class Transaction:
    trid: str
    total: float
    info: Dict[str, Dict[str, int]] = field(default_factory=dict) # {sid: {cid: cnt}}


class ShopSession:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.shops = self.init_shops()

        self.my_balance = self.rng.randint(8000, 100000)
        self.cart: List[CartItem] = []
        self.trans_history: List[Transaction] = []

    def get_session_dict(self):
        shops = {sid: asdict(shop) for sid, shop in self.shops.items()}
        cart = [asdict(item) for item in self.cart]
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
    
    def get_shop(self, sid: str):
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
        shop, err = self.get_shop(sid)
        if err: return err
        items_list = [asdict(item) for item in shop.items.values()]

        return {
            "status": "ok",
            "output": sorted(items_list, key=lambda x: x.get("name", ""))
        }
    
    def add_to_cart(self, sid: str, tid: str, cnt: int):
        shop, err = self.get_shop(sid)
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
                shop.items[cart_item.tid] += cart_item.count
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
        shop, err = self.get_shop(sid)
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


if __name__ == "__main__":
    shop_session = ShopSession(seed=42)

    from pprint import pprint

    pprint(shop_session.get_session_dict())