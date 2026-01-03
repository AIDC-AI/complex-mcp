from typing import Dict, List
from fastmcp import FastMCP
from session import LightTalkSession
import logging
import colorlog

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


mcp = FastMCP("LightTalk")

session_dict: Dict[str, LightTalkSession] = {}

def get_session(session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return None, {
            "status": "failed",
            "output": "session not found"
        }
    return session, None

@mcp.tool
async def login(seed: int, os_cfg: Dict[str, str]):
    session = LightTalkSession(seed=seed, os_cfg=os_cfg)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {
        "status": "ok",
        "session_id": session.session_id,
        "session_info": {
            "status": "ok",
            "output": session.contact_session.get_session_dict()
        }
    }

@mcp.tool
async def logout(session_id: str | None = None):
    session, err = get_session(session_id)
    if err: return err
    session_info = {
        "status": "ok",
        "output": session.contact_session.get_session_dict()
    }
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")

    return session_info

@mcp.tool
async def get_all_contacts(session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_all_contacts()

@mcp.tool
async def get_contacts(page: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_contacts(page)

@mcp.tool
async def get_uid_from_name(name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_uid_from_name(name)

@mcp.tool
async def send_message(uid: str, content: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.send_message(uid, content)

@mcp.tool
async def get_myuid(session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_myuid()

@mcp.tool
async def get_chat_history(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_chat_history(uid)

@mcp.tool
async def delete_chat_history(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.delete_chat_history(uid)

@mcp.tool
async def delete_message(uid: str, mid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.delete_message(uid, mid)

@mcp.tool
async def block(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.block(uid)

@mcp.tool
async def unblock(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.unblock(uid)

@mcp.tool
async def get_contact_info(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_contact_info(uid)

@mcp.tool
async def get_all_moments(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_all_moments(uid)

@mcp.tool
async def get_last_k_moments(uid: str, k: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_last_k_moments(uid, k)

@mcp.tool
async def get_moment(uid: str, index: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.get_moment(uid, index)

@mcp.tool
async def like_moment(uid: str, moid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.like_moment(uid, moid)

@mcp.tool
async def unlike_moment(uid: str, moid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.unlike_moment(uid, moid)

@mcp.tool
async def comment_moment(uid: str, moid: str, content: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.comment_moment(uid, moid, content)

@mcp.tool
async def comment_comment(uid: str, moid: str, cid: str, content: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.comment_comment(uid=uid, moid=moid, cid=cid, content=content)

@mcp.tool
async def list_all_tags(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.list_all_tags()

@mcp.tool
async def get_contacts_by_tag(tag: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_contacts_by_tag(tag)

@mcp.tool
async def get_contacts_by_gender(gender: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_contacts_by_gender(gender)

@mcp.tool
async def withdraw_comment_moment(uid: str, moid: str, my_cid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.withdraw_comment_moment(uid, moid, my_cid)

@mcp.tool
async def withdraw_comment_comment(uid: str, moid: str, cid: str, my_cid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.withdraw_comment_comment(uid, moid, cid, my_cid)

@mcp.tool
async def mark_as_read(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.mark_as_read(uid)

@mcp.tool
async def mark_as_unread(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.mark_as_unread(uid)

@mcp.tool
async def get_my_moments(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_my_moments()

@mcp.tool
async def post_moment(content: str, img_urls: List[str], session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.post_moment(content, img_urls)

@mcp.tool
async def delete_moment(moid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.delete_moment(moid)

@mcp.tool
async def get_shared_url_of_moment(uid: str, moid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_shared_url_of_moment(uid, moid)

@mcp.tool
async def get_shared_url_of_contact(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_shared_url_of_contact(uid)

@mcp.tool
async def delete_contact(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.delete_contact(uid)

@mcp.tool
async def ask_for_privilege(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.ask_for_privilege()

@mcp.tool
async def list_ip_choices(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.list_ip_choices()

@mcp.tool
async def change_my_ip(where: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.change_my_ip(where)

@mcp.tool
async def edit_remark(uid: str, remark: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.edit_remark(uid, remark)

@mcp.tool
async def delete_remark(uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.delete_remark(uid)

@mcp.tool
async def create_group_chat(uids: List[str], session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.create_group_chat(uids)

@mcp.tool
async def send_message_to_group(gid: str, content: str, at: List[str] | str = [], session_id: str = ""):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.send_message_to_group(gid, content, at)

@mcp.tool
async def get_group_chat_history(gid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_group_chat_history(gid)

@mcp.tool
async def send_image(uid: str, img_url: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.send_image(uid, img_url)

@mcp.tool
async def send_image_to_group(gid: str, img_url: str, at: List[str] | str = [], session_id: str = ""):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.send_image_to_group(gid, img_url, at)

@mcp.tool
async def rename_group(gid: str, name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.rename_group(gid, name)

@mcp.tool
async def delete_group(gid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.delete_group(gid)

@mcp.tool
async def change_owner_of_group(gid: str, uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.change_owner_of_group(gid, uid)

@mcp.tool
async def quit_group(gid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.quit_group(gid)

@mcp.tool
async def invite_new_member(gid: str, uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.invite_new_member(gid, uid)

@mcp.tool
async def list_all_groups(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.list_all_groups()

@mcp.tool
async def get_group_info(gid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.get_group_info(gid)

@mcp.tool
async def mark_as_read_in_group(gid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.mark_as_read_in_group(gid)

@mcp.tool
async def mark_as_unread_in_group(gid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.mark_as_unread_in_group(gid)

@mcp.tool
async def acc_network(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.contact_session.acc_network()