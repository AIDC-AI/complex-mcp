from typing import Dict, List
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
        return None, {
            "status": "failed",
            "output": "session not found"
        }
    return session, None

@mcp.tool
async def login(seed: int, os_cfg: Dict[str, str]):
    session = LightFlightSession(seed=seed, os_cfg=os_cfg)
    session_dict[session.session_id] = session
    logger.info(f"A new user logged in! [{session.session_id}]")
    return {
        "status": "ok",
        "session_id": session.session_id,
        "session_info": {
            "status": "ok",
            "output": session.flight_session.get_session_dict()
        }
    }

@mcp.tool
async def logout(session_id: str | None = None):
    session, err = get_session(session_id)
    if err: return err
    session_info = {
        "status": "ok",
        "output": session.flight_session.get_session_dict()
    }
    del session_dict[session_id]
    logger.info(f"A user logged out! [{session_id}]")

    return session_info

@mcp.tool
async def list_all_cities(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.list_all_cities()

@mcp.tool
async def list_airports_by_city(city: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.list_airports_by_city(city)

@mcp.tool
async def get_flight_details(fid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.get_flight_details(fid)

@mcp.tool
async def search_flights(departure: str, arrival: str, date: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.search_flights(departure, arrival, date)

@mcp.tool
async def check_seat_availability(fid: str, seat_class: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.check_seat_availability(fid, seat_class)

@mcp.tool
async def check_passengers(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.check_passengers()

@mcp.tool
async def add_passenger(name: str, light_talk_uid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.add_passenger(name, light_talk_uid)

@mcp.tool
async def remove_passenger(passenger_idx: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.remove_passenger(passenger_idx)

@mcp.tool
async def add_to_booking(fid: str, seat_class: str, passenger_idx: int, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.add_to_booking(fid, seat_class, passenger_idx)

@mcp.tool
async def check_bookings(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.check_bookings()

@mcp.tool
async def remove_from_booking(bid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.remove_from_booking(bid)

@mcp.tool
async def wait_payment_password(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.wait_payment_password()

@mcp.tool
async def checkout_bookings(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.checkout_bookings()

@mcp.tool
async def check_balance(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.check_balance()

@mcp.tool
async def get_booking_history(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.get_booking_history()

@mcp.tool
async def cancel_booking(bids: List[str], session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.cancel_booking(bids)

@mcp.tool
async def search_airports(airport_name: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.search_airports(airport_name)

@mcp.tool
async def star_airport(aid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.star_airport(aid)

@mcp.tool
async def unstar_airport(aid: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.unstar_airport(aid)

@mcp.tool
async def get_my_starred_airports(session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.get_my_starred_airports()

@mcp.tool
async def get_fids_by_arrival(arrival: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.get_fids_by_arrival(arrival)

@mcp.tool
async def get_fids_by_departure(departure: str, session_id: str):
    session, err = get_session(session_id)
    if err: return err

    return session.flight_session.get_fids_by_departure(departure)

