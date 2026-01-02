from shortuuid import uuid
from typing import Dict

from flight import FlightSession


class LightFlightSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.session_id = f"session_{uuid()}"
        self.flight_session = FlightSession(seed=seed, os_cfg=os_cfg)
