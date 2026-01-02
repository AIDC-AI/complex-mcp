from shortuuid import uuid
from typing import Dict

from weather import WeatherSession

class LightWeatherSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.session_id = f"session_{uuid()}"
        self.weather_session = WeatherSession(seed=seed, os_cfg=os_cfg)
