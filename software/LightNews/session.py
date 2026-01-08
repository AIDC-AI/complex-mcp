from shortuuid import uuid
from typing import Dict
from news import NewsSession

class LightNewsSession:
    def __init__(
        self,
        seed: int,
        os_cfg: Dict[str, str]
    ):
        self.session_id = f"session_{uuid()}"
        self.news_session = NewsSession(
            seed=seed,
            os_cfg=os_cfg
        )

    
    