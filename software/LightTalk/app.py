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
    session = session_dict.get(session_id)
    if session is None:
        return {
            "stutas": "failed",
            "output": "session not found"
        }
    session_info = {
        "status": "ok",
        "contacts": session.contact_session.get_dict()
    }
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")

    return session_info

@mcp.tool
async def get_all_contacts(session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return {
            "stutas": "failed",
            "output": "session not found"
        }
    
    return session.contact_session.get_all_contacts()

@mcp.tool
async def get_uid_from_name(name: str, session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return {
            "status": "failed",
            "output": "session not found"
        }
    
    return session.contact_session.get_uid_from_name(name)

@mcp.tool
async def send_message(uid: str, content: str, session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return {
            "status": "failed",
            "output": "session not found"
        }

    return session.contact_session.send_message(uid, content)

@mcp.tool
async def get_myuid(session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return {
            "status": "failed",
            "output": "session not found"
        }
    
    return session.contact_session.get_myuid()

@mcp.tool
async def get_chat_history(uid: str, session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return {
            "status": "failed",
            "output": "session not found"
        }
    
    return session.contact_session.get_chat_history(uid)