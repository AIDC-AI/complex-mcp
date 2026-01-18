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
    return {
        "status": "ok",
        "session_id": session.session_id,
        "session_info": {
            "status": "ok",
            "output": session.stock_session.get_session_dict()
        }
    }


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
async def get_account_summary(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_account_summary()

@mcp.tool
async def list_all_sectors(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.list_all_sectors()

@mcp.tool
async def list_all_tickers_by_sector(sector: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.list_all_tickers_by_sector(sector)

@mcp.tool
async def search_stocks(session_id: str, query: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.search_stocks(query)


@mcp.tool
async def get_stock_details(session_id: str, ticker: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_stock_details(ticker)


@mcp.tool
async def wait_trade_password(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.wait_trade_password()


@mcp.tool
async def transfer_funds(session_id: str, amount: float, direction: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.transfer_funds(amount, direction)


@mcp.tool
async def place_market_order(session_id: str, ticker: str, side: str, quantity: int):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.place_market_order(ticker, side, quantity)


@mcp.tool
async def place_limit_order(session_id: str, ticker: str, side: str, quantity: int, limit_price: float):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.place_limit_order(ticker, side, quantity, limit_price)


@mcp.tool
async def place_stop_loss_order(session_id: str, ticker: str, quantity: int, stop_price: float):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.place_stop_loss_order(ticker, quantity, stop_price)


@mcp.tool
async def get_portfolio(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_portfolio()


@mcp.tool
async def get_pending_orders(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_pending_orders()


@mcp.tool
async def cancel_order(session_id: str, oid: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.cancel_order(oid)


@mcp.tool
async def get_trade_history(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_trade_history()


@mcp.tool
async def toggle_watchlist(session_id: str, ticker: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.toggle_watchlist(ticker)


@mcp.tool
async def get_watchlist_details(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_watchlist_details()


@mcp.tool
async def check_vip_price(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.check_vip_price()


@mcp.tool
async def upgrade_to_vip(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.upgrade_to_vip()


@mcp.tool
async def get_day_trades_remaining(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.get_day_trades_remaining()


@mcp.tool
async def set_price_alert(session_id: str, ticker: str, price: float):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.set_price_alert(ticker, price)

@mcp.tool
async def remove_price_alert(session_id: str, ticker: str):
    session, err = get_session(session_id)
    if err: return err

    return session.stock_session.remove_price_alert(ticker)