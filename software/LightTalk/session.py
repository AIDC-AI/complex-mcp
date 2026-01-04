from shortuuid import uuid
from typing import Dict
from contact import ContactSession

from software.utils.core import OSConnector

class LightTalkSession:
    def __init__(
        self,
        seed: int,
        os_cfg: Dict[str, str]
    ):
        self.session_id = f"session_{uuid()}"
        self.contact_session = ContactSession(seed=seed, os_cfg=os_cfg)
    
    
