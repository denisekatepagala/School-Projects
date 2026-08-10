from math import radians, sin, cos, asin, sqrt
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from app.models.models import Driver, RideRequest, User

# NEW: import the Maps helper
from app.services.google_maps import get_eta_and_distance_minutes

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def _score(distance_km: float, eta_min: float, user_priority: int) -> float:
    return (distance_km * 1.0) + (eta_min * 0.3) - (user_priority * 0.5)

def choose_best_driver(session: Session, ride: RideRequest) -> Optional[Driver]:
    if ride.pickup_lat is None or ride.pickup_lng is None:
        return None

    drivers = session.exec(
        select(Driver).where(Driver.availability_status == "available")
    ).all()
    if not drivers:
        return None

    user = session.get(User, ride.user_id)
    user_priority = user.priority_level if user else 0

    best_driver, best_score = None, float("inf")

    for d in drivers:
        # Try Google Distance Matrix (ETA from driver -> pickup)
        maps_result = get_eta_and_distance_minutes(
            d.current_lat, d.current_lng, ride.pickup_lat, ride.pickup_lng
        )

        if maps_result is not None:
            eta_min, dist_km = maps_result
        else:
            # Fallback: Haversine + 20 km/h heuristic
            dist_km = _haversine_km(ride.pickup_lat, ride.pickup_lng, d.current_lat, d.current_lng)
            eta_min = (dist_km / 20.0) * 60.0

        score = _score(dist_km, eta_min, user_priority)
        if score < best_score:
            best_driver, best_score = d, score

    return best_driver

def assign_driver_to_ride(session: Session, ride: RideRequest) -> Optional[RideRequest]:
    driver = choose_best_driver(session, ride)
    if not driver:
        return None

    ride.driver_id = driver.driver_id
    ride.status = "assigned"
    ride.assigned_at = datetime.utcnow()
    driver.availability_status = "on_ride"

    # Optional: also set estimates from pickup -> dropoff using Maps
    if ride.dropoff_lat is not None and ride.dropoff_lng is not None:
        maps_leg = get_eta_and_distance_minutes(
            ride.pickup_lat, ride.pickup_lng, ride.dropoff_lat, ride.dropoff_lng
        )
        if maps_leg is not None:
            ride.estimated_duration, ride.estimated_distance = maps_leg[0], maps_leg[1]

    session.add(ride)
    session.add(driver)
    session.commit()
    session.refresh(ride)
    return ride
