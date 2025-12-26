from shortuuid import uuid

# import sys
# from pathlib import Path

# WORK_DIR = Path(".").__str__()

# if WORK_DIR not in sys.path:
#     sys.path.append(WORK_DIR)

from shop import ShopSession

class LightShopSession:
    def __init__(self, seed: int):
        self.session_id = f"session_{uuid()}"
        self.shop_session = ShopSession(seed=seed)