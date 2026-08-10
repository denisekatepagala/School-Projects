# --- Load .env (for GOOGLE_MAPS_API_KEY, etc.) ---
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    # Safe to ignore if python-dotenv isn't installed
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import users, drivers, ride_requests

# Optional: include analytics router only if present
try:
    from app.routers import analytics
    HAS_ANALYTICS = True
except Exception:
    HAS_ANALYTICS = False

app = FastAPI(title="Accessible Transport Scheduler")

# --- CORS (dev-friendly; tighten in prod) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # set to your Flet app origin(s) in prod
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# --- DB bootstrapping ---
@app.on_event("startup")
def on_startup():
    init_db()  # creates tables if they don't exist

# --- Routers ---
app.include_router(users.router)
app.include_router(drivers.router)
app.include_router(ride_requests.router)
if HAS_ANALYTICS:
    app.include_router(analytics.router)
