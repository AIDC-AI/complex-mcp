from typing import Dict, List
from fastmcp import FastMCP
from session import LightNewsSession
import logging
import colorlog

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


mcp = FastMCP("LightNews")

session_dict: Dict[str, LightNewsSession] = {}

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
    session = LightNewsSession(seed=seed, os_cfg=os_cfg)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {
        "status": "ok",
        "session_id": session.session_id,
        "session_info": {
            "status": "ok",
            "output": session.news_session.get_session_dict()
        }
    }

@mcp.tool
async def logout(session_id: str):
    session, err = get_session(session_id)
    if err: return err
    session_info = {
        "status": "ok",
        "output": session.news_session.get_session_dict()
    }
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")

    return session_info

@mcp.tool
async def list_all_sections(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.news_session.list_all_sections()

@mcp.tool
async def get_last_k_news(section: str, k: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.news_session.get_last_k_news(section, k)

@mcp.tool
async def search(
    session_id: str,
    section: str,
    query: str,
    maxn: int,
    begin_date: str | None = None,
    end_date: str | None = None
):
    session, err = get_session(session_id)
    if err: return err

    return session.news_session.search(
        section=section,
        query=query,
        maxn=maxn,
        begin_date=begin_date,
        end_date=end_date
    )

@mcp.tool
async def get_details(nid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.news_session.get_details(nid)

@mcp.tool
async def get_news_url(nid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.news_session.get_news_url(nid)