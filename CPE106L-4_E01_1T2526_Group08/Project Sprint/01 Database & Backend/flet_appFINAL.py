import json
from typing import Optional
import requests
import flet as ft
from flet import Colors, Icons

DEFAULT_API_BASE = "http://127.0.0.1:8000"

# ------------- Thin REST client (no Google keys here) -------------
class Api:
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def _ok(self, r: requests.Response):
        try:
            r.raise_for_status()
            return r.json() if r.text else {}
        except requests.HTTPError as e:
            try:
                detail = r.json().get("detail")
            except Exception:
                detail = r.text
            raise RuntimeError(f"{r.status_code}: {detail}") from e

    # Users
    def create_user(self, name: str, email: str, phone: str, priority: int = 0):
        payload = {"name": name, "email": email, "phone": phone, "priority_level": priority}
        return self._ok(requests.post(f"{self.base}/users/", json=payload))

    # Drivers
    def create_driver(self, name: str, phone: str, vehicle_type: str, plate_number: str,
                      lat: Optional[float] = None, lng: Optional[float] = None,
                      status: str = "available"):
        payload = {
            "name": name, "phone": phone, "vehicle_type": vehicle_type,
            "plate_number": plate_number, "availability_status": status
        }
        if lat is not None and lng is not None:
            payload["current_lat"] = lat
            payload["current_lng"] = lng
        return self._ok(requests.post(f"{self.base}/drivers/", json=payload))

    def set_driver_status(self, driver_id: int, status: str):
        return self._ok(requests.patch(f"{self.base}/drivers/{driver_id}/status", json={"status": status}))

    def set_driver_location(self, driver_id: int, lat: float, lng: float):
        return self._ok(requests.patch(f"{self.base}/drivers/{driver_id}/location", json={"lat": lat, "lng": lng}))

    # Rides
    def create_ride(self, user_id: int, pickup_location: str, dropoff_location: str,
                    pickup_lat: float, pickup_lng: float,
                    dropoff_lat: Optional[float] = None, dropoff_lng: Optional[float] = None):
        payload = {
            "user_id": user_id,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng
        }
        if dropoff_lat is not None and dropoff_lng is not None:
            payload["dropoff_lat"] = dropoff_lat
            payload["dropoff_lng"] = dropoff_lng
        return self._ok(requests.post(f"{self.base}/ride-requests/", json=payload))

    def list_rides(self, user_id: Optional[int] = None, driver_id: Optional[int] = None):
        url = f"{self.base}/ride-requests/"
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if driver_id is not None:
            params["driver_id"] = driver_id
        if params:
            return self._ok(requests.get(url, params=params))
        return self._ok(requests.get(url))

    def get_driver(self, driver_id: int):
        return self._ok(requests.get(f"{self.base}/drivers/{driver_id}"))

    def list_drivers(self):
        return self._ok(requests.get(f"{self.base}/drivers/"))

    def get_user(self, user_id: int):
        return self._ok(requests.get(f"{self.base}/users/{user_id}"))

    def list_users(self):
        return self._ok(requests.get(f"{self.base}/users/"))


