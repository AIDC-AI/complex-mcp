import random
from typing import Tuple
from datetime import datetime, timedelta

class TimeMachine:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.cur_time = self.gen(years=(2026, 2026))

    def gen(self, years: Tuple[int, int] = (2015, 2025)) -> str:
        year = self.rng.randint(years[0], years[1])
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        year_duration = end_date - start_date
        total_seconds = int(year_duration.total_seconds())
        
        random_seconds = self.rng.randint(0, total_seconds - 1)
        random_timestamp = start_date + timedelta(seconds=random_seconds)
        
        return random_timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def add_secs(self, timestamp: str, min_secs: int = 10, max_secs: int = 1000000) -> str:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        
        seconds_to_add = self.rng.randint(min_secs, max_secs)
        
        new_dt = dt + timedelta(seconds=seconds_to_add)

        cur_dt = datetime.strptime(self.cur_time, "%Y-%m-%d %H:%M:%S")
        
        if new_dt > cur_dt:
            self.cur_time = (new_dt + timedelta(seconds=100)).strftime("%Y-%m-%d %H:%M:%S")
        
        return new_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def step(self):
        self.cur_time = self.add_secs(self.cur_time, min_secs=10, max_secs=100)
        return self.cur_time
    
    def now(self):
        return self.cur_time


if __name__ == "__main__":
    time_machine = TimeMachine(random.Random(42))

    print(time_machine.step())
    print(time_machine.step())
    print(time_machine.step())
    print(time_machine.step())
    print(time_machine.step())