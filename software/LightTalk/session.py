from shortuuid import uuid

from contact import ContactSession

def xorshift(x: int):
    x = x ^ (x << 13)
    x = x ^ (x >> 17)
    x = x ^ (x << 5)

    return x

class LightTalkSession:
    def __init__(
        self,
        seed: int
    ):
        self.session_id = f"session_{uuid()}"
        contact_seed = seed

        self.contact_session = ContactSession(seed=contact_seed)
    
    
