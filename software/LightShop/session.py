from shortuuid import uuid

# import sys
# from pathlib import Path

# WORK_DIR = Path(".").__str__()

# if WORK_DIR not in sys.path:
#     sys.path.append(WORK_DIR)

from shop import ShopSession
from typing import Dict

class LightShopSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.session_id = f"session_{uuid()}"
        self.shop_session = ShopSession(seed=seed, os_cfg=os_cfg)