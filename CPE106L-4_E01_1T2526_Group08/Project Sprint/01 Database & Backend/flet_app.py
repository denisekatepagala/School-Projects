import json
import requests
import flet as ft
from flet import Colors

# ---- Configure your backend base URL here ----
DEFAULT_API_BASE = "http://127.0.0.1:8000"

# --------------- Simple REST client ----------------
class Api:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    def _handle(self, r: requests.Response):
        try:
            r.raise_for_status()
            if r.text:
                return r.json()
            return {}
        except requests.HTTPError as e:
            # Try to surface FastAPI error detail
            try:
                detail = r.json().get("detail")
            except Exception:
                detail = r.text
            raise RuntimeError(f"{r.status_code}: {detail}") from e

    # Users
    def create_user(self, name: str, email: str, phone: str, priority_level: int = 5):
        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "priority_level": priority_level,
        }
        return self._handle(requests.post(f"{self.base}/users/", json=payload))

    # Drivers
    def create_driver(self, name: str, phone: str, vehicle_type: str, plate_number: str):
        payload = {
            "name": name,
            "phone": phone,
            "vehicle_type": vehicle_type,
            "plate_number": plate_number,
            "availability_status": "available",
            # Optional live location; can be updated later
            "current_lat": 14.5649,
            "current_lng": 120.9933,
        }
        return self._handle(requests.post(f"{self.base}/drivers/", json=payload))

    def set_driver_status(self, driver_id: int, status: str):
        return self._handle(requests.patch(f"{self.base}/drivers/{driver_id}/status",
                                           json={"status": status}))

    def set_driver_location(self, driver_id: int, lat: float, lng: float):
        return self._handle(requests.patch(f"{self.base}/drivers/{driver_id}/location",
                                           json={"lat": lat, "lng": lng}))

    # Ride requests
    def create_ride(self,
                    user_id: int,
                    pickup_location: str, dropoff_location: str,
                    pickup_lat: float, pickup_lng: float,
                    dropoff_lat: float | None = None, dropoff_lng: float | None = None):
        payload = {
            "user_id": user_id,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
        }
        if dropoff_lat is not None and dropoff_lng is not None:
            payload["dropoff_lat"] = dropoff_lat
            payload["dropoff_lng"] = dropoff_lng
        return self._handle(requests.post(f"{self.base}/ride-requests/", json=payload))


