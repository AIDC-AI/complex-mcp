from typing import Dict, List, Any
from fastmcp import FastMCP
from session import LightFlightSession
import logging
import colorlog

LOG_FORMAT = '%(log_color)s%(levelname)-8s%(reset)s %(message)s'
colorlog.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


mcp = FastMCP("LightFlight")

session_dict: Dict[str, LightFlightSession] = {}


def get_session(session_id: str):
    session = session_dict.get(session_id)
    if session is None:
        return None, {"status": "failed", "output": "session not found"}
    return session, None


@mcp.tool
async def login(seed: int, os_cfg: Dict[str, str]):
    session = LightFlightSession(seed=seed, os_cfg=os_cfg)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {"status": "ok", "session_id": session.session_id, "session_info": {"status": "ok", "output": session.flight_session.get_session_dict()}}


@mcp.tool
async def logout(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    session_info = {"status": "ok", "output": session.flight_session.get_session_dict()}
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")
    return session_info


@mcp.tool
async def list_airlines(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.list_airlines()


@mcp.tool
async def list_airports(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.list_airports()


@mcp.tool
async def search_flights(origin: str, dest: str, date: str, passengers: int, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.search_flights(origin, dest, date, passengers)


@mcp.tool
async def get_flight_details(flight_no: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_flight_details(flight_no)


@mcp.tool
async def hold_seat(flight_no: str, seat_class: str, hold_minutes: int, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.hold_seat(flight_no, seat_class, hold_minutes)


@mcp.tool
async def confirm_payment(hold_id: str, amount: float, method: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.confirm_payment(hold_id, amount, method)


@mcp.tool
async def book_flight(flight_no: str, passenger_info: Dict[str, Any], seat_class: str, promo: str | None, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.book_flight(flight_no, passenger_info, seat_class, promo)


@mcp.tool
async def cancel_booking(booking_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.cancel_booking(booking_id)


@mcp.tool
async def list_bookings(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.list_bookings()


@mcp.tool
async def get_booking(booking_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_booking(booking_id)


@mcp.tool
async def upgrade_seat(booking_id: str, target_class: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.upgrade_seat(booking_id, target_class)


@mcp.tool
async def get_fare_rules(flight_no: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_fare_rules(flight_no)


@mcp.tool
async def get_seat_map(flight_no: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_seat_map(flight_no)


@mcp.tool
async def check_in(booking_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.check_in(booking_id)


@mcp.tool
async def get_boarding_pass(booking_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_boarding_pass(booking_id)


@mcp.tool
async def list_promotions(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.list_promotions()


@mcp.tool
async def apply_promo(promo_code: str, booking_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.apply_promo(promo_code, booking_id)


@mcp.tool
async def get_wallet_balance(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_wallet_balance()


@mcp.tool
async def add_funds(amount: float, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.add_funds(amount)


@mcp.tool
async def refund(booking_id: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.refund(booking_id)


@mcp.tool
async def estimate_travel_time(origin: str, dest: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.estimate_travel_time(origin, dest)


@mcp.tool
async def suggest_connections(origin: str, dest: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.suggest_connections(origin, dest)


@mcp.tool
async def report_issue(booking_id: str, issue: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.report_issue(booking_id, issue)


@mcp.tool
async def get_operational_status(flight_no: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_operational_status(flight_no)


@mcp.tool
async def get_delay_estimate(flight_no: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_delay_estimate(flight_no)


@mcp.tool
async def get_baggage_info(flight_no: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_baggage_info(flight_no)


@mcp.tool
async def add_baggage(booking_id: str, kg: int, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.add_baggage(booking_id, kg)


@mcp.tool
async def set_preference(key: str, value: Any, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.set_preference(key, value)


@mcp.tool
async def get_preference(key: str, session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.get_preference(key)


@mcp.tool
async def health(session_id: str):
    session, err = get_session(session_id)
    if err:
        return err
    return session.flight_session.health()
