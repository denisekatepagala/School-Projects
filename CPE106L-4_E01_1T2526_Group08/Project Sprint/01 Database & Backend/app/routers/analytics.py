from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import engine
from ..services.analytics import rides_per_day, avg_wait_minutes
from ..services.google_maps import get_eta_and_distance_minutes

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/rides-per-day")
def get_rides_per_day(days: int = 7, session: Session = Depends(get_session)):
    return rides_per_day(session, days)

@router.get("/avg-wait-time")
def get_avg_wait_time(days: int = 30, session: Session = Depends(get_session)):
    return avg_wait_minutes(session, days)


@router.get("/eta")
def get_eta(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float):
    """
    Return ETA in minutes and distance in km between origin and destination using Google Distance Matrix.
    Example: /analytics/eta?origin_lat=14.56&origin_lng=120.99&dest_lat=14.57&dest_lng=121.00
    """
    res = get_eta_and_distance_minutes(origin_lat, origin_lng, dest_lat, dest_lng)
    if res is None:
        return {"duration_min": None, "distance_km": None}
    duration_min, distance_km = res
    return {"duration_min": round(duration_min, 1), "distance_km": round(distance_km, 2)}
