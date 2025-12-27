from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from collections import defaultdict
import random


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
    ip: str = field(default="Unknown")
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
    read_new_message: bool = field(default=True)

from pathlib import Path
import yaml
import sys

WORK_DIR = Path('.')
if WORK_DIR not in sys.path:
    sys.path.append(WORK_DIR.__str__())

from software.utils.time import TimeMachine

corpus_path = Path("software") / "LightTalk" / "corpus"

class ContactSession:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.time_machine = TimeMachine(self.rng)

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
        self.my_ip = "UnKnown"

        self.has_privilege = False

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
        self.contacts_dict[self.my_uid] = Contact(
            name=self.my_name,
            gender=self.my_gender,
            tag="Me",
            uid=self.my_uid,
            blocked=False
        )

        # Generate moments of each contact
        for contact in self.contacts_dict.values():
            moment_cnt = self.rng.choices([0, 1, 2, 3, 4, 5], weights=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])[0]
            contact_moments = self.draw_without_replacement(moments, min(moment_cnt, len(moments)))
            base_timestamp = self.time_machine.gen()
            for contact_moment in contact_moments:
                moment = Moment(
                    moid=f"mo_{self.uuid()}",
                    owner_uid=contact.uid,
                    content=contact_moment["content"],
                    timestamp=(base_timestamp := self.time_machine.add_secs(base_timestamp, min_secs=600)),
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
                        timestamp=(base_timestamp := self.time_machine.add_secs(base_timestamp, min_secs=60, max_secs=864000))
                    )
                    moment.comments.append(comment)
                contact.moments.append(moment)
    
    @staticmethod
    def require_privilege(func):
        def wrapper(self: 'ContactSession', *args, **kwargs):
            if not self.has_privilege:
                return {
                    "status": "failed",
                    "output": "This operation need privilege"
                }
            return func(self, *args, **kwargs)
        
        return wrapper
    
    @staticmethod
    def network_trouble(prob: float = 0.05):
        def __network_trouble(func):
            def wrapper(self: 'ContactSession', *args, **kwargs):
                if self.rng.uniform(0, 1) < prob:
                    return {
                        "status": "internel error",
                        "output": "It appears there's a network issue, please try again."
                    }
                return func(self, *args, **kwargs)
            return wrapper
        return __network_trouble
    
    def ask_for_privilege(self):
        self.has_privilege = True

        return {
            "status": "ok",
            "output": "You have successfully got the privilege"
        }

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
    
    @network_trouble()
    def get_all_contacts(self) -> List[Dict[str, str]]:
        contacts_list = []
        for contact in self.contacts_dict.values():
            contacts_list.append({
                "uid": contact.uid,
                "name": contact.name,
                "tag": contact.tag
            })
        
        return {
            "status": "ok",
            "output": contacts_list
        }

    def get_contacts(self, page: int = 0) -> List[Dict[str, str]]:
        PAGE_SIZE = 10
        result = self.get_all_contacts()
        if result["status"] != "ok":
            return result
        
        contacts_list = result["output"]
        page = min(len(contacts_list) // PAGE_SIZE, page)

        return contacts_list[PAGE_SIZE * page : PAGE_SIZE * (page + 1)]

    def get_uid_from_name(
        self,
        name: str
    ) -> str:
        uid = self.uid_dict.get(name)
        if uid:
            return {
                "status": "ok",
                "output": uid
            }
        else:
            return {
                "status": "failed",
                "output": f"Contact {name} not found"
            }

    @network_trouble(prob=0.1)
    def send_message(
        self,
        uid: str,
        content: str
    ) -> Dict[str, str]:
        msg = Message(
            send_uid=self.my_uid,
            receive_uid=uid,
            timestamp=self.time_machine.step(),
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

        return {
            "status": "ok",
            "output": f"You have successfully sent one message to {contact.name} ({uid})"
        }

    @network_trouble()
    def get_chat_history(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found."
            }
        chat_history = [asdict(message) for message in contact.chat_history]

        return {
            "status": "ok",
            "output": chat_history
        }
    
    @network_trouble()
    def get_myuid(self):
        return {
            "status": "ok",
            "output": self.my_uid
        }
    
    @network_trouble()
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
    
    @network_trouble()
    @require_privilege
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
    
    @network_trouble()
    @require_privilege
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
    
    @network_trouble()
    @require_privilege
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

    @network_trouble()
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

    @network_trouble()
    def get_all_moments(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }
        moments = contact.moments

        return {
            "status": "ok",
            "output": [asdict(moment) for moment in moments]
        }

    @network_trouble()
    def get_last_k_moments(self, uid: str, k: int):
        result = self.get_all_moments(uid)
        if result["status"] != "ok":
            return result
        
        result["output"] = result["output"][-k:]

        return result

    @network_trouble()
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

    @network_trouble()
    def like_moment(self, uid: str, moid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }

        for moment in contact.moments:
            if moment.moid == moid:
                moment.who_likes.append(self.my_uid)
                return {
                    "status": "ok",
                    "output": f"You have successfully liked the moment (MOID={moid}) of contact `{contact.name}` (UID={contact.uid})"
                }

        return {
            "status": "failed",
            "output": f"The moment with MOID={moid} not found of {contact.name} (UID={uid})'s moments"
        }
    
    @network_trouble()
    def unlike_moment(self, uid: str, moid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }
        
        for moment in contact.moments:
            if moment.moid != moid:
                continue
            for idx, _uid in enumerate(moment.who_likes):
                if _uid == self.my_uid:
                    moment.who_likes.pop(idx)
                    return {
                        "status": "ok",
                        "output": f"You have successfully unliked the moment (MOID={moid}) of contact `{contact.name}` (UID={contact.uid})"
                    }
            return {
                "status": "failed",
                "output": f"You have not liked this moment (MOID={moid}) of contact `{contact.name}` (UID={contact.uid}) before."
            }

        return {
            "status": "failed",
            "output": f"The moment with MOID={moid} not found of {contact.name} (UID={uid})'s moments"
        }

    @network_trouble()
    def comment_moment(self, uid: str, moid: str, content: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }

        for moment in contact.moments:
            comment = Comment(
                cid=f"com_{self.uuid()}",
                send_uid=self.my_uid,
                receive_moid=moid,
                content=content,
                timestamp=self.time_machine.step()
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
    
    @network_trouble()
    def list_all_tags(self):
        tags = defaultdict(int)
        for contact in self.contacts_dict.values():
            tags[contact.tag] += 1
        return {
            "status": "ok",
            "output": [f"{tag} ({cnt})" for tag, cnt in tags.items()]
        }

    @network_trouble()
    def get_contacts_by_tag(self, tag: str):
        matched = []
        for contact in self.contacts_dict.values():
            if contact.tag == tag:
                matched.append({
                    "uid": contact.uid,
                    "name": contact.name,
                    "gender": contact.gender,
                    "tag": contact.tag
                })
        if not matched:
            return {
                "status": "failed",
                "output": f"No contacts found with tag '{tag}'"
            }
        return {
            "status": "ok",
            "output": matched
        }

    @network_trouble()
    def get_contacts_by_gender(self, gender: str):
        if gender not in ("male", "female"):
            return {
                "status": "failed",
                "output": "Gender must be either 'male' or 'female'"
            }
        matched = []
        for contact in self.contacts_dict.values():
            if contact.gender == gender:
                matched.append({
                    "uid": contact.uid,
                    "name": contact.name,
                    "gender": contact.gender,
                    "tag": contact.tag
                })
        if not matched:
            return {
                "status": "failed",
                "output": f"No contacts found with gender '{gender}'"
            }
        return {
            "status": "ok",
            "output": matched
        }

    @network_trouble()
    def comment_comment(self, uid: str, moid: str, cid: str, content: str):
        """在某条评论下回复（嵌套评论）"""
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }

        # 查找对应 moment
        target_moment = None
        for moment in contact.moments:
            if moment.moid == moid:
                target_moment = moment
                break
        if target_moment is None:
            return {
                "status": "failed",
                "output": f"The moment with MOID={moid} not found for contact `{contact.name}` (UID={uid})"
            }

        # 查找父评论
        parent_comment = None
        def find_comment(comments_list):
            for c in comments_list:
                if c.cid == cid:
                    return c
                # 递归查找子评论（虽然当前模型未使用嵌套，但为 future-proof）
                if c.comments:
                    found = find_comment(c.comments)
                    if found:
                        return found
            return None

        parent_comment = find_comment(target_moment.comments)
        if parent_comment is None:
            return {
                "status": "failed",
                "output": f"Comment with CID={cid} not found under moment MOID={moid}"
            }

        # 创建新回复
        new_reply = Comment(
            cid=f"com_{self.uuid()}",
            send_uid=self.my_uid,
            receive_moid=moid,
            content=content,
            timestamp=self.time_machine.step()
        )

        parent_comment.comments.append(new_reply)

        return {
            "status": "ok",
            "output": f"You have successfully replied to comment (CID={cid}) under moment (MOID={moid}) of contact `{contact.name}` (UID={uid})"
        }

    @network_trouble()
    def withdraw_comment_moment(self, uid: str, moid: str, my_cid: str):
        """撤回自己对动态的直接评论（非嵌套）"""
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }

        target_moment = None
        for moment in contact.moments:
            if moment.moid == moid:
                target_moment = moment
                break
        if target_moment is None:
            return {
                "status": "failed",
                "output": f"The moment with MOID={moid} not found for contact `{contact.name}` (UID={uid})"
            }

        # 在顶层评论中查找
        for i, comment in enumerate(target_moment.comments):
            if comment.cid == my_cid and comment.send_uid == self.my_uid:
                target_moment.comments.pop(i)
                return {
                    "status": "ok",
                    "output": f"You have successfully withdrawn your comment (CID={my_cid}) on moment (MOID={moid})"
                }

        return {
            "status": "failed",
            "output": f"Your comment with CID={my_cid} not found (or you didn't post it) under moment MOID={moid}"
        }
    
    @network_trouble()
    def withdraw_comment_comment(self, uid: str, moid: str, cid: str, my_cid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }

        target_moment = None
        for moment in contact.moments:
            if moment.moid == moid:
                target_moment = moment
                break
        if target_moment is None:
            return {
                "status": "failed",
                "output": f"The moment with MOID={moid} not found for contact `{contact.name}` (UID={uid})"
            }

        def remove_nested_comment(comments_list):
            for i, comment in enumerate(comments_list):
                if comment.cid == my_cid:
                    if comment.send_uid != self.my_uid:
                        raise PermissionError("Not your comment")
                    comments_list.pop(i)
                    return True
                if comment.comments:
                    try:
                        if remove_nested_comment(comment.comments):
                            return True
                    except PermissionError:
                        raise
            return False

        try:
            found_and_removed = remove_nested_comment(target_moment.comments)
        except PermissionError:
            return {
                "status": "failed",
                "output": f"You cannot withdraw comment CID={my_cid} because it was not posted by you."
            }

        if not found_and_removed:
            return {
                "status": "failed",
                "output": f"Your reply with CID={my_cid} under comment CID={cid} (or anywhere in moment MOID={moid}) was not found."
            }

        return {
            "status": "ok",
            "output": f"You have successfully withdrawn your reply (CID={my_cid}) to comment (CID={cid}) under moment (MOID={moid}) of contact `{contact.name}` (UID={uid})"
        }
    
    @network_trouble()
    def mark_as_read(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }
        
        contact.read_new_message = True

        return {
            "status": "ok",
            "output": f"You have successfully marked the messages from contact `{contact.name}` (UID={uid}) as read"
        }
    
    @network_trouble()
    def mark_as_unread(self, uid: str):
        contact = self.contacts_dict.get(uid)
        if contact is None:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }
        if contact.blocked:
            return {
                "status": "failed",
                "output": f"You've already blocked {contact.name} ({uid}). Please unblock {'him' if contact.gender == 'male' else 'her'} first."
            }
        
        contact.read_new_message = False

        return {
            "status": "ok",
            "output": f"You have successfully marked the messages from contact `{contact.name}` (UID={uid}) as unread"
        }
    
    def get_session_dict(self):
        return {
            uid: asdict(contact) for uid, contact in self.contacts_dict.items()
        }
    
    @network_trouble()
    def get_my_moments(self):
        contact = self.contacts_dict[self.my_uid]

        return {
            "status": "ok",
            "output": [asdict(moment) for moment in contact.moments]
        }
    
    @network_trouble()
    @require_privilege
    def post_moment(self, content: str, img_urls: List[str]):
        contact = self.contacts_dict[self.my_uid]
        moment = Moment(
            moid=f"mo_{self.uuid()}",
            owner_uid=self.my_uid,
            content=content,
            img_urls=img_urls,
            timestamp=self.time_machine.step(),
            ip=self.my_ip
        )

        contact.moments.append(moment)

        return {
            "status": "ok",
            "output": f"You have successfully post a moment (MOID = {moment.moid})"
        }

    @network_trouble()
    @require_privilege    
    def delete_moment(self, moid: str):
        contact = self.contacts_dict[self.my_uid]
        for idx, moment in enumerate(contact.moments):
            if moment.moid == moid:
                contact.moments.pop(idx)
                return {
                    "status": "ok",
                    "output": f"You have successfully deleted one moment (MOID = {moid})"
                }

        return {
            "status": "failed",
            "output": f"Moment (MOID = {moid}) not found"
        }

    def get_shared_url_of_moment(self, uid: str, moid: str):
        return {
            "status": "ok",
            "output": f"light://moment.talk.so?uid={uid}&moid={moid}"
        }
    
    def get_shared_url_of_contact(self, uid: str):
        return {
            "status": "ok",
            "output": f"light://contact.talk.so?uid={uid}"
        }
    
    @network_trouble()
    @require_privilege
    def delete_contact(self, uid: str):
        if uid == self.my_uid:
            return {
                "status": "failed",
                "output": f"You can't delete yourself."
            }

        if uid not in self.contacts_dict:
            return {
                "status": "failed",
                "output": f"Contact with UID ({uid}) not found"
            }

        contact_info = asdict(self.contacts_dict[uid])

        del self.contacts_dict[uid]

        return {
            "status": "ok",
            "output": f"You have successfully deleted the contact {contact_info['name']} (UID={contact_info['uid']})"
        }



if __name__ == "__main__":
    contact_session = ContactSession(seed=42)

    print(contact_session.list_all_tags())

    print(contact_session.delete_contact(uid="user_C7SSUjgz7QMsGCTSHGvTsZ"))
    print(contact_session.ask_for_privilege())
    print(contact_session.delete_contact(uid="user_C7SSUjgz7QMsGCTSHGvTsZ"))

    print(contact_session.list_all_tags())