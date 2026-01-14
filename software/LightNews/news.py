from typing import Dict, List
from pathlib import Path
import random
import sys
import yaml
from dataclasses import dataclass, asdict
from datetime import datetime

WORK_DIR = Path('.').__str__()
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR)

from software.utils.core import OSConnector, DummyOSConnector

@dataclass
class NewsItem:
    nid: str
    timestamp: str
    title: str
    abstract: str
    content: str

CORPUS_PATH = Path("software") / "LightNews" / "corpus"

class NewsSession:
    def __init__(self, seed: int, os_cfg: Dict[str, str] = None):
        self.rng = random.Random(seed)
        self.os = OSConnector(
            session_id=os_cfg["session_id"],
            url=os_cfg["url"]
        ) if os_cfg else DummyOSConnector()
        self.sections = [
            "Town Updates",
            "School & Kids",
            "Events & Happenings",
            "Local Business",
            "Public Safety",
            "Sports"
        ]
        self._news, self._news_dict = self._initialize_news()

    def get_session_dict(self):
        return {}

    def uuid(self):
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(self.rng.choices(alphabet, k=22))

    def _initialize_news(self):
        files = {
            "Town Updates": "town-updates.yaml",
            "School & Kids": "school-kids.yaml",
            "Events & Happenings": "events-happenings.yaml",
            "Local Business": "local-business.yaml",
            "Public Safety": "public-safety.yaml",
            "Sports": "sports.yaml"
        }
        news: Dict[str, List[NewsItem]] = {}
        news_dict: Dict[str, NewsItem] = {}
        for section, file in files.items():
            with open(CORPUS_PATH / file) as f:
                news_list = yaml.safe_load(f)
                news_cnt = self.rng.randint(40, 60)
                sel_news_list = self.rng.sample(news_list, k=news_cnt)
                timestamps = self.os.gen_past(start_year=2025, k=news_cnt)
                news_item_list = []

                for timestamp, news_info in zip(timestamps, sel_news_list):
                    news_item = NewsItem(
                        nid=f"news_{self.uuid()}",
                        timestamp=timestamp,
                        title=news_info["title"],
                        abstract=news_info["abstract"],
                        content=news_info["content"]
                    )
                    news_item_list.append(news_item)
                    news_dict[news_item.nid] = news_item
                news[section] = news_item_list
        
        return news, news_dict

    def list_all_sections(self):
        return {
            "status": "ok",
            "output": self.sections
        }
    
    def get_details(self, nid: str):
        if nid not in self._news_dict:
            return {
                "status": "failed",
                "output": f"News with ID={nid} not found"
            }
        return {
            "status": "ok",
            "output": asdict(self._news_dict[nid])
        }
    
    def get_last_k_news(self, section: str, k: int):
        if section not in self.sections:
            return {
                "status": "failed",
                "output": f"Section '{section}' not found"
            }
        
        return {
            "status": "ok",
            "output": [{"nid": news_item.nid, "title": news_item.title, "timestamp": news_item.timestamp, "abstract": news_item.abstract} for news_item in self._news[section][-k:]]
        }
    
    def search(self, section: str, query: str, maxn: int = 10, begin_date: str = None, end_date: str = None):
        if section not in self.sections:
            return {
                "status": "failed",
                "output": f"Section '{section}' not found"
            }
        _sec_news = self._news[section]
        begin_date = datetime.fromisoformat(begin_date) if begin_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
        results = []
        query = query.lower()
        for news_item in _sec_news[-1::-1]:
            _timestamp = datetime.fromisoformat(news_item.timestamp)
            if begin_date and _timestamp < begin_date:
                continue
            if end_date and _timestamp > end_date:
                continue
            if query in news_item.title.lower() or query in news_item.abstract.lower():
                results.append({
                    "nid": news_item.nid,
                    "timestamp": news_item.timestamp,
                    "title": news_item.title,
                    "abstract": news_item.abstract
                })
                if len(results) >= maxn:
                    break
        
        return {
            "status": "ok",
            "output": results
        }

    def get_news_url(self, nid: str):
        return {
            "status": "ok",
            "output": f"light://news?nid={nid}"
        }

if __name__ == "__main__":
    news_session = NewsSession(seed=42)
    
    from pprint import pprint
    # print(news_session.get_last_k_news(section="Sports", k=3))
