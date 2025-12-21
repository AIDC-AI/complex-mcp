from typing import Dict
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
async def login(seed: int):
    session = LightTalkSession(seed=seed)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {
        "status": "ok",
        "session_id": session.session_id
    }

@mcp.tool
async def logout(session_id: str | None = None):
    session, err = get_session(session_id)
    if err: return err
    session_info = {
        "status": "ok",
        "contacts": session.contact_session.get_dict()
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
async def comment_moment(uid: str, moid: str, content: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err
    
    return session.contact_session.comment_moment(uid, moid, content)