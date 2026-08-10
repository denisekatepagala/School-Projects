import os
import requests
from typing import Optional, Tuple
from urllib.parse import quote_plus

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def geocode_location(address: str) -> Optional[Tuple[float, float]]:
    """
    Convert an address/location string to latitude and longitude.
    Returns (lat, lng) if successful, else None.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None
    
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY,
    }
    
    try:
        resp = requests.get(GEOCODING_URL, params=params, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") != "OK" or not data.get("results"):
            return None
        
        location = data["results"][0]["geometry"]["location"]
        lat = location.get("lat")
        lng = location.get("lng")
        return (lat, lng) if lat and lng else None
    
    except requests.RequestException:
        return None


# Fallback using OpenStreetMap Nominatim (no API key required)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_location_with_fallback(address: str) -> Optional[Tuple[float, float]]:
    """
    Try Google geocoding first (if key available), otherwise fall back to Nominatim.
    """
    # Try Google first
    res = geocode_location(address)
    if res:
        return res

    # Nominatim fallback
    try:
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "CPE106L-Project/1.0 (contact@example.com)"}
        r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5.0)
        r.raise_for_status()
        items = r.json()
        if items:
            item = items[0]
            lat = float(item.get("lat"))
            lon = float(item.get("lon"))
            return (lat, lon)
    except requests.RequestException:
        return None

    return None


def make_static_map_url(pickup_lat, pickup_lng, dropoff_lat=None, dropoff_lng=None, size="600x300"):
    if not GOOGLE_MAPS_API_KEY:
        return None
    markers = [f"color:green|label:P|{pickup_lat},{pickup_lng}"]
    if dropoff_lat is not None and dropoff_lng is not None:
        markers.append(f"color:red|label:D|{dropoff_lat},{dropoff_lng}")
    params = {
        "size": size,
        "maptype": "roadmap",
        "key": GOOGLE_MAPS_API_KEY,
        # markers will be joined as separate params
    }
    base = "https://maps.googleapis.com/maps/api/staticmap"
    markers_part = "&".join("markers=" + requests.utils.quote(m) for m in markers)
    qs = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items())
    return f"{base}?{qs}&{markers_part}"

def get_eta_and_distance_minutes(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    timeout: float = 5.0,
) -> Optional[Tuple[float, float]]:
    """
    Returns (duration_minutes, distance_km) if successful, else None.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None

    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": f"{dest_lat},{dest_lng}",
        "mode": "driving",
        "units": "metric",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        resp = requests.get(DISTANCE_MATRIX_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "OK":
            return None

        rows = data.get("rows", [])
        if not rows or not rows[0].get("elements"):
            return None

        el = rows[0]["elements"][0]
        if el.get("status") != "OK":
            return None

        duration_sec = el["duration"]["value"]           # seconds
        distance_m  = el["distance"]["value"]            # meters

        duration_min = duration_sec / 60.0
        distance_km  = distance_m / 1000.0
        return duration_min, distance_km

    except requests.RequestException:
        return None


def make_static_map_url(
    pickup_lat: float,
    pickup_lng: float,
    dropoff_lat: Optional[float] = None,
    dropoff_lng: Optional[float] = None,
    size: str = "600x300",
):
    """
    Build a Google Static Maps URL with markers for pickup (P) and optional dropoff (D).
    Returns a full URL string or None if API key is not configured.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None

    base = "https://maps.googleapis.com/maps/api/staticmap"
    markers = [f"color:green|label:P|{pickup_lat},{pickup_lng}"]
    if dropoff_lat is not None and dropoff_lng is not None:
        markers.append(f"color:red|label:D|{dropoff_lat},{dropoff_lng}")

    params = {
        "size": size,
        "maptype": "roadmap",
        "key": GOOGLE_MAPS_API_KEY,
    }

    # Build query string; markers can repeat
    qs = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    markers_part = "&".join("markers=" + quote_plus(m) for m in markers)
    return f"{base}?{qs}&{markers_part}"
