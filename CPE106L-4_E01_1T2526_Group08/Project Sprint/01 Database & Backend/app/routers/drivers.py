from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field as PydField
from sqlmodel import Session, select
from app.database import engine
from app.models.models import Driver

router = APIRouter(prefix="/drivers", tags=["Drivers"])

# ---------- Request bodies for PATCH endpoints ----------
class StatusUpdate(BaseModel):
    status: str = PydField(..., description="Driver status: available | on_ride | inactive")

class LocationUpdate(BaseModel):
    lat: float = PydField(..., description="Current latitude")
    lng: float = PydField(..., description="Current longitude")

# ---------- Session dependency ----------
def get_session():
    with Session(engine) as session:
        yield session

# ---------- CRUD ----------
@router.post("/", response_model=Driver)
def create_driver(driver: Driver, session: Session = Depends(get_session)):
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver

@router.get("/", response_model=List[Driver])
def get_drivers(session: Session = Depends(get_session)):
    return session.exec(select(Driver)).all()

@router.get("/{driver_id}", response_model=Driver)
def get_driver(driver_id: int, session: Session = Depends(get_session)):
    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.put("/{driver_id}", response_model=Driver)
def update_driver(driver_id: int, updated: Driver, session: Session = Depends(get_session)):
    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    # partial update using provided fields only
    for k, v in updated.dict(exclude_unset=True).items():
        setattr(driver, k, v)
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver

@router.delete("/{driver_id}")
def delete_driver(driver_id: int, session: Session = Depends(get_session)):
    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    session.delete(driver)
    session.commit()
    return {"message": "Driver deleted"}

# ---------- Extra endpoints used by the app/scheduler ----------
_ALLOWED_STATUSES = {"available", "on_ride", "inactive"}

@router.patch("/{driver_id}/status", response_model=Driver)
def set_status(driver_id: int, payload: StatusUpdate, session: Session = Depends(get_session)):
    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    if payload.status not in _ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Allowed: {sorted(_ALLOWED_STATUSES)}"
        )
    driver.availability_status = payload.status
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver

@router.patch("/{driver_id}/location", response_model=Driver)
def set_location(driver_id: int, payload: LocationUpdate, session: Session = Depends(get_session)):
    driver = session.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.current_lat = payload.lat
    driver.current_lng = payload.lng
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver
