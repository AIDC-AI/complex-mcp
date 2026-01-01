from shortuuid import uuid

from clock import ClockSession

class LightSystemSession:
    def __init__(self, seed: int):
        self.session_id = f"session_{uuid()}"
        self.clock_session = ClockSession(seed)

    def get_session_dict(self):
        return {}