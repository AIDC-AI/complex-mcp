from typing import Dict
from fastmcp import FastMCP
from session import LightShopSession
import logging
import colorlog

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


mcp = FastMCP("LightShop")

session_dict: Dict[str, LightShopSession] = {}

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
    session = LightShopSession(seed=seed)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {
        "status": "ok",
        "session_id": session.session_id,
        "session_info": {
            "status": "ok",
            "output": session.shop_session.get_session_dict()
        }
    }

@mcp.tool
async def logout(session_id: str):
    session, err = get_session(session_id)
    if err: return err
    session_info = {
        "status": "ok",
        "output": session.shop_session.get_session_dict()
    }
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")

    return session_info

@mcp.tool
async def list_all_shop_categories(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.list_all_shop_categories()

@mcp.tool
async def list_all_shops_by_category(category: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.list_all_shops_by_category(category)

@mcp.tool
async def get_shop_id_by_name(shop_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_shop_id_by_name(shop_name)

@mcp.tool
async def list_items(sid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.list_items(sid)

@mcp.tool
async def add_to_cart(sid: str, tid: str, cnt: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.add_to_cart(sid, tid, cnt)

@mcp.tool
async def get_item_info(sid: str, tid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_item_info(sid, tid)

@mcp.tool
async def delete_item_in_cart(caid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.delete_item_in_cart(caid)

@mcp.tool
async def check_balance(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.check_balance()

@mcp.tool
async def checkout_all(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.checkout_all()

@mcp.tool
async def get_trans_history(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_trans_history()

# TODO
@mcp.tool
async def get_cart_summary(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_cart_summary()

@mcp.tool
async def search_shops(shop_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.search_shops(shop_name)

@mcp.tool
async def fuzzy_search_shops(shop_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.fuzzy_search_shops(shop_name)

@mcp.tool
async def search_items(item_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.search_items(item_name)

@mcp.tool
async def fuzzy_search_items(item_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.fuzzy_search_items(item_name)

@mcp.tool
async def search_items_in_shop(sid: str, item_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.search_items_in_shop(sid, item_name)

@mcp.tool
async def fuzzy_search_items_in_shop(sid: str, item_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.fuzzy_search_items_in_shop(sid, item_name)

@mcp.tool
async def get_trans_info(trid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_trans_info(trid)

@mcp.tool
async def delete_trans_history(trid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.delete_trans_history(trid)

@mcp.tool
async def star_shop(sid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.star_shop(sid)

@mcp.tool
async def unstar_shop(sid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.unstar_shop(sid)

@mcp.tool
async def star_item(sid: str, tid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.star_item(sid, tid)

@mcp.tool
async def unstar_item(sid: str, tid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.unstar_item(sid, tid)

@mcp.tool
async def get_starred_shops(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_my_starred_shops()

@mcp.tool
async def get_my_starred_items(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.get_my_starred_items()

@mcp.tool
async def wait_payment_password(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.shop_session.wait_payment_password()