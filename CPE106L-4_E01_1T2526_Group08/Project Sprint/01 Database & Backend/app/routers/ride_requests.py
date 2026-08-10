from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..database import engine
from ..models.models import RideRequest, User, Driver
from ..services.scheduler import assign_driver_to_ride
from ..services.google_maps import make_static_map_url, geocode_location


router = APIRouter(prefix="/ride-requests", tags=["Ride Requests"])


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/", response_model=list[RideRequest])
def list_rides(user_id: int = Query(None), driver_id: int = Query(None), session: Session = Depends(get_session)):
    statement = select(RideRequest)
    if user_id is not None:
        statement = statement.where(RideRequest.user_id == user_id)
    if driver_id is not None:
        statement = statement.where(RideRequest.driver_id == driver_id)
    return session.exec(statement).all()


@router.post("/")
def create_ride(req: RideRequest, session: Session = Depends(get_session)):
    # 1) Validate user
    user = session.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) Initialize lifecycle fields
    req.status = "requested"
    req.requested_at = datetime.utcnow()

    session.add(req)
    session.commit()
    session.refresh(req)

    # 3) Try to auto-assign a driver
    assigned = assign_driver_to_ride(session, req)
    if not assigned:
        # leave as "requested" if no driver or missing coords
        raise HTTPException(status_code=400, detail="No available drivers or missing pickup coordinates")

    # 4) Attach static map URL to the response
    static_map_url = make_static_map_url(assigned.pickup_lat, assigned.pickup_lng, assigned.dropoff_lat, assigned.dropoff_lng)
    response = assigned.dict() if hasattr(assigned, 'dict') else dict(assigned)
    response["static_map_url"] = static_map_url
    return response

@router.get("/{ride_id}/static-map")
def ride_static_map(ride_id: int, session: Session = Depends(get_session)):
    ride = session.get(RideRequest, ride_id)
    if not ride:
        raise HTTPException(404, "Ride not found")
    url = make_static_map_url(ride.pickup_lat, ride.pickup_lng, ride.dropoff_lat, ride.dropoff_lng)
    return {"static_map_url": url}

@router.get("/geocode")
def geocode(address: str = Query(...)):
    """
    Convert an address to latitude and longitude.
    Returns {"lat": <float>, "lng": <float>} or null if not found.
    """
    coords = geocode_location(address)
    if coords:
        return {"lat": coords[0], "lng": coords[1]}
    return {"lat": None, "lng": None}


@router.patch("/{ride_id}/complete")
def complete_ride(ride_id: int, session: Session = Depends(get_session)):
    """
    Mark a ride as completed and set the assigned driver's status to 'available'.
    """
    ride = session.get(RideRequest, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # mark ride completed
    ride.status = "completed"
    session.add(ride)

    # update driver status if present
    if ride.driver_id:
        driver = session.get(Driver, ride.driver_id)
        if driver:
            driver.availability_status = "available"
            session.add(driver)

    session.commit()
    session.refresh(ride)
    return ride