# --------------- Flet UI ----------------
def main(page: ft.Page):
    page.title = "Accessible Transportation Scheduler"
    page.theme_mode = "light"
    page.window_width = 1000
    page.window_height = 680
    page.padding = 20

    # API client bound to a TextField so teammates can change base URL
    api_base_tf = ft.TextField(label="API Base URL", value=DEFAULT_API_BASE, width=420)
    api = Api(api_base_tf.value)

    def refresh_api(_=None):
        nonlocal api
        api = Api(api_base_tf.value.strip())
        toast(f"API set to {api_base_tf.value}")

    def toast(msg: str, color=Colors.GREEN_400):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # ------------------ USER VIEW ------------------
    user_name = ft.TextField(label="Name", width=300)
    user_phone = ft.TextField(label="Contact Number", width=300)
    user_email = ft.TextField(label="Email", width=300)
    user_priority = ft.TextField(label="Priority (0-5)", value="5", width=150)

    created_user_id = ft.Text(value="—", size=14)

    pickup_loc = ft.TextField(label="Pickup Location", width=400)
    drop_loc = ft.TextField(label="Drop-off Location", width=400)
    pickup_lat = ft.TextField(label="Pickup Lat", value="14.5649", width=190)
    pickup_lng = ft.TextField(label="Pickup Lng", value="120.9933", width=190)
    drop_lat = ft.TextField(label="Drop-off Lat (optional)", width=190)
    drop_lng = ft.TextField(label="Drop-off Lng (optional)", width=190)

    def do_create_user(_):
        try:
            uid = int(user_priority.value) if user_priority.value.strip() else 5
        except ValueError:
            toast("Priority must be an integer.", Colors.RED_400)
            return
        try:
            res = api.create_user(user_name.value, user_email.value, user_phone.value, uid)
            created_user_id.value = str(res.get("user_id"))
            toast("User created ✓")
            page.update()
        except Exception as e:
            toast(f"Create user failed: {e}", Colors.RED_400)

    def do_request_ride(_):
        if created_user_id.value == "—":
            toast("Create/select a user first.", Colors.RED_400)
            return
        try:
            uid = int(created_user_id.value)
            plat = float(pickup_lat.value)
            plng = float(pickup_lng.value)
            dlat = float(drop_lat.value) if drop_lat.value.strip() else None
            dlng = float(drop_lng.value) if drop_lng.value.strip() else None
        except ValueError:
            toast("Lat/Lng must be numbers.", Colors.RED_400)
            return
        try:
            res = api.create_ride(
                user_id=uid,
                pickup_location=pickup_loc.value,
                dropoff_location=drop_loc.value,
                pickup_lat=plat, pickup_lng=plng,
                dropoff_lat=dlat, dropoff_lng=dlng
            )
            dlg = ft.AlertDialog(
                title=ft.Text("Ride Created"),
                content=ft.Text(json.dumps(res, indent=2)),
                actions=[ft.TextButton("OK", on_click=lambda e: page.dialog.close())]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()
        except Exception as e:
            toast(f"Ride request failed: {e}", Colors.RED_400)

    def user_view():
        return ft.Column([
            ft.Text("User Dashboard", size=22, weight="bold"),
            ft.Row([api_base_tf, ft.ElevatedButton("Use API URL", on_click=refresh_api)]),
            ft.Divider(),
            ft.Text("Create User", size=16, weight="bold"),
            ft.Row([user_name, user_phone, user_email, user_priority]),
            ft.Row([ft.ElevatedButton("Create User", on_click=do_create_user),
                    ft.Text("User ID: "), created_user_id]),
            ft.Divider(),
            ft.Text("Request Ride", size=16, weight="bold"),
            ft.Row([pickup_loc, drop_loc]),
            ft.Row([pickup_lat, pickup_lng, drop_lat, drop_lng]),
            ft.Row([ft.ElevatedButton("Request Ride", on_click=do_request_ride),
                    ft.ElevatedButton("Back to Main", on_click=lambda e: show_main_dashboard())]),
        ], spacing=12)

    # ------------------ DRIVER VIEW ------------------
    drv_name = ft.TextField(label="Driver Name", width=240)
    drv_phone = ft.TextField(label="Phone", width=200)
    drv_vehicle = ft.TextField(label="Vehicle Type", width=160)
    drv_plate = ft.TextField(label="Plate Number", width=160)
    drv_created_id = ft.Text("—")

    drv_status = ft.Dropdown(label="Set Status",
                             options=[ft.dropdown.Option("available"),
                                      ft.dropdown.Option("on_ride"),
                                      ft.dropdown.Option("inactive")],
                             value="available",
                             width=180)
    drv_status_id = ft.TextField(label="Driver ID", width=120)

    loc_driver_id = ft.TextField(label="Driver ID", width=120)
    loc_lat = ft.TextField(label="Lat", value="14.5649", width=140)
    loc_lng = ft.TextField(label="Lng", value="120.9933", width=140)

    def do_register_driver(_):
        try:
            res = api.create_driver(drv_name.value, drv_phone.value, drv_vehicle.value, drv_plate.value)
            drv_created_id.value = str(res.get("driver_id"))
            toast("Driver registered ✓")
            page.update()
        except Exception as e:
            toast(f"Register driver failed: {e}", Colors.RED_400)

    def do_set_status(_):
        try:
            did = int(drv_status_id.value)
        except ValueError:
            toast("Driver ID must be an integer.", Colors.RED_400)
            return
        try:
            res = api.set_driver_status(did, drv_status.value)
            toast(f"Status set to {res.get('availability_status')} ✓")
        except Exception as e:
            toast(f"Set status failed: {e}", Colors.RED_400)

    def do_set_location(_):
        try:
            did = int(loc_driver_id.value)
            la = float(loc_lat.value)
            ln = float(loc_lng.value)
        except ValueError:
            toast("Driver ID must be int, lat/lng must be numbers.", Colors.RED_400)
            return
        try:
            api.set_driver_location(did, la, ln)
            toast("Location updated ✓")
        except Exception as e:
            toast(f"Update location failed: {e}", Colors.RED_400)

    def driver_view():
        return ft.Column([
            ft.Text("Driver Dashboard", size=22, weight="bold"),
            ft.Row([api_base_tf, ft.ElevatedButton("Use API URL", on_click=refresh_api)]),
            ft.Divider(),
            ft.Text("Register Driver", size=16, weight="bold"),
            ft.Row([drv_name, drv_phone, drv_vehicle, drv_plate]),
            ft.Row([ft.ElevatedButton("Register Driver", on_click=do_register_driver),
                    ft.Text("Driver ID: "), drv_created_id]),
            ft.Divider(),
            ft.Text("Live Status / Location", size=16, weight="bold"),
            ft.Row([drv_status_id, drv_status, ft.ElevatedButton("Set Status", on_click=do_set_status)]),
            ft.Row([loc_driver_id, loc_lat, loc_lng, ft.ElevatedButton("Set Location", on_click=do_set_location)]),
            ft.Row([ft.ElevatedButton("Back to Main", on_click=lambda e: show_main_dashboard())]),
        ], spacing=12)

    # ------------------ ADMIN VIEW ------------------
    def admin_view():
        return ft.Column([
            ft.Text("Administrator Dashboard", size=22, weight="bold"),
            ft.Row([api_base_tf, ft.ElevatedButton("Use API URL", on_click=refresh_api)]),
            ft.Text("Try analytics endpoints in Swagger for now.", size=12, italic=True),
            ft.ElevatedButton("Back to Main Dashboard", on_click=lambda e: show_main_dashboard()),
        ])

    # ------------------ NAV ------------------
    def show_main_dashboard():
        page.controls.clear()
        page.add(
            ft.Column([
                ft.Text("Accessible Transportation Scheduler", size=24, weight="bold"),
                ft.Text("Select your role:", size=18),
                ft.Row([
                    ft.ElevatedButton("User", on_click=lambda e: switch_view("user")),
                    ft.ElevatedButton("Driver", on_click=lambda e: switch_view("driver")),
                    ft.ElevatedButton("Administrator", on_click=lambda e: switch_view("admin")),
                ], alignment="center")
            ], alignment="center", horizontal_alignment="center", spacing=20)
        )
        page.update()

    def switch_view(role):
        page.controls.clear()
        if role == "user":
            page.add(user_view())
        elif role == "driver":
            page.add(driver_view())
        elif role == "admin":
            page.add(admin_view())
        page.update()

    show_main_dashboard()

ft.app(target=main)
