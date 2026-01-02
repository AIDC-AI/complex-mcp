from typing import Dict, List, Any
from fastmcp import FastMCP
from session import LightStockSession
import logging
import colorlog

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


mcp = FastMCP("LightStock")

session_dict: Dict[str, LightStockSession] = {}


def get_session(session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return None, {"status": "failed", "output": "session not found"}
    return session, None


@mcp.tool
async def login(seed: int, os_cfg: Dict[str, str]):
    session = LightStockSession(seed=seed, os_cfg=os_cfg)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {"status": "ok", "session_id": session.session_id, "session_info": {"status": "ok", "output": session.stock_session.get_session_dict()}}


@mcp.tool
async def logout(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    session_info = {"status": "ok", "output": session.stock_session.get_session_dict()}
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")
    return session_info


@mcp.tool
async def list_markets(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.list_markets()


@mcp.tool
async def list_companies(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.list_companies()


@mcp.tool
async def get_quote(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_quote(symbol)


@mcp.tool
async def get_historical(symbol: str, days: int, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_historical(symbol, days)


@mcp.tool
async def place_order(symbol: str, side: str, qty: int, price: float | None, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.place_order(symbol, side, qty, price)


@mcp.tool
async def cancel_order(order_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.cancel_order(order_id)


@mcp.tool
async def list_orders(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.list_orders()


@mcp.tool
async def get_order(order_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_order(order_id)


@mcp.tool
async def get_portfolio(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_portfolio()


@mcp.tool
async def deposit_funds(amount: float, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.deposit_funds(amount)


@mcp.tool
async def withdraw_funds(amount: float, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.withdraw_funds(amount)


@mcp.tool
async def get_company_info(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_company_info(symbol)


@mcp.tool
async def search_stocks(keyword: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.search_stocks(keyword)


@mcp.tool
async def get_watchlist(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_watchlist()


@mcp.tool
async def add_watch(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.add_watch(symbol)


@mcp.tool
async def remove_watch(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.remove_watch(symbol)


@mcp.tool
async def dividend_history(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.dividend_history(symbol)


@mcp.tool
async def analyst_rating(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.analyst_rating(symbol)


@mcp.tool
async def market_news(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.market_news(symbol)


@mcp.tool
async def set_alert(symbol: str, target_price: float, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.set_alert(symbol, target_price)


@mcp.tool
async def list_alerts(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.list_alerts()


@mcp.tool
async def delete_alert(alert_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.delete_alert(alert_id)


@mcp.tool
async def get_trade_history(symbol: str | None, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_trade_history(symbol)


@mcp.tool
async def get_market_status(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_market_status()


@mcp.tool
async def simulate_trade(symbol: str, side: str, qty: int, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.simulate_trade(symbol, side, qty)


@mcp.tool
async def get_order_book(symbol: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.get_order_book(symbol)


@mcp.tool
async def health(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.stock_session.health()
