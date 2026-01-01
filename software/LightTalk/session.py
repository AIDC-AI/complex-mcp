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
        connector = OSConnector(
            session_id=os_cfg["session_id"],
            url=os_cfg["url"]
        )
        self.contact_session = ContactSession(seed=seed, connector=connector)
    
    
