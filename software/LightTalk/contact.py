from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import random
from datetime import datetime

@dataclass
class Message:
    send_uid: str
    receive_uid: str
    timestamp: str
    content: str
    mid: str


@dataclass
class Contact:
    name: str
    tag: str
    uid: str
    chat_history: List[Message] = field(default_factory=list)

from pathlib import Path
import yaml

corpus_path = Path("software") / "LightTalk" / "corpus"

class ContactSession:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
        self.contacts_dict: Dict[str, Contact] = {}
        self.uid_dict = {}
        self.my_uid = self.uuid()
        
        with open(corpus_path / "contact.yaml") as f:
            info = yaml.safe_load(f)

        n_contacts = self.rng.randint(5, 100)

        first_names = self.rng.choices(info["first_names"], k=n_contacts)
        surnames = self.rng.choices(info["first_names"], k=n_contacts)
        tags = self.rng.choices(info["tags"], k=n_contacts)

        for first_name, surname, tag in zip(first_names, surnames, tags):
            name = f"{first_name} {surname}"
            if name in self.uid_dict:
                continue
            contact = Contact(name=name, tag=tag, uid=f"user_{self.uuid()}")
            self.contacts_dict[contact.uid] = contact
            self.uid_dict[name] = contact.uid
    
    def uuid(self):
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(self.rng.choices(alphabet, k=22))
    
    def get_all_contacts(self) -> List[Dict[str, str]]:
        contacts_list = []
        for contact in self.contacts_dict.values():
            contacts_list.append({
                "uid": contact.uid,
                "name": contact.name,
                "tag": contact.tag
            })
        
        return contacts_list

    def get_uid_from_name(
        self,
        name: str
    ) -> str:
        return self.uid_dict.get(name, f"Contact {name} not found")

    def send_message(
        self,
        uid: str,
        content: str
    ) -> Dict[str, str]:
        msg = Message(
            send_uid=self.my_uid,
            receive_uid=uid,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content=content,
            mid=f"msg_{self.uuid()}"
        )

        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found."
            }


        self.contacts_dict[uid].chat_history.append(msg)

        return {
            "status": "ok"
        }

    def get_chat_history(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found."
            }
        chat_history = asdict(contact.chat_history)

        return chat_history
    
    def get_myuid(self):
        return self.my_uid
    
    def get_dict(self):
        results = {uid: asdict(contact) for uid, contact in self.contacts_dict.items()}

        return results


if __name__ == "__main__":
    pass
