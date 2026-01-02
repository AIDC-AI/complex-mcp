import random
from typing import Dict, List, Any, Tuple
from pathlib import Path
import yaml

import sys
from pathlib import Path

WORK_DIR = Path('.').__str__()
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)

from software.utils.core import OSConnector
from software.utils.time import TimeMachine

CORPUS_PATH = Path("software") / "LightWeather" / "corpus"


class WeatherSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str]):
        self.rng = random.Random(seed)
        self.os = OSConnector(
            session_id=os_cfg["session_id"],
            url=os_cfg["url"]
        )
        self.time_machine = TimeMachine(rng=self.rng)

        # Load corpus data
        with open(CORPUS_PATH / "weather.yaml") as f:
            info = yaml.safe_load(f)

        self.conditions = {c["id"]: c for c in info.get("conditions", [])}
        self.advisories = {a["id"]: a for a in info.get("advisories", [])}
        self.cities = {c["name"]: c for c in info.get("cities", [])}
        self.stations = {s["id"]: s for s in info.get("stations", [])}
        self.climate_samples = {c["city"]: c for c in info.get("climate_samples", [])}

        # State
        self.alerts: Dict[str, Dict[str, Any]] = {}
        self.preferences: Dict[str, Any] = {}
        self.session_id = os_cfg.get("session_id", f"sess_{self.uuid()}")

    def uuid(self) -> str:
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(self.rng.choices(alphabet, k=12))

    def _now(self) -> str:
        # Use OSConnector's now (which delegates to the MCP server) to simulate real clock
        return self.os.now()

    def list_cities(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.cities.keys())}

    def get_current_weather(self, location: str) -> Dict[str, Any]:
        now = self._now()
        city = self.cities.get(location)
        if not city:
            return {"status": "failed", "output": f"Location {location} not found"}

        condition = self.rng.choice(list(self.conditions.values()))
        temp = round(self.climate_samples.get(location, {}).get("avg_temp", 15) + self.rng.uniform(-10, 10), 1)
        wind_kph = round(self.rng.uniform(0, 60), 1)
        humidity = round(self.rng.uniform(20, 95), 1)

        return {
            "status": "ok",
            "output": {
                "location": location,
                "timestamp": now,
                "condition": condition,
                "temperature_c": temp,
                "wind_kph": wind_kph,
                "humidity": humidity
            }
        }

    def get_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        city = self.cities.get(location)
        if not city:
            return {"status": "failed", "output": f"Location {location} not found"}

        base_temp = self.climate_samples.get(location, {}).get("avg_temp", 15)
        forecasts = []
        base_time = self._now()
        for d in range(days):
            cond = self.rng.choice(list(self.conditions.values()))
            temp = round(base_temp + self.rng.uniform(-8, 8), 1)
            precip_mm = round(max(0.0, self.rng.gauss(3, 8)), 1)
            forecasts.append({
                "day_offset": d,
                "date": self.time_machine.add_secs(base_time, min_secs=86400 * d, max_secs=86400 * d + 10),
                "condition": cond,
                "temp_c": temp,
                "precip_mm": precip_mm
            })

        return {"status": "ok", "output": forecasts}

    def get_hourly_forecast(self, location: str, hours: int = 12) -> Dict[str, Any]:
        city = self.cities.get(location)
        if not city:
            return {"status": "failed", "output": f"Location {location} not found"}

        base_temp = self.climate_samples.get(location, {}).get("avg_temp", 15)
        hourly = []
        base_time = self._now()
        for h in range(hours):
            cond = self.rng.choice(list(self.conditions.values()))
            temp = round(base_temp + self.rng.uniform(-6, 6), 1)
            precip_prob = round(self.rng.uniform(0, 1), 2)
            hourly.append({"hour_offset": h, "timestamp": self.time_machine.add_secs(base_time, min_secs=3600 * h, max_secs=3600 * h + 10), "condition": cond, "temp_c": temp, "precip_prob": precip_prob})

        return {"status": "ok", "output": hourly}

    def list_stations(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.stations.values())}

    def get_station_info(self, station_id: str) -> Dict[str, Any]:
        st = self.stations.get(station_id)
        if not st:
            return {"status": "failed", "output": f"Station {station_id} not found"}
        # mock coords and status
        return {"status": "ok", "output": {**st, "status": self.rng.choice(["online", "offline", "maintenance"])}}

    def get_station_observation(self, station_id: str) -> Dict[str, Any]:
        st = self.stations.get(station_id)
        if not st:
            return {"status": "failed", "output": f"Station {station_id} not found"}

        obs = {
            "timestamp": self._now(),
            "temperature_c": round(10 + self.rng.uniform(-10, 15), 1),
            "humidity": round(self.rng.uniform(10, 95), 1),
            "wind_kph": round(self.rng.uniform(0, 80), 1),
            "pressure_hpa": round(1000 + self.rng.uniform(-30, 30), 1)
        }
        return {"status": "ok", "output": obs}

    def get_historical_weather(self, location: str, start: str, end: str) -> Dict[str, Any]:
        # start/end are strings; we won't parse precisely — just return random historic samples
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}

        k = self.rng.randint(3, 20)
        records = []
        for _ in range(k):
            records.append({"date": self.time_machine.gen(), "temp_c": round(self.rng.uniform(-10, 35), 1), "condition": self.rng.choice(list(self.conditions.values()))})

        return {"status": "ok", "output": records}

    def get_weather_alerts(self, location: str) -> Dict[str, Any]:
        # return active alerts that match location
        results = [a for a in self.alerts.values() if a.get("location") == location]
        return {"status": "ok", "output": results}

    def create_alert(self, location: str, condition: str, threshold: float) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        aid = f"alert_{self.uuid()}"
        alert = {"id": aid, "location": location, "condition": condition, "threshold": threshold, "created_at": self._now()}
        self.alerts[aid] = alert
        return {"status": "ok", "output": alert}

    def delete_alert(self, alert_id: str) -> Dict[str, Any]:
        if alert_id not in self.alerts:
            return {"status": "failed", "output": f"Alert {alert_id} not found"}
        del self.alerts[alert_id]
        return {"status": "ok", "output": f"Alert {alert_id} deleted"}

    def list_alerts(self) -> Dict[str, Any]:
        return {"status": "ok", "output": list(self.alerts.values())}

    def get_uv_index(self, location: str) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        val = round(self.rng.uniform(0, 11), 1)
        desc = "low" if val < 3 else ("moderate" if val < 6 else ("high" if val < 8 else "very high"))
        return {"status": "ok", "output": {"uv": val, "level": desc}}

    def get_air_quality(self, location: str) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        aqi = int(max(0, min(500, self.rng.gauss(50, 60))))
        category = "Good" if aqi <= 50 else ("Moderate" if aqi <= 100 else ("Unhealthy" if aqi <= 200 else "Very Unhealthy"))
        return {"status": "ok", "output": {"aqi": aqi, "category": category}}

    def get_sun_times(self, location: str, date: str) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        # Mock sunrise/sunset times relative to the provided date
        sunrise = date + " 06:00:00"
        sunset = date + " 18:00:00"
        return {"status": "ok", "output": {"sunrise": sunrise, "sunset": sunset}}

    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        fu = from_unit.lower()
        tu = to_unit.lower()
        if fu == tu:
            return {"status": "ok", "output": value}
        # convert to c then to target
        if fu == "f":
            c = (value - 32) * 5.0 / 9.0
        elif fu == "k":
            c = value - 273.15
        else:
            c = value

        if tu == "f":
            out = c * 9.0 / 5.0 + 32
        elif tu == "k":
            out = c + 273.15
        else:
            out = c

        return {"status": "ok", "output": round(out, 2)}

    def estimate_travel_weather(self, route: List[str]) -> Dict[str, Any]:
        # route is list of city names
        legs = []
        for loc in route:
            if loc not in self.cities:
                legs.append({"location": loc, "status": "unknown"})
                continue
            cw = self.get_current_weather(loc)["output"]
            legs.append({"location": loc, "weather": cw})
        return {"status": "ok", "output": legs}

    def compare_climate(self, location1: str, location2: str) -> Dict[str, Any]:
        c1 = self.climate_samples.get(location1)
        c2 = self.climate_samples.get(location2)
        if not c1 or not c2:
            return {"status": "failed", "output": "One or both locations not found in climate samples"}
        diff = {"temp_diff": c1["avg_temp"] - c2["avg_temp"], "rain_diff_mm": c1["rainfall_mm"] - c2["rainfall_mm"]}
        return {"status": "ok", "output": diff}

    def get_precip_probability(self, location: str, next_hours: int = 6) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        probs = []
        for h in range(next_hours):
            probs.append({"hour_offset": h, "prob": round(self.rng.uniform(0, 1), 2)})
        return {"status": "ok", "output": probs}

    def get_wind_forecast(self, location: str, hours: int = 12) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        winds = []
        for h in range(hours):
            winds.append({"hour_offset": h, "speed_kph": round(self.rng.uniform(0, 100), 1), "gust_kph": round(self.rng.uniform(0, 140), 1)})
        return {"status": "ok", "output": winds}

    def get_climate_summary(self, location: str, year: int = 2024) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        sample = self.climate_samples.get(location, {})
        summary = {"year": year, "avg_temp": sample.get("avg_temp", 15), "annual_rainfall_mm": sample.get("rainfall_mm", 800)}
        return {"status": "ok", "output": summary}

    def set_primary_location(self, location: str) -> Dict[str, Any]:
        if location not in self.cities:
            return {"status": "failed", "output": f"Location {location} not found"}
        self.preferences["primary_location"] = location
        return {"status": "ok", "output": f"Primary location set to {location}"}

    def get_primary_location(self) -> Dict[str, Any]:
        return {"status": "ok", "output": self.preferences.get("primary_location", None)}
