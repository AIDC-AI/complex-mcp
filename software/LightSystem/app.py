from typing import Dict, List
from fastmcp import FastMCP
from session import LightSystemSession
import logging
import colorlog

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

mcp = FastMCP("LightSystem")

session_dict: Dict[str, LightSystemSession] = {}

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
    session = LightSystemSession(seed=seed)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {
        "status": "ok",
        "session_id": session.session_id,
        "session_info": {
            "status": "ok",
            "output": session.get_session_dict()
        }
    }

@mcp.tool
async def logout(session_id: str):
    session, err = get_session(session_id)
    if err: return err
    session_info = {
        "status": "ok",
        "output": session.get_session_dict()
    }
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")

    return session_info

@mcp.tool
async def _step(session_id: str):
    # Not visible to LLM
    session, err = get_session(session_id)
    if err: return err

    return session.clock_session.step()

@mcp.tool
async def health(session_id: str):
    _, err = get_session(session_id)
    if err: return err

    return {
        "status": "ok",
        "output": "The OS is alive"
    }

@mcp.tool
async def now(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.clock_session.now()

@mcp.tool
async def _gen_past(start_year: int, k: int, session_id: str):
    # Not visible to LLM
    session, err = get_session(session_id)
    if err: return err

    return session.clock_session.gen_past(start_year, k)