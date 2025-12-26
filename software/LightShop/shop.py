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
            "output": list(shop_category)
        }
    
    def get_shop(self, sid: str):
        shop = self.shops.get(sid)
        if shop:
            return shop, None
        return None, {
            "status": "failed",
            "output": f"Shop with ID ({sid}) not found."
        }
    
    def add_to_cart(self, sid: str, tid: str, cnt: int):
        shop, err = self.get_shop(sid)
        if err: return err

        item = shop.items.get(tid)
        if item is None:
            return {
                "status": "failed",
                "output": f"Item with ID ({tid}) not found in the shop {shop.name} (ID={shop.sid})"
            }

        if shop.count.get(tid, 0) < cnt:
            return {
                "status": "failed",
                "output": f"The number of `{item.name}` (ID={tid}) in the shop {shop.name} (ID={shop.sid}) is {shop.count.get(tid, 0)}, which is less than {cnt}"
            }

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
            "output": f"You have successfully added {cnt}x`{item.name}` (ID={tid}) to the cart."
        }


    def delete_item_in_cart(self, caid: str):
        pass

    def checkout(self):
        pass






if __name__ == "__main__":
    shop_session = ShopSession(seed=42)

    print(shop_session.shops)