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
class Comment:
    cid: str
    send_uid: str
    receive_moid: str
    content: str
    timestamp: str
    comments: List['Comment'] = field(default_factory=list)

@dataclass
class Moment:
    moid: str
    owner_uid: str
    content: str
    timestamp: str
    ip: str = field(default="UnKnown")
    img_urls: List[str] = field(default_factory=list)
    who_likes: List[str] = field(default_factory=list)
    comments: List[Comment] = field(default_factory=list)

@dataclass
class Contact:
    name: str
    gender: str
    tag: str
    uid: str
    blocked: bool
    chat_history: List[Message] = field(default_factory=list)
    moments: List[Moment] = field(default_factory=list)
    read_new_message: bool = field(default=False)

from pathlib import Path
import yaml

corpus_path = Path("software") / "LightTalk" / "corpus"

class ContactSession:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        
        self.contacts_dict: Dict[str, Contact] = {}
        self.uid_dict = {}
        self.my_uid = f"user_{self.uuid()}"
        
        with open(corpus_path / "contact.yaml") as f:
            info = yaml.safe_load(f)
        
        with open(corpus_path / "moment.yaml") as f:
            moments = yaml.safe_load(f)["moments"]

        n_contacts = self.rng.randint(5, 100)

        surnames = self.rng.choices(info["surnames"], k=n_contacts + 1)
        tags = self.rng.choices(info["tags"], k=n_contacts)
        genders = self.rng.choices(["male", "female"], k=n_contacts + 1)
        first_names_arr = info["first_names"]
        first_names = [self.rng.choice(first_names_arr[gender]) for gender in genders]

        blockeds = self.rng.choices([False, True], weights=[0.9, 0.1], k=n_contacts)

        self.my_name = f"{first_names[-1]} {surnames[-1]}"
        self.my_gender = genders[-1]
        self.my_moments: List[Moment] = []

        # Generate all contacts
        for first_name, surname, tag, gender, blocked in \
            zip(first_names[:-1], surnames[:-1], tags, genders, blockeds):
            name = f"{first_name} {surname}"
            if name in self.uid_dict:
                continue
            contact = Contact(name=name, tag=tag, uid=f"user_{self.uuid()}", gender=gender, blocked=blocked)
            self.contacts_dict[contact.uid] = contact
            self.uid_dict[name] = contact.uid
        
        self.uids = list(self.contacts_dict.keys())

        # Generate moments of each contact
        for contact in self.contacts_dict.values():
            moment_cnt = self.rng.choices([0, 1, 2, 3, 4, 5], weights=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])[0]
            contact_moments = self.draw_without_replacement(moments, min(moment_cnt, len(moments)))
            for contact_moment in contact_moments:
                moment = Moment(
                    moid=f"mo_{self.uuid()}",
                    owner_uid=contact.uid,
                    content=contact_moment["content"],
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ip=contact_moment["ip"],
                    who_likes=self.rng.sample(
                        population=self.uids,
                        k=self.rng.randint(0, min(10, len(self.uids)))
                    )
                )
                for moment_comment in contact_moment["comments"]:
                    send_uid = self.rng.choice(self.uids)
                    comment = Comment(
                        cid=f"com_{self.uuid()}",
                        send_uid=send_uid,
                        receive_moid=moment.moid,
                        content=moment_comment,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    moment.comments.append(comment)
                contact.moments.append(moment)

    def draw_without_replacement(self, arr: List[Dict[str, Any]], k: int):
        if k > len(arr):
            return arr
        
        results = []
        for _ in range(k):
            index = self.rng.randrange(len(arr))
            results.append(arr.pop(index))
        
        return results
    
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

    def get_contacts(self, page: int = 0) -> List[Dict[str, str]]:
        PAGE_SIZE = 10
        contacts_list = self.get_all_contacts()

        page = min(len(contacts_list) // PAGE_SIZE, page)

        return contacts_list[PAGE_SIZE * page : PAGE_SIZE * (page + 1)]

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
        
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }


        self.contacts_dict[uid].chat_history.append(msg)

        if self.rng.random() > 0.8:
            return {
                "status": "failed",
                "output": "It appears there's a network issue, please try again."
            }

        return {
            "status": "ok",
            "output": f"You have successfully sent one message to {contact.name} ({uid})"
        }

    def get_chat_history(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found."
            }
        chat_history = [asdict(message) for message in contact.chat_history]

        return chat_history
    
    def get_myuid(self):
        return self.my_uid
    
    def get_dict(self):
        results = {uid: asdict(contact) for uid, contact in self.contacts_dict.items()}

        return results
    
    def delete_chat_history(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        
        contact.chat_history.clear()

        return {
            "status": "ok",
            "output": f"The chat history with {contact.name} ({uid}) has been successfully deleted"
        }
    
    def delete_message(self, uid: str, mid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        
        chat_history = contact.chat_history

        for i in range(len(chat_history)):
            if chat_history[i].mid == mid:
                chat_history.pop(i)
                return {
                    "status": "ok",
                    "output": f"The message with MID ({mid}) was successfully deleted."
                }
        
        return {
            "status": "failed",
            "output": f"Message with MID ({mid}) with user (UID={uid}) not found."
        }
    
    def unblock(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        
        if not contact.blocked:
            return {
                "status": "failed",
                "output": f"You can't unblock {contact.name} ({uid}), who is not blocked currently"
            }

        contact.blocked = False

        return {
            "status": "ok",
            "output": f"You have successfully unblocked contact {contact.name} ({uid})"
        }
    
    def block(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }

        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You can't block {contact.name} ({uid}), who is already blocked currently"
            }

        contact.blocked = True

        return {
            "status": "ok",
            "output": f"You have successfully blocked contact {contact.name} ({uid})"
        }

    def get_contact_info(self, uid: str):
        if uid == self.my_uid:
            return {
                "status": "ok",
                "output": {
                    "name": f"{self.my_name} (Me)"
                }
            }
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        
        return {
            "status": "ok",
            "output": {
                "name": contact.name,
                "tag": contact.tag,
                "gender": contact.gender,
                "blocked": str(contact.blocked)
            }
        }

    def get_all_moments(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        moments = contact.moments

        return {
            "status": "ok",
            "output": [asdict(moment) for moment in moments]
        }

    def get_last_k_moments(self, uid: str, k: int):
        result = self.get_all_moments(uid)
        if result["status"] != "ok":
            return result
        
        result["output"] = result["output"][-k:]

        return result


    def get_moment(self, uid: str, index: int):
        result = self.get_all_moments(uid)
        if result["status"] != "ok":
            return result
        try:
            result["output"] = result["output"][index]
        except Exception as e:
            result["status"] = "failed"
            result["output"] = e.__str__()
        
        return result

    def like_moment(self, uid: str, moid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }

        for moment in contact.moments:
            moment.who_likes.append(self.my_uid)
            return {
                "status": "ok",
                "output": f"You have successfully liked the moment (MOID={moid}) of contact `{contact.name}` (UID={contact.uid})"
            }

        return {
            "status": "failed",
            "output": f"The moment with MOID={moid} not found of {contact.name} (UID={uid})'s moments"
        }

    def comment_moment(self, uid: str, moid: str, content: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }

        for moment in contact.moments:
            comment = Comment(
                cid=f"com_{self.uuid()}",
                send_uid=self.my_uid,
                receive_moid=moid,
                content=content,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            moment.comments.append(comment)
            return {
                "status": "ok",
                "output": f"You have successfully commented the moment (MOID={moid}) of contact `{contact.name}`(UID={contact.uid})'s moments"
            }

        return {
            "status": "failed",
            "output": f"The moment with MOID={moid} not found of contact `{contact.name}` (UID={uid})'s moments"
        }
    
    def comment_comment(self, uid: str, moid: str, cid: str, comment: str):
        # TODO
        pass


if __name__ == "__main__":
    contact_session = ContactSession(seed=42)

    uid = contact_session.get_uid_from_name(name='Arthur Israel')

    from pprint import pprint

    # pprint(contact_session.get_contact_info(uid=uid))
    # print(contact_session.get_last_k_moments(uid, 1))

    moment = contact_session.get_moment(uid=uid, index=0)['output']
    print(moment)

    moid = moment["moid"]

    contact_session.like_moment(uid, moid)

    print(contact_session.get_moment(uid=uid, index=0)['output'])

    print(contact_session.get_myuid())
