from shortuuid import uuid

from contact import ContactSession


class LightTalkSession:
    def __init__(
        self,
        seed: int
    ):
        self.session_id = f"session_{uuid()}"
        self.contact_session = ContactSession(seed=seed)
    
    