# ------------- Flet multi-screen app -------------
def main(page: ft.Page):
    print("[flet_app3] main() starting")
    page.title = "Accessible Transportation Scheduler"
    page.window_width = 1060
    page.window_height = 720
    page.padding = 16
    page.theme_mode = "light"

    # Sanity check control to ensure page can render basic controls
    sanity = ft.Text("[sanity] page.controls test - should be visible at top")
    page.controls.append(sanity)
    page.update()

    # shared
    api = Api(DEFAULT_API_BASE)

    def on_click_login(e=None):
        print("[flet_app3] Login button clicked")
        page.go("/login/choose")

    def on_click_register(e=None):
        print("[flet_app3] Register button clicked")
        page.go("/register/choose")

    def do_logout():
        print("[flet_app3] logging out")
        page.session.set("current_user", None)
        toast("Logged out", Colors.GREEN_400)
        # After logout, go to the login/register chooser so the user can sign in or register again
        page.go("/login/choose")

    def toast(msg: str, color=Colors.GREEN_400):
        print(f"[flet_app3] toast: {msg}")
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # convenience for passing data between screens
    def put_session(key, value):
        page.session.set(key, value)

    def get_session(key, default=None):
        v = page.session.get(key)
        return v if v is not None else default

    # ---------------- Home ----------------
    def home_view():
        current_user = get_session("current_user")
        controls = [
            ft.Text("Accessible Transportation Scheduler", size=28, weight="bold"),
            ft.Divider(),
        ]

        # show logged-in user on the home view if available
        if current_user:
            name = current_user.get("name") or current_user.get("email") or str(current_user.get("user_id") or "")
            # Distinguish between driver and user sessions
            is_user = (current_user.get("user_id") is not None) or ("user_id" in current_user)
            is_driver = (current_user.get("driver_id") is not None) or ("driver_id" in current_user)
            
            if is_driver:
                role_label = f"Logged in as driver: {name}"
            else:
                role_label = f"Logged in as {name}"
            
            controls.append(
                ft.Row([
                    ft.Text(role_label, weight="bold", color=Colors.BLUE_700),
                    ft.ElevatedButton("Logout", on_click=lambda e: do_logout()),
                ], alignment="end")
            )
            # quick actions for logged-in users (only show Request Ride for user accounts)
            if is_user:
                controls.append(
                    ft.Row([
                        ft.ElevatedButton("Request Ride", on_click=lambda e: page.go("/ride/new")),
                        ft.ElevatedButton("My Rides", on_click=lambda e: page.go("/user/rides")),
                    ], spacing=12)
                )
            # quick actions for drivers
            if is_driver:
                controls.append(
                    ft.Row([
                        ft.ElevatedButton("Driver Dashboard", on_click=lambda e: page.go("/driver/dashboard")),
                    ], spacing=12)
                )
        else:
            controls.append(
                ft.Row([
                    ft.ElevatedButton("Login", width=200, height=60, on_click=lambda e: on_click_login(e)),
                    ft.ElevatedButton("Register", width=200, height=60, on_click=lambda e: on_click_register(e)),
                ], spacing=40)
            )

        controls.extend([
            ft.Divider(),
            ft.Text("(After login you can access dashboards and admin analytics)", italic=True, size=12),
        ])
        print(f"[flet_app3] home_view() constructed with {len(controls)} controls")
        return ft.View(route="/", controls=controls)

    # ---------------- Login/Register choice screens ----------------
    def login_choose_view():
        return ft.View(
            route="/login/choose",
            controls=[
                ft.Text("Login As", size=22, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("User", on_click=lambda e: page.go("/login/user")),
                    ft.ElevatedButton("Driver", on_click=lambda e: page.go("/login/driver")),
                    ft.ElevatedButton("Administrator", on_click=lambda e: page.go("/login/admin")),
                ], spacing=12),
                ft.Row([ft.OutlinedButton("Back", on_click=lambda e: page.go("/"))]),
            ],
        )

    def register_choose_view():
        return ft.View(
            route="/register/choose",
            controls=[
                ft.Text("Register As", size=22, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("User", on_click=lambda e: page.go("/register/user")),
                    ft.ElevatedButton("Driver", on_click=lambda e: page.go("/register/driver")),
                ], spacing=12),
                ft.Row([ft.OutlinedButton("Back", on_click=lambda e: page.go("/"))]),
            ],
        )

    # ---------------- Create User ----------------
    u_name = ft.TextField(label="Name", width=280)
    u_email = ft.TextField(label="Email", width=280)
    u_phone = ft.TextField(label="Phone", width=220)
    u_prio = ft.TextField(label="Priority (0-5)", value="5", width=140)

    def do_create_user(_):
        print("[flet_app3] do_create_user called")
        if not u_name.value or not u_email.value:
            toast("Name and Email are required.", Colors.RED_400)
            return
        try:
            pr = int(u_prio.value.strip() or "0")
        except ValueError:
            toast("Priority must be an integer.", Colors.RED_400)
            return
        try:
            print(f"[flet_app3] creating user: {u_name.value}, {u_email.value}, pr={pr}")
            res = api.create_user(u_name.value, u_email.value, u_phone.value, pr)
            print(f"[flet_app3] create_user response: {res}")
            # Automatically log in the newly created user and go to dashboard
            put_session("current_user", res)
            # Clear form fields
            u_name.value = ""
            u_email.value = ""
            u_phone.value = ""
            u_prio.value = "5"
            toast(f"Welcome, {res.get('name')}! \u2713", Colors.GREEN_400)
            page.go("/user/rides")
        except Exception as e:
            print(f"[flet_app3] create_user exception: {e}")
            toast(f"Create user failed: {e}", Colors.RED_400)

    def user_new_view():
        return ft.View(
            route="/user/new",
            controls=[
                ft.Text("Create User", size=22, weight="bold"),
                ft.Row([u_name, u_email, u_phone, u_prio], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Submit", on_click=do_create_user),
                    ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/")),
                ], spacing=10),
            ],
        )

    # ---------------- Login / Registration hub ----------------
    l_identifier = ft.TextField(label="User ID or Email", width=360)

    def do_login(_):
        ident = l_identifier.value.strip()
        if not ident:
            toast("Enter user id or email to login.", Colors.RED_400)
            return
        try:
            if ident.isdigit():
                res = api.get_user(int(ident))
            else:
                users = api.list_users()
                # users endpoint returns list[User]
                res = next((u for u in users if u.get("email") == ident), None)
                if res is None:
                    raise RuntimeError("User not found")
            put_session("current_user", res)
            toast(f"Logged in as {res.get('name')} \u2713")
            page.go("/")
        except Exception as e:
            toast(f"Login failed: {e}", Colors.RED_400)

    def login_view():
        return ft.View(
            route="/login",
            controls=[
                ft.Text("Login", size=22, weight="bold"),
                ft.Row([l_identifier, ft.ElevatedButton("Login", on_click=do_login)], spacing=10),
                ft.Row([ft.OutlinedButton("Back to Home", on_click=lambda e: page.go("/"))]),
            ],
        )

    # ---------- Driver Login ----------
    d_login_id = ft.TextField(label="Driver ID", width=360)

    def do_driver_login(_):
        driver_id = d_login_id.value.strip()
        if not driver_id:
            toast("Enter driver ID to login.", Colors.RED_400)
            return
        try:
            if not driver_id.isdigit():
                toast("Driver ID must be a number.", Colors.RED_400)
                return
            res = api.get_driver(int(driver_id))
            put_session("current_user", res)
            toast(f"Logged in as driver: {res.get('name')} \u2713")
            page.go("/driver/dashboard")
        except Exception as e:
            toast(f"Driver login failed: {e}", Colors.RED_400)

    def driver_login_view():
        return ft.View(
            route="/login/driver",
            controls=[
                ft.Text("Driver Login", size=22, weight="bold"),
                ft.Row([d_login_id, ft.ElevatedButton("Login", on_click=do_driver_login)], spacing=10),
                ft.Row([ft.OutlinedButton("Back", on_click=lambda e: page.go("/login/choose"))]),
            ],
        )

    # ---------- Admin Login ----------
    a_login_password = ft.TextField(label="Admin Password", password=True, width=360)

    def do_admin_login(_):
        password = a_login_password.value.strip()
        if not password:
            toast("Enter admin password to login.", Colors.RED_400)
            return
        try:
            # Simple admin authentication (in production, use proper auth with backend)
            if password == "admin123":  # This is a simple demo password
                admin_user = {"admin_id": 1, "name": "Administrator", "role": "admin"}
                put_session("current_user", admin_user)
                toast(f"Logged in as Administrator \u2713")
                page.go("/admin")
            else:
                toast("Invalid admin password.", Colors.RED_400)
        except Exception as e:
            toast(f"Admin login failed: {e}", Colors.RED_400)

    def admin_login_view():
        return ft.View(
            route="/login/admin",
            controls=[
                ft.Text("Admin Login", size=22, weight="bold"),
                ft.Row([a_login_password, ft.ElevatedButton("Login", on_click=do_admin_login)], spacing=10),
                ft.Row([ft.OutlinedButton("Back", on_click=lambda e: page.go("/login/choose"))]),
            ],
        )

    def register_view():
        return ft.View(
            route="/register",
            controls=[
                ft.Text("Register", size=22, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("Register User", on_click=lambda e: page.go("/user/new")),
                    ft.ElevatedButton("Register Driver", on_click=lambda e: page.go("/driver/new")),
                ], spacing=10),
                ft.Row([ft.OutlinedButton("Back to Home", on_click=lambda e: page.go("/"))]),
            ],
        )

    # ---------------- Request Ride ----------------
    r_user_id = ft.TextField(label="User ID", width=120)
    r_pick = ft.TextField(label="Pickup Location", width=360)
    r_drop = ft.TextField(label="Drop-off Location", width=360)
    r_plat = ft.TextField(label="Pickup Lat", value="14.5649", width=180)
    r_plng = ft.TextField(label="Pickup Lng", value="120.9933", width=180)
    r_dlat = ft.TextField(label="Drop-off Lat", width=180)
    r_dlng = ft.TextField(label="Drop-off Lng", width=180)

    def geocode_pickup(_=None):
        """Geocode pickup location and auto-fill lat/lng"""
        if not r_pick.value.strip():
            return
        try:
            print(f"[flet_app3] geocoding pickup: {r_pick.value}")
            resp = requests.get(f"{api.base}/ride-requests/geocode", params={"address": r_pick.value})
            resp.raise_for_status()
            data = resp.json()
            lat, lng = data.get("lat"), data.get("lng")
            if lat and lng:
                r_plat.value = str(lat)
                r_plng.value = str(lng)
                page.update()
                print(f"[flet_app3] geocoded pickup: {lat}, {lng}")
            else:
                toast("Location not found", Colors.RED_400)
        except Exception as e:
            print(f"[flet_app3] geocode_pickup exception: {e}")
            toast(f"Geocoding failed: {e}", Colors.RED_400)

    def geocode_dropoff(_=None):
        """Geocode dropoff location and auto-fill lat/lng"""
        if not r_drop.value.strip():
            return
        try:
            print(f"[flet_app3] geocoding dropoff: {r_drop.value}")
            resp = requests.get(f"{api.base}/ride-requests/geocode", params={"address": r_drop.value})
            resp.raise_for_status()
            data = resp.json()
            lat, lng = data.get("lat"), data.get("lng")
            if lat and lng:
                r_dlat.value = str(lat)
                r_dlng.value = str(lng)
                page.update()
                print(f"[flet_app3] geocoded dropoff: {lat}, {lng}")
            else:
                toast("Location not found", Colors.RED_400)
        except Exception as e:
            print(f"[flet_app3] geocode_dropoff exception: {e}")
            toast(f"Geocoding failed: {e}", Colors.RED_400)

    # Wire geocoding to location text field changes
    r_pick.on_change = geocode_pickup
    r_drop.on_change = geocode_dropoff

    # Controls for map preview and trip details
    r_map_image = ft.Image(width=700, height=350, fit=ft.ImageFit.CONTAIN, visible=False)
    r_eta_text = ft.Text("", size=14, color=Colors.BLUE_700, weight="bold")
    r_distance_text = ft.Text("", size=14, color=Colors.BLUE_700, weight="bold")
    r_map_container = ft.Container(
        content=r_map_image,
        border=ft.border.all(1, "lightgray"),
        border_radius=8,
        padding=8,
        visible=False,
    )
    r_trip_details = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(Icons.SCHEDULE, color=Colors.BLUE_700),
                ft.Text("ETA:", weight="bold"),
                r_eta_text,
            ], spacing=12),
            ft.Row([
                ft.Icon(Icons.ROUTE, color=Colors.BLUE_700),
                ft.Text("Distance:", weight="bold"),
                r_distance_text,
            ], spacing=12),
            ft.Divider(height=1),
            ft.Text("Route Map", size=12, weight="bold", color=Colors.BLUE_600),
            r_map_container,
        ], spacing=8),
        bgcolor=Colors.BLUE_50,
        padding=12,
        border_radius=8,
        visible=False,
    )

    def check_locations(_=None):
        """Manually check and geocode both pickup and dropoff locations, then fetch map and ETA"""
        print("[flet_app3] check_locations called")
        geocode_pickup()
        geocode_dropoff()
        
        # After geocoding, fetch map and ETA/distance
        try:
            plat_val = float(r_plat.value) if r_plat.value.strip() else None
            plng_val = float(r_plng.value) if r_plng.value.strip() else None
            dlat_val = float(r_dlat.value) if r_dlat.value.strip() else None
            dlng_val = float(r_dlng.value) if r_dlng.value.strip() else None
            
            if not (plat_val and plng_val and dlat_val and dlng_val):
                toast("Please ensure all coordinates are valid", Colors.RED_400)
                return
            
            # Fetch ETA and distance first
            eta_val = None
            dist_val = None
            try:
                print(f"[flet_app3] fetching ETA/distance")
                eta_resp = requests.get(
                    f"{api.base}/analytics/eta",
                    params={
                        "origin_lat": plat_val,
                        "origin_lng": plng_val,
                        "dest_lat": dlat_val,
                        "dest_lng": dlng_val,
                    },
                    timeout=6.0
                )
                print(f"[flet_app3] ETA response status: {eta_resp.status_code}")
                if eta_resp.status_code == 200:
                    eta_data = eta_resp.json()
                    eta_val = eta_data.get("duration_min")
                    dist_val = eta_data.get("distance_km")
                    
                    if eta_val is not None:
                        r_eta_text.value = f"{eta_val} min"
                        print(f"[flet_app3] Set ETA: {eta_val} min")
                    if dist_val is not None:
                        r_distance_text.value = f"{dist_val:.2f} km"
                        print(f"[flet_app3] Set distance: {dist_val:.2f} km")
                    
                    print(f"[flet_app3] fetched ETA: {eta_val}, Distance: {dist_val}")
                else:
                    print(f"[flet_app3] ETA response failed with status: {eta_resp.status_code}")
            except Exception as e:
                print(f"[flet_app3] Failed to fetch ETA/distance: {e}")
                import traceback
                traceback.print_exc()
            
            # Fetch static map
            try:
                print(f"[flet_app3] fetching static map: {plat_val}, {plng_val} -> {dlat_val}, {dlng_val}")
                map_resp = requests.get(
                    f"{api.base}/ride-requests/static-map",
                    params={
                        "pickup_lat": plat_val,
                        "pickup_lng": plng_val,
                        "dropoff_lat": dlat_val,
                        "dropoff_lng": dlng_val,
                    },
                    timeout=6.0
                )
                print(f"[flet_app3] Static map response status: {map_resp.status_code}")
                print(f"[flet_app3] Static map response body: {map_resp.text}")
                
                map_url = None
                if map_resp.status_code == 200:
                    try:
                        map_data = map_resp.json()
                        map_url = map_data.get("url")
                        print(f"[flet_app3] Extracted map_url from JSON: {map_url}")
                    except Exception as json_err:
                        print(f"[flet_app3] Failed to parse map response as JSON: {json_err}")
                        # Try treating response as direct URL
                        if map_resp.text:
                            map_url = map_resp.text.strip()
                            print(f"[flet_app3] Using response text as URL: {map_url}")
                
                if map_url:
                    r_map_image.src = map_url
                    print(f"[flet_app3] Set r_map_image.src to: {map_url}")
                    r_map_image.visible = True
                    print(f"[flet_app3] Set r_map_image.visible = True")
                    r_map_container.visible = True
                    print(f"[flet_app3] Set r_map_container.visible = True")
                else:
                    print(f"[flet_app3] No map_url found in response")
            except Exception as e:
                print(f"[flet_app3] Failed to fetch static map: {e}")
                import traceback
                traceback.print_exc()
            
            # Make trip details visible if we have any data
            if eta_val is not None or dist_val is not None:
                r_trip_details.visible = True
                print(f"[flet_app3] Set r_trip_details.visible = True (has ETA/distance data)")
            
            page.update()
            print(f"[flet_app3] page.update() called")
            toast("Route preview loaded \u2713", Colors.GREEN_400)
        except ValueError:
            toast("Coordinates must be numeric", Colors.RED_400)
        except Exception as e:
            print(f"[flet_app3] check_locations exception: {e}")
            toast(f"Failed to load preview: {e}", Colors.RED_400)

    def do_request_ride(_):
        print("[flet_app3] do_request_ride called")
        if not r_user_id.value or not r_pick.value or not r_drop.value:
            toast("User ID, Pickup, and Drop-off are required.", Colors.RED_400)
            return
        try:
            uid = int(r_user_id.value)
            plat = float(r_plat.value); plng = float(r_plng.value)
            dlat = float(r_dlat.value)
            dlng = float(r_dlng.value)
        except ValueError:
            toast("User ID must be int; pickup/dropoff lat/lng must be numeric.", Colors.RED_400)
            return
        try:
            print(f"[flet_app3] creating ride for user {uid}")
            res = api.create_ride(uid, r_pick.value, r_drop.value, plat, plng, dlat, dlng)
            print(f"[flet_app3] create_ride response: {res}")
            res = dict(res) if isinstance(res, dict) else res
            
            # Store ride details for the ride details view
            put_session("ride_details", res)
            
            # Check if driver is assigned
            driver_id = res.get("driver_id")
            if driver_id:
                # Driver assigned - show ride details with driver info
                page.go("/ride/details")
            else:
                # No driver assigned - show apology message
                page.go("/ride/no-driver")
        except Exception as e:
            print(f"[flet_app3] create_ride exception: {e}")
            # Store error and show apology message
            put_session("ride_error", str(e))
            page.go("/ride/no-driver")

    def ride_new_view():
        # Auto-fill user ID from logged-in session
        current_user = get_session("current_user")
        if current_user:
            user_id_val = current_user.get("user_id") or current_user.get("id") or ""
            r_user_id.value = str(user_id_val) if user_id_val else ""
        
        return ft.View(
            route="/ride/new",
            controls=[
                ft.Text("Request Ride", size=22, weight="bold"),
                ft.Row([r_user_id, r_pick, r_drop], spacing=10),
                ft.Row([r_plat, r_plng, r_dlat, r_dlng], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Check Location", on_click=check_locations),
                    ft.ElevatedButton("Submit", on_click=do_request_ride),
                    ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/")),
                ], spacing=10),
                ft.Divider(),
                ft.Text("Route Preview", size=16, weight="bold", color=Colors.BLUE_700),
                r_trip_details,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Admin Analytics ----------------
    def admin_view():
        # fetch analytics from backend (use api.base)
        try:
            r1 = requests.get(f"{api.base}/analytics/rides-per-day")
            r1.raise_for_status()
            rides = r1.json()
        except Exception as e:
            rides = []
            toast(f"Failed to load rides-per-day: {e}", Colors.RED_400)

        try:
            r2 = requests.get(f"{api.base}/analytics/avg-wait-time")
            r2.raise_for_status()
            avg = r2.json().get("avg_wait_min")
        except Exception as e:
            avg = None
            toast(f"Failed to load avg-wait-time: {e}", Colors.RED_400)

        # Build a simple horizontal bar chart (text + colored bar)
        rows = []
        max_count = max((item.get("count", 0) for item in rides), default=0)
        for item in rides:
            date = item.get("date")
            count = item.get("count", 0)
            bar_width = int((count / max_count) * 400) if max_count else 0
            rows.append(
                ft.Row([
                    ft.Text(date, width=110),
                    ft.Container(width=bar_width, height=28, bgcolor=Colors.BLUE_400),
                    ft.Text(str(count), width=50),
                ], spacing=8)
            )

        avg_text = "" if avg is None else f"{avg} min"

        # tables for users and drivers (populated by buttons)
        users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("User ID")),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Phone")),
                ft.DataColumn(ft.Text("Priority")),
            ],
            rows=[],
            width=1000,
        )

        drivers_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Driver ID")),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Phone")),
                ft.DataColumn(ft.Text("Vehicle")),
                ft.DataColumn(ft.Text("Plate")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[],
            width=1000,
        )

        def refresh_users(e=None):
            try:
                data = api.list_users()
                items = data if isinstance(data, list) else data.get("items", [])
                users_table.rows = []
                for u in items:
                    users_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(u.get("user_id") or u.get("id") or ""))),
                            ft.DataCell(ft.Text(str(u.get("name") or ""))),
                            ft.DataCell(ft.Text(str(u.get("email") or ""))),
                            ft.DataCell(ft.Text(str(u.get("phone") or ""))),
                            ft.DataCell(ft.Text(str(u.get("priority_level") or u.get("priority") or ""))),
                        ])
                    )
                page.update()
                toast(f"Loaded {len(users_table.rows)} users \u2713")
            except Exception as e:
                toast(f"Failed to load users: {e}", Colors.RED_400)

        def refresh_drivers(e=None):
            try:
                data = api.list_drivers()
                items = data if isinstance(data, list) else data.get("items", [])
                drivers_table.rows = []
                for d in items:
                    drivers_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(d.get("driver_id") or d.get("id") or ""))),
                            ft.DataCell(ft.Text(str(d.get("name") or ""))),
                            ft.DataCell(ft.Text(str(d.get("phone") or ""))),
                            ft.DataCell(ft.Text(str(d.get("vehicle_type") or ""))),
                            ft.DataCell(ft.Text(str(d.get("plate_number") or ""))),
                            ft.DataCell(ft.Text(str(d.get("availability_status") or ""))),
                        ])
                    )
                page.update()
                toast(f"Loaded {len(drivers_table.rows)} drivers \u2713")
            except Exception as e:
                toast(f"Failed to load drivers: {e}", Colors.RED_400)

        # Rides table
        rides_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ride ID")),
                ft.DataColumn(ft.Text("User ID")),
                ft.DataColumn(ft.Text("Driver ID")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Pickup")),
                ft.DataColumn(ft.Text("Dropoff")),
                ft.DataColumn(ft.Text("Scheduled Time")),
            ],
            rows=[],
            width=1200,
        )

        # Filter controls
        filter_type = ft.Dropdown(
            label="Filter by Type",
            value="all",
            options=[
                ft.dropdown.Option("all", "All (Rides, Users, Drivers)"),
                ft.dropdown.Option("rides", "Rides"),
                ft.dropdown.Option("users", "Users"),
                ft.dropdown.Option("drivers", "Drivers"),
            ],
            width=300,
        )
        search_field = ft.TextField(label="Search (ID, Name, Email, Phone)", width=400)

        def refresh_all_data(e=None):
            search_term = search_field.value.strip().lower()
            selected_filter = filter_type.value
            
            # Load and display rides
            if selected_filter in ["all", "rides"]:
                try:
                    data = requests.get(f"{api.base}/ride-requests/").json()
                    items = data if isinstance(data, list) else data.get("items", [])
                    rides_table.rows = []
                    for r in items:
                        # Filter by search term
                        if search_term:
                            ride_id_str = str(r.get("ride_id") or r.get("id") or "")
                            user_id_str = str(r.get("user_id") or "")
                            driver_id_str = str(r.get("driver_id") or "")
                            status_str = str(r.get("status") or "")
                            if not any(search_term in s.lower() for s in [ride_id_str, user_id_str, driver_id_str, status_str]):
                                continue
                        
                        rides_table.rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(r.get("ride_id") or r.get("id") or ""))),
                                ft.DataCell(ft.Text(str(r.get("user_id") or ""))),
                                ft.DataCell(ft.Text(str(r.get("driver_id") or "N/A"))),
                                ft.DataCell(ft.Text(str(r.get("status") or ""))),
                                ft.DataCell(ft.Text(str(r.get("pickup_location") or ""))),
                                ft.DataCell(ft.Text(str(r.get("dropoff_location") or ""))),
                                ft.DataCell(ft.Text(str(r.get("scheduled_time") or ""))),
                            ])
                        )
                except Exception as e:
                    toast(f"Failed to load rides: {e}", Colors.RED_400)

            # Load and display users
            if selected_filter in ["all", "users"]:
                try:
                    data = api.list_users()
                    items = data if isinstance(data, list) else data.get("items", [])
                    users_table.rows = []
                    for u in items:
                        # Filter by search term
                        if search_term:
                            user_id_str = str(u.get("user_id") or u.get("id") or "")
                            name_str = str(u.get("name") or "").lower()
                            email_str = str(u.get("email") or "").lower()
                            phone_str = str(u.get("phone") or "").lower()
                            if not any(search_term in s for s in [user_id_str.lower(), name_str, email_str, phone_str]):
                                continue
                        
                        users_table.rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(u.get("user_id") or u.get("id") or ""))),
                                ft.DataCell(ft.Text(str(u.get("name") or ""))),
                                ft.DataCell(ft.Text(str(u.get("email") or ""))),
                                ft.DataCell(ft.Text(str(u.get("phone") or ""))),
                                ft.DataCell(ft.Text(str(u.get("priority_level") or u.get("priority") or ""))),
                            ])
                        )
                except Exception as e:
                    toast(f"Failed to load users: {e}", Colors.RED_400)

            # Load and display drivers
            if selected_filter in ["all", "drivers"]:
                try:
                    data = api.list_drivers()
                    items = data if isinstance(data, list) else data.get("items", [])
                    drivers_table.rows = []
                    for d in items:
                        # Filter by search term
                        if search_term:
                            driver_id_str = str(d.get("driver_id") or d.get("id") or "")
                            name_str = str(d.get("name") or "").lower()
                            phone_str = str(d.get("phone") or "").lower()
                            vehicle_str = str(d.get("vehicle_type") or "").lower()
                            if not any(search_term in s for s in [driver_id_str.lower(), name_str, phone_str, vehicle_str]):
                                continue
                        
                        drivers_table.rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(str(d.get("driver_id") or d.get("id") or ""))),
                                ft.DataCell(ft.Text(str(d.get("name") or ""))),
                                ft.DataCell(ft.Text(str(d.get("phone") or ""))),
                                ft.DataCell(ft.Text(str(d.get("vehicle_type") or ""))),
                                ft.DataCell(ft.Text(str(d.get("plate_number") or ""))),
                                ft.DataCell(ft.Text(str(d.get("availability_status") or ""))),
                            ])
                        )
                except Exception as e:
                    toast(f"Failed to load drivers: {e}", Colors.RED_400)

            page.update()
            toast(f"Data refreshed \u2713")

        return ft.View(
            route="/admin",
            controls=[
                ft.Text("Admin Dashboard", size=24, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
                    ft.ElevatedButton("Logout", on_click=lambda e: do_logout()),
                ], spacing=12),
                ft.Divider(),
                
                # Analytics section
                ft.Text("📊 Analytics", size=20, weight="bold", color=Colors.BLUE_700),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Average Wait Time", size=14, weight="bold"),
                            ft.Text(avg_text if avg_text else "N/A", size=24, weight="bold", color=Colors.BLUE_700),
                            ft.Text("minutes", size=12, color="gray"),
                        ]),
                        bgcolor=Colors.BLUE_100,
                        padding=16,
                        border_radius=8,
                        width=250,
                    ),
                ]),
                ft.Text("Rides Per Day", size=16, weight="bold"),
                ft.Container(
                    content=ft.Column(rows, spacing=6) if rows else ft.Text("No data available", color="gray"),
                    border=ft.border.all(1, "lightgray"),
                    border_radius=8,
                    padding=12,
                ),
                ft.Divider(),
                
                # Filter and Search section
                ft.Text("🔍 Search & Filter", size=20, weight="bold", color=Colors.BLUE_700),
                ft.Row([
                    filter_type,
                    search_field,
                    ft.ElevatedButton("Search", on_click=refresh_all_data),
                ], spacing=12, wrap=True),
                ft.Divider(),
                
                # Data tables section
                ft.Text("Rides", size=18, weight="bold"),
                ft.Container(
                    content=ft.Column([rides_table], scroll=ft.ScrollMode.AUTO),
                    height=300,
                    border=ft.border.all(1, "lightgray"),
                    border_radius=8,
                ),
                ft.Divider(),
                
                ft.Text("Users", size=18, weight="bold"),
                ft.Container(
                    content=ft.Column([users_table], scroll=ft.ScrollMode.AUTO),
                    height=300,
                    border=ft.border.all(1, "lightgray"),
                    border_radius=8,
                ),
                ft.Divider(),
                
                ft.Text("Drivers", size=18, weight="bold"),
                ft.Container(
                    content=ft.Column([drivers_table], scroll=ft.ScrollMode.AUTO),
                    height=300,
                    border=ft.border.all(1, "lightgray"),
                    border_radius=8,
                ),
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton("Refresh All Data", on_click=refresh_all_data),
                    ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
                ], spacing=12),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Register Driver ----------------
    d_name = ft.TextField(label="Driver Name", width=240)
    d_phone = ft.TextField(label="Phone", width=180)
    d_vehicle = ft.TextField(label="Vehicle Type", width=160)
    d_plate = ft.TextField(label="Plate Number", width=160)
    d_location = ft.TextField(label="Current Location (auto-fill lat/lng)", width=300)
    d_lat = ft.TextField(label="Initial Lat (optional)", width=150)
    d_lng = ft.TextField(label="Initial Lng (optional)", width=150)

    def geocode_driver_location(_=None):
        """Geocode driver location and auto-fill lat/lng"""
        if not d_location.value.strip():
            return
        try:
            print(f"[flet_app3] geocoding driver location: {d_location.value}")
            resp = requests.get(f"{api.base}/ride-requests/geocode", params={"address": d_location.value})
            resp.raise_for_status()
            data = resp.json()
            lat, lng = data.get("lat"), data.get("lng")
            if lat and lng:
                d_lat.value = str(lat)
                d_lng.value = str(lng)
                page.update()
                print(f"[flet_app3] geocoded driver location: {lat}, {lng}")
            else:
                toast("Location not found", Colors.RED_400)
        except Exception as e:
            print(f"[flet_app3] geocode_driver_location exception: {e}")
            toast(f"Geocoding failed: {e}", Colors.RED_400)

    d_location.on_change = geocode_driver_location

    def do_register_driver(_):
        print("[flet_app3] do_register_driver called")
        if not d_name.value or not d_vehicle.value or not d_plate.value:
            toast("Name, Vehicle, Plate are required.", Colors.RED_400)
            return
        try:
            la = float(d_lat.value) if d_lat.value.strip() else None
            ln = float(d_lng.value) if d_lng.value.strip() else None
        except ValueError:
            toast("Initial lat/lng must be numeric.", Colors.RED_400)
            return
        try:
            print(f"[flet_app3] creating driver: {d_name.value}, plate={d_plate.value}, lat={la}, lng={ln}")
            res = api.create_driver(d_name.value, d_phone.value, d_vehicle.value, d_plate.value, la, ln)
            print(f"[flet_app3] create_driver response: {res}")
            put_session("last_action", "register_driver")
            put_session("last_payload", {"name": d_name.value, "phone": d_phone.value, "vehicle": d_vehicle.value, "plate": d_plate.value, "lat": la, "lng": ln})
            # store response and auto-login the new driver into session
            put_session("last_response", res)
            put_session("current_user", res)
            toast(f"Registered and logged in as driver: {res.get('name')} \u2713")
            page.go("/driver/dashboard")
        except Exception as e:
            print(f"[flet_app3] create_driver exception: {e}")
            toast(f"Register driver failed: {e}", Colors.RED_400)

    def driver_new_view():
        return ft.View(
            route="/driver/new",
            controls=[
                ft.Text("Register Driver", size=22, weight="bold"),
                ft.Row([d_name, d_phone, d_vehicle, d_plate], spacing=10),
                ft.Row([d_location], spacing=10),
                ft.Row([d_lat, d_lng], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Submit", on_click=do_register_driver),
                    ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/")),
                ], spacing=10),
            ],
        )

    # ---------------- Driver Dashboard ----------------
    def driver_dashboard_view():
        current_driver = get_session("current_user")
        driver_name = current_driver.get("name") if current_driver else "Unknown"
        driver_id = current_driver.get("driver_id") if current_driver else None
        vehicle = current_driver.get("vehicle_type") if current_driver else "N/A"
        plate = current_driver.get("plate_number") if current_driver else "N/A"
        # use mutable object to track status changes
        status_holder = {"value": current_driver.get("availability_status") if current_driver else "unknown"}
        
        # Text control for live status update
        status_text = ft.Text(f"Status: {status_holder['value']}", size=14, weight="bold", 
                             color=Colors.GREEN_700 if status_holder['value'] == "available" else Colors.ORANGE_700)
        
        # Table for assigned rides
        assigned_rides_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ride ID")),
                ft.DataColumn(ft.Text("User ID")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Pickup")),
                ft.DataColumn(ft.Text("Dropoff")),
                ft.DataColumn(ft.Text("ETA (min)")),
                ft.DataColumn(ft.Text("Dist (km)")),
                ft.DataColumn(ft.Text("Scheduled Time")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[],
            width=1300,
        )
        
        def load_assigned_rides(e=None):
            try:
                if not driver_id:
                    toast("Driver ID not found in session.", Colors.RED_400)
                    return
                    
                # Fetch rides assigned to this driver
                data = requests.get(f"{api.base}/ride-requests/", params={"driver_id": driver_id}).json()
                items = data if isinstance(data, list) else data.get("items", [])
                assigned_rides_table.rows = []
                
                for r in items:
                    # attempt to get ETA/distance from backend analytics endpoint if coords available
                    eta_val = None
                    dist_val = None
                    try:
                        plat = r.get("pickup_lat") or r.get("pickupLat") or r.get("pickup_latitude")
                        plng = r.get("pickup_lng") or r.get("pickupLng") or r.get("pickup_longitude")
                        dlat = r.get("dropoff_lat") or r.get("dropoffLat") or r.get("dropoff_latitude")
                        dlng = r.get("dropoff_lng") or r.get("dropoffLng") or r.get("dropoff_longitude")
                        if plat and plng and dlat and dlng:
                            q = {"origin_lat": plat, "origin_lng": plng, "dest_lat": dlat, "dest_lng": dlng}
                            eta_resp = requests.get(f"{api.base}/analytics/eta", params=q, timeout=6.0)
                            if eta_resp.status_code == 200:
                                eta_json = eta_resp.json()
                                eta_val = eta_json.get("duration_min")
                                dist_val = eta_json.get("distance_km")
                    except Exception:
                        # ignore ETA errors; we'll still show the ride
                        pass

                    ride_id_val = r.get("ride_id") or r.get("id") or None
                    # action buttons (Drop Off) for non-completed rides
                    actions_row = ft.Row()
                    try:
                        if r.get("status") != "completed":
                            def make_dropoff_cb(rid):
                                def cb(ev=None):
                                    try:
                                        resp = requests.patch(f"{api.base}/ride-requests/{rid}/complete")
                                        if resp.status_code == 200:
                                            toast("Passenger dropped off; driver set to available", Colors.GREEN_400)
                                            # refresh driver in session
                                            try:
                                                drv = api.get_driver(driver_id)
                                                put_session("current_user", drv)
                                            except Exception:
                                                pass
                                            load_assigned_rides()
                                        else:
                                            toast(f"Drop off failed: {resp.status_code}", Colors.RED_400)
                                    except Exception as e:
                                        toast(f"Drop off failed: {e}", Colors.RED_400)
                                return cb
                            actions_row.controls.append(ft.ElevatedButton("Drop Off", on_click=make_dropoff_cb(ride_id_val)))
                    except Exception:
                        pass

                    assigned_rides_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(ride_id_val or ""))),
                            ft.DataCell(ft.Text(str(r.get("user_id") or ""))),
                            ft.DataCell(ft.Text(str(r.get("status") or ""))),
                            ft.DataCell(ft.Text(str(r.get("pickup_location") or ""))),
                            ft.DataCell(ft.Text(str(r.get("dropoff_location") or ""))),
                            ft.DataCell(ft.Text("" if eta_val is None else f"{eta_val}")),
                            ft.DataCell(ft.Text("" if dist_val is None else f"{dist_val}")),
                            ft.DataCell(ft.Text(str(r.get("scheduled_time") or ""))),
                            ft.DataCell(actions_row),
                        ])
                    )
                
                page.update()
                if len(assigned_rides_table.rows) > 0:
                    toast(f"Loaded {len(assigned_rides_table.rows)} assigned rides \u2713")
                else:
                    toast("No assigned rides at this time.")
            except Exception as e:
                print(f"[flet_app3] load_assigned_rides exception: {e}")
                toast(f"Failed to load assigned rides: {e}", Colors.RED_400)

        # helper to change driver availability
        def set_availability(new_status):
            try:
                if not driver_id:
                    toast("Driver ID not found in session.", Colors.RED_400)
                    return
                res = api.set_driver_status(driver_id, new_status)
                put_session("current_user", res)
                # update local status holder and text
                status_holder["value"] = new_status
                status_text.value = f"Status: {new_status}"
                status_text.color = Colors.GREEN_700 if new_status == "available" else Colors.ORANGE_700
                page.update()
                toast(f"Driver status set to {new_status}", Colors.GREEN_400)
            except Exception as e:
                toast(f"Set availability failed: {e}", Colors.RED_400)

        # helper to drop off current ride (find first non-completed ride for this driver)
        def do_drop_current():
            try:
                data = requests.get(f"{api.base}/ride-requests/", params={"driver_id": driver_id}).json()
                items = data if isinstance(data, list) else data.get("items", [])
                ride_to_complete = next((x for x in items if x.get("status") != "completed"), None)
                if not ride_to_complete:
                    toast("No current ride to drop off", Colors.RED_400)
                    return
                rid = ride_to_complete.get("ride_id") or ride_to_complete.get("id")
                resp = requests.patch(f"{api.base}/ride-requests/{rid}/complete")
                if resp.status_code == 200:
                    toast("Passenger dropped off; driver available", Colors.GREEN_400)
                    # Update status to available
                    status_holder["value"] = "available"
                    status_text.value = "Status: available"
                    status_text.color = Colors.GREEN_700
                    try:
                        drv = api.get_driver(driver_id)
                        put_session("current_user", drv)
                    except Exception:
                        pass
                    page.update()
                    load_assigned_rides()
                else:
                    toast(f"Drop off failed: {resp.status_code}", Colors.RED_400)
            except Exception as e:
                toast(f"Drop off failed: {e}", Colors.RED_400)
        
        # Auto-load assigned rides when the view is created
        # Call the loader directly so it populates the table before the view is shown
        try:
            load_assigned_rides()
        except Exception as _:
            # swallow; load_assigned_rides will show a toast on failure
            pass
        # Dynamic button row that updates based on status
        def get_status_buttons():
            buttons = [status_text]
            # Show availability toggle only when not on a ride
            if status_holder["value"] == "available":
                buttons.append(ft.ElevatedButton("Set Unavailable", on_click=lambda e: set_availability("inactive")))
            elif status_holder["value"] == "inactive":
                buttons.append(ft.ElevatedButton("Set Available", on_click=lambda e: set_availability("available")))
            # Show drop-off button only when on a ride
            if status_holder["value"] == "on_ride":
                buttons.append(ft.ElevatedButton("Drop Off Current Ride", on_click=lambda e: do_drop_current()))
            return buttons
        
        status_button_row = ft.Row(get_status_buttons(), spacing=12)
        
        # Function to build current ride section
        def build_current_ride_section():
            """Build the current ride display section if driver is on a ride"""
            controls = []
            
            # Only show current ride section if driver is on_ride
            if status_holder["value"] == "on_ride":
                try:
                    # Fetch current ride (first non-completed ride)
                    data = requests.get(f"{api.base}/ride-requests/", params={"driver_id": driver_id}).json()
                    items = data if isinstance(data, list) else data.get("items", [])
                    current_ride = next((x for x in items if x.get("status") != "completed"), None)
                    
                    if current_ride:
                        ride_id = current_ride.get("ride_id") or current_ride.get("id")
                        user_id = current_ride.get("user_id")
                        status = current_ride.get("status")
                        pickup = current_ride.get("pickup_location")
                        dropoff = current_ride.get("dropoff_location")
                        eta = current_ride.get("estimated_duration")
                        distance = current_ride.get("estimated_distance")
                        scheduled_time = current_ride.get("scheduled_time")
                        static_map_url = current_ride.get("static_map_url")
                        
                        # Fetch user details
                        user_info = None
                        try:
                            user_info = api.get_user(user_id)
                        except Exception as e:
                            print(f"[flet_app3] Failed to fetch user details: {e}")
                        
                        # Build controls list
                        ride_controls = [
                            ft.Divider(),
                            ft.Text("🎯 Current Ride", size=20, weight="bold", color=Colors.BLUE_700),
                        ]
                        
                        # Static map if available
                        if static_map_url:
                            ride_controls.append(
                                ft.Container(
                                    content=ft.Image(
                                        src=static_map_url,
                                        width=700,
                                        height=350,
                                        fit=ft.ImageFit.CONTAIN,
                                    ),
                                    border=ft.border.all(1, "lightgray"),
                                    border_radius=8,
                                    padding=8,
                                )
                            )
                        
                        # Ride details
                        ride_details = [
                            ft.Text("Ride Details", size=16, weight="bold", color=Colors.BLUE_600),
                            ft.Row([
                                ft.Text("Ride ID:", weight="bold", width=120),
                                ft.Text(str(ride_id), size=14),
                            ]),
                            ft.Row([
                                ft.Text("Pickup:", weight="bold", width=120),
                                ft.Text(pickup, size=14),
                            ]),
                            ft.Row([
                                ft.Text("Dropoff:", weight="bold", width=120),
                                ft.Text(dropoff, size=14),
                            ]),
                            ft.Row([
                                ft.Text("ETA:", weight="bold", width=120),
                                ft.Text(f"{eta} min" if eta else "Calculating...", size=14, color=Colors.BLUE_700),
                            ]),
                            ft.Row([
                                ft.Text("Distance:", weight="bold", width=120),
                                ft.Text(f"{distance:.2f} km" if distance else "Calculating...", size=14, color=Colors.BLUE_700),
                            ]),
                            ft.Row([
                                ft.Text("Scheduled:", weight="bold", width=120),
                                ft.Text(str(scheduled_time) if scheduled_time else "N/A", size=14),
                            ]),
                        ]
                        
                        ride_controls.append(
                            ft.Container(
                                content=ft.Column(ride_details, spacing=8),
                                bgcolor=Colors.BLUE_50,
                                padding=12,
                                border_radius=8,
                            )
                        )
                        
                        # Passenger details
                        if user_info:
                            passenger_controls = [
                                ft.Text("Passenger Details", size=16, weight="bold", color=Colors.AMBER_700),
                                ft.Row([
                                    ft.Text("Name:", weight="bold", width=120),
                                    ft.Text(user_info.get("name", "Unknown"), size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Phone:", weight="bold", width=120),
                                    ft.Text(user_info.get("phone", "N/A"), size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Email:", weight="bold", width=120),
                                    ft.Text(user_info.get("email", "N/A"), size=14),
                                ]),
                                ft.Row([
                                    ft.Text("Priority:", weight="bold", width=120),
                                    ft.Text(str(user_info.get("priority_level", user_info.get("priority", "N/A"))), size=14),
                                ]),
                            ]
                            
                            ride_controls.append(
                                ft.Container(
                                    content=ft.Column(passenger_controls, spacing=8),
                                    bgcolor=Colors.AMBER_50,
                                    padding=12,
                                    border_radius=8,
                                )
                            )
                        
                        # Drop off button
                        ride_controls.append(
                            ft.Row([
                                ft.ElevatedButton(
                                    "Complete Ride & Drop Off",
                                    on_click=lambda e: do_drop_current(),
                                    color=Colors.WHITE,
                                    bgcolor=Colors.GREEN_700,
                                    icon=Icons.CHECK,
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        )
                        
                        controls.extend(ride_controls)
                except Exception as e:
                    print(f"[flet_app3] Failed to build current ride section: {e}")
            
            return controls
        
        # Get current ride controls
        current_ride_controls = build_current_ride_section()
        
        return ft.View(
            route="/driver/dashboard",
            controls=[
                ft.Text("Driver Dashboard", size=22, weight="bold"),
                ft.Divider(),
                ft.Text(f"Driver: {driver_name}", size=16, weight="bold"),
                ft.Text(f"Driver ID: {driver_id}"),
                ft.Text(f"Vehicle: {vehicle} ({plate})"),
                status_button_row,
            ] + current_ride_controls + [
                ft.Divider(),
                ft.Text("Assigned Rides", size=18, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("Refresh Rides", on_click=load_assigned_rides),
                ], spacing=10),
                ft.Container(
                    content=ft.Column([assigned_rides_table], scroll=ft.ScrollMode.AUTO),
                    height=350,
                    border=ft.border.all(1, "lightgray"),
                    border_radius=8,
                ),
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
                ], spacing=10),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- User: My Rides ----------------
    mr_user_id = ft.TextField(label="User ID", width=140)
    rides_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Ride ID")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Driver ID")),
            ft.DataColumn(ft.Text("Pickup")),
            ft.DataColumn(ft.Text("Drop-off")),
            ft.DataColumn(ft.Text("ETA (min)")),
            ft.DataColumn(ft.Text("Dist (km)")),
        ],
        rows=[],
        width=1000,
    )

    def do_list_rides(_=None):
        try:
            uid = int(mr_user_id.value)
        except ValueError:
            toast("User ID must be an integer.", Colors.RED_400); return
        try:
            data = api.list_rides(uid)
            items = data if isinstance(data, list) else data.get("items", [])
            rides_table.rows = []
            for r in items:
                eta = r.get("estimated_duration")
                dist = r.get("estimated_distance")
                rides_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(r.get("ride_id")))),
                        ft.DataCell(ft.Text(str(r.get("status")))),
                        ft.DataCell(ft.Text(str(r.get("driver_id")))),
                        ft.DataCell(ft.Text(str(r.get("pickup_location")))),
                        ft.DataCell(ft.Text(str(r.get("dropoff_location")))),
                        ft.DataCell(ft.Text("" if eta is None else f"{eta}")),
                        ft.DataCell(ft.Text("" if dist is None else f"{dist:.2f}")),
                    ])
                )
            page.update()
            toast(f"Loaded {len(rides_table.rows)} rides \u2713")
        except Exception as e:
            print(f"[flet_app3] do_list_rides exception: {e}")
            toast(f"List rides failed: {e}", Colors.RED_400)

    def my_rides_view():
        # Auto-fill user ID from logged-in session and auto-load rides
        current_user = get_session("current_user")
        print(f"[flet_app3] my_rides_view() current_user={current_user}")
        if current_user:
            user_id_val = current_user.get("user_id") or current_user.get("id") or ""
            mr_user_id.value = str(user_id_val) if user_id_val else ""
            print(f"[flet_app3] my_rides_view() set mr_user_id.value={mr_user_id.value}")
            # Auto-load rides for this user
            if mr_user_id.value:
                print(f"[flet_app3] my_rides_view() calling do_list_rides()")
                do_list_rides()
        
        return ft.View(
            route="/user/rides",
            controls=[
                ft.Text("My Rides", size=22, weight="bold"),
                ft.Row([mr_user_id, ft.ElevatedButton("Refresh", on_click=do_list_rides)], spacing=10),
                rides_table,
                ft.Row([ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/"))]),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Confirm Screen (shows last action) ----------------
    # If backend returns a 'static_map_url', we show it.
    static_img = ft.Image(width=600, height=340, fit=ft.ImageFit.CONTAIN, visible=False)

    def confirm_view():
        action = get_session("last_action", "\u2014")
        payload = get_session("last_payload", {})
        response = get_session("last_response", {})

        # handle optional static map url from backend
        url = response.get("static_map_url")
        if url:
            static_img.src = url
            static_img.visible = True
        else:
            static_img.visible = False

        # Determine success/failure from the response
        resp_success = False
        resp_error = None
        try:
            if isinstance(response, dict) and response.get("success") is not None:
                resp_success = bool(response.get("success"))
            else:
                # heuristic: presence of any resource ID (user_id, ride_id, driver_id) or assigned status implies success
                resp_success = bool(response.get("user_id") or response.get("ride_id") or response.get("driver_id") or response.get("status") == "assigned")
        except Exception:
            resp_success = False
        if isinstance(response, dict) and response.get("error"):
            resp_error = response.get("error")

        return ft.View(
            route="/confirm",
            controls=[
                ft.Text("Action Completed", size=22, weight="bold"),
                ft.Text(f"Action: {action}", size=16),
                (ft.Row([ft.Icon(Icons.CHECK_CIRCLE, color=Colors.GREEN_400), ft.Text("Succeeded", color=Colors.GREEN_700, weight="bold")]) if resp_success else ft.Row([ft.Icon(Icons.ERROR, color=Colors.RED_400), ft.Text("Failed", color=Colors.RED_700, weight="bold")]) ),
                ft.Text("Submitted:", size=16, weight="bold"),
                ft.Container(content=ft.Text(json.dumps(payload, indent=2), selectable=True),
                             bgcolor=Colors.GREY_100, padding=10, width=800),
                ft.Text("Response:", size=16, weight="bold"),
                ft.Container(content=ft.Text(json.dumps(response, indent=2), selectable=True),
                             bgcolor=Colors.GREY_100, padding=10, width=800),
                static_img,
                (ft.Text(f"Error: {resp_error}", color=Colors.RED_400, weight="bold") if resp_error else ft.Column([])),
                ft.Row([
                    ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
                    ft.ElevatedButton("Go to Login", on_click=lambda e: page.go("/login/choose")),
                ]),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Ride Details (Driver Assigned) ----------------
    def ride_details_view():
        ride = get_session("ride_details", {})
        ride_id = ride.get("ride_id") or ride.get("id")
        driver_id = ride.get("driver_id")
        user_id = ride.get("user_id")
        status = ride.get("status")
        pickup = ride.get("pickup_location")
        dropoff = ride.get("dropoff_location")
        scheduled_time = ride.get("scheduled_time")
        eta = ride.get("estimated_duration")
        distance = ride.get("estimated_distance")
        static_map_url = ride.get("static_map_url")
        
        # Fetch driver details
        driver_info = None
        if driver_id:
            try:
                driver_info = api.get_driver(driver_id)
            except Exception as e:
                print(f"[flet_app3] Failed to fetch driver details: {e}")
        
        # Build driver info section
        driver_section = []
        if driver_info:
            driver_name = driver_info.get("name", "Unknown")
            driver_phone = driver_info.get("phone", "N/A")
            vehicle_type = driver_info.get("vehicle_type", "N/A")
            plate_number = driver_info.get("plate_number", "N/A")
            
            driver_section = [
                ft.Divider(),
                ft.Text("Driver Details", size=18, weight="bold", color=Colors.BLUE_700),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Name:", weight="bold", width=100),
                            ft.Text(driver_name, size=14),
                        ]),
                        ft.Row([
                            ft.Text("Phone:", weight="bold", width=100),
                            ft.Text(driver_phone, size=14),
                        ]),
                        ft.Row([
                            ft.Text("Vehicle:", weight="bold", width=100),
                            ft.Text(f"{vehicle_type} ({plate_number})", size=14),
                        ]),
                    ], spacing=8),
                    bgcolor=Colors.BLUE_50,
                    padding=16,
                    border_radius=8,
                ),
            ]
        
        # Build ride info section
        ride_info_section = [
            ft.Divider(),
            ft.Text("Ride Information", size=18, weight="bold", color=Colors.GREEN_700),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Ride ID:", weight="bold", width=120),
                        ft.Text(str(ride_id), size=14),
                    ]),
                    ft.Row([
                        ft.Text("Status:", weight="bold", width=120),
                        ft.Text(status, size=14, color=Colors.GREEN_700 if status == "assigned" else Colors.ORANGE_700),
                    ]),
                    ft.Row([
                        ft.Text("Pickup:", weight="bold", width=120),
                        ft.Text(pickup, size=14),
                    ]),
                    ft.Row([
                        ft.Text("Dropoff:", weight="bold", width=120),
                        ft.Text(dropoff, size=14),
                    ]),
                    ft.Row([
                        ft.Text("ETA:", weight="bold", width=120),
                        ft.Text(f"{eta} min" if eta else "Calculating...", size=14, color=Colors.BLUE_700),
                    ]),
                    ft.Row([
                        ft.Text("Distance:", weight="bold", width=120),
                        ft.Text(f"{distance:.2f} km" if distance else "Calculating...", size=14, color=Colors.BLUE_700),
                    ]),
                    ft.Row([
                        ft.Text("Scheduled:", weight="bold", width=120),
                        ft.Text(str(scheduled_time) if scheduled_time else "N/A", size=14),
                    ]),
                ], spacing=8),
                bgcolor=Colors.GREEN_50,
                padding=16,
                border_radius=8,
            ),
        ]
        
        # Build map section
        map_section = []
        if static_map_url:
            map_section = [
                ft.Divider(),
                ft.Text("Route Map", size=18, weight="bold", color=Colors.AMBER_700),
                ft.Image(
                    src=static_map_url,
                    width=700,
                    height=400,
                    fit=ft.ImageFit.CONTAIN,
                ),
            ]
        
        # Combine all sections
        controls = [
            ft.Text("Your Ride is Ready! 🎉", size=24, weight="bold", color=Colors.GREEN_700),
            ft.Text("A driver has been assigned to your ride.", size=14, italic=True),
        ]
        controls.extend(driver_section)
        controls.extend(ride_info_section)
        controls.extend(map_section)
        controls.extend([
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("View My Rides", on_click=lambda e: page.go("/user/rides")),
                ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
            ], spacing=12),
        ])
        
        return ft.View(
            route="/ride/details",
            controls=controls,
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- No Driver Available ----------------
    def ride_no_driver_view():
        error = get_session("ride_error", "")
        
        controls = [
            ft.Icon(Icons.ERROR_OUTLINE, size=80, color=Colors.ORANGE_700),
            ft.Text("No Driver Available", size=28, weight="bold", color=Colors.ORANGE_700),
            ft.Divider(),
            ft.Text(
                "We apologize, but there are currently no available drivers in your area. "
                "Please try again in a few moments or contact support for assistance.",
                size=14,
                text_align=ft.TextAlign.CENTER,
            ),
        ]
        
        if error:
            controls.extend([
                ft.Divider(),
                ft.Text("Error Details:", size=12, weight="bold"),
                ft.Container(
                    content=ft.Text(error, selectable=True, size=11),
                    bgcolor=Colors.GREY_100,
                    padding=12,
                    border_radius=6,
                ),
            ])
        
        controls.extend([
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("Request Another Ride", on_click=lambda e: page.go("/ride/new")),
                ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
            ], spacing=12),
        ])
        
        return ft.View(
            route="/ride/no-driver",
            controls=controls,
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Router ----------------
    def route_change(route: ft.RouteChangeEvent):
        print(f"[flet_app3] route_change fired; page.route={page.route}")
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view())
        elif page.route == "/user/new":
            page.views.append(user_new_view())
        elif page.route == "/ride/new":
            page.views.append(ride_new_view())
        elif page.route == "/ride/details":
            page.views.append(ride_details_view())
        elif page.route == "/ride/no-driver":
            page.views.append(ride_no_driver_view())
        elif page.route == "/driver/new":
            page.views.append(driver_new_view())
        elif page.route == "/driver/dashboard":
            page.views.append(driver_dashboard_view())
        elif page.route == "/user/rides":
            page.views.append(my_rides_view())
        elif page.route == "/admin":
            page.views.append(admin_view())
        elif page.route == "/confirm":
            page.views.append(confirm_view())
        elif page.route == "/login":
            page.views.append(login_view())
        elif page.route == "/register":
            page.views.append(register_view())
        elif page.route == "/login/choose":
            page.views.append(login_choose_view())
        elif page.route == "/register/choose":
            page.views.append(register_choose_view())
        elif page.route == "/login/user":
            page.views.append(login_view())
        elif page.route == "/login/driver":
            page.views.append(driver_login_view())
        elif page.route == "/login/admin":
            page.views.append(admin_login_view())
        elif page.route == "/register/user":
            page.views.append(user_new_view())
        elif page.route == "/register/driver":
            page.views.append(driver_new_view())
        else:
            page.views.append(home_view())
        print(f"[flet_app3] appended view for route {page.route}; total views={len(page.views)}")
        page.update()

    def view_pop(view: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route if page.views else "/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")  # start at home

ft.app(target=main)
