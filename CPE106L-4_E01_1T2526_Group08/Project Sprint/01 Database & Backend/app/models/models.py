from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


# -------------------------
# USER
# -------------------------
class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: Optional[str] = None
    priority_level: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    ride_requests: List["RideRequest"] = Relationship(back_populates="user")


# -------------------------
# DRIVER
# -------------------------
class Driver(SQLModel, table=True):
    driver_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: Optional[str] = None
    vehicle_type: str
    plate_number: str

    # availability: "available", "on_ride", "inactive"
    availability_status: str = "available"

    # NEW: live position for matching
    current_lat: float = 0.0
    current_lng: float = 0.0

    ride_requests: List["RideRequest"] = Relationship(back_populates="driver")


# -------------------------
# RIDE REQUEST
# -------------------------
class RideRequest(SQLModel, table=True):
    ride_id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.user_id")
    driver_id: Optional[int] = Field(default=None, foreign_key="driver.driver_id")

    # human-readable addresses
    pickup_location: str
    dropoff_location: str

    # NEW: coordinates (recommended for matching)
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None

    # lifecycle: "requested", "assigned", "ongoing", "completed", "cancelled"
    status: str = "requested"

    requested_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = None

    # NEW: set when a driver is assigned (for analytics)
    assigned_at: Optional[datetime] = None

    # optional estimates
    estimated_distance: Optional[float] = None
    estimated_duration: Optional[int] = None

    user: Optional[User] = Relationship(back_populates="ride_requests")
    driver: Optional[Driver] = Relationship(back_populates="ride_requests")
