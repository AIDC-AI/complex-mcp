from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from collections import defaultdict
import random 

@dataclass
class Item:
    tid: str
    name: str
    price: float

@dataclass
class Shop:
    sid: str
    category: str
    description: str
    start_time: str
    items: Dict[str, Item] = field(default_factory=dict)
    count: Dict[str, int] = field(default_factory=dict)
    discount: Dict[str, float] = field(default_factory=dict)

@dataclass
class CartItem:
    sid: str
    tid: str
    count: int

@dataclass
class Transaction:
    trid: str
    timestamp: str
    total: float
    info: Dict[str, Dict[str, int]] = field(default_factory=dict) # {sid: {cid: cnt}}

import yaml
from pathlib import Path

class ShopSession:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def init_shops(self):
        mock_shops_path = Path("software") / "LightShop" / "corpus" / "shop.yaml"
        shops: List[Shop] = []
        with open(mock_shops_path) as f:
            mock_shops = yaml.safe_load(f)
        # TODO
        for shop_cfg in mock_shops["shops"]:
            pass

