from shortuuid import uuid
from typing import Dict

from stock import StockSession


class LightStockSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.session_id = f"session_{uuid()}"
        self.stock_session = StockSession(seed=seed, os_cfg=os_cfg)
