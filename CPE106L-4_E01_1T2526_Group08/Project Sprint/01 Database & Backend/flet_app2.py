import json
from typing import Optional
import requests
import flet as ft
from flet import Colors

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

    def list_rides(self, user_id: Optional[int] = None):
        url = f"{self.base}/ride-requests/"
        if user_id is not None:
            url += f"?user_id={user_id}"
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
    page.title = "Accessible Transportation Scheduler"
    page.window_width = 1060
    page.window_height = 720
    page.padding = 16
    page.theme_mode = "light"

    # shared
    api_base_tf = ft.TextField(label="API Base URL", value=DEFAULT_API_BASE, width=420)
    api = Api(api_base_tf.value)

    def set_api(_=None):
        nonlocal api
        api = Api(api_base_tf.value.strip())
        toast(f"API set to: {api_base_tf.value}")

    def toast(msg: str, color=Colors.GREEN_400):
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
        return ft.View(
            route="/",
            controls=[
                ft.Text("Accessible Transportation Scheduler", size=28, weight="bold"),
                ft.Divider(),
                ft.Row([api_base_tf, ft.ElevatedButton("Use API URL", on_click=set_api)], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Login", width=200, height=60, on_click=lambda e: page.go("/login/choose")),
                    ft.ElevatedButton("Register", width=200, height=60, on_click=lambda e: page.go("/register/choose")),
                ], alignment="center", spacing=40),
                ft.Divider(),
                ft.Text("(After login you can access dashboards and admin analytics)", italic=True, size=12),
            ],
            alignment="center",
            horizontal_alignment="center",
        )

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
        if not u_name.value or not u_email.value:
            toast("Name and Email are required.", Colors.RED_400); return
        try:
            pr = int(u_prio.value.strip() or "0")
        except ValueError:
            toast("Priority must be an integer.", Colors.RED_400); return
        try:
            res = api.create_user(u_name.value, u_email.value, u_phone.value, pr)
            put_session("last_action", "create_user")
            put_session("last_payload", {"name": u_name.value, "email": u_email.value, "phone": u_phone.value, "priority": pr})
            put_session("last_response", res)
            page.go("/confirm")
        except Exception as e:
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
            toast(f"Logged in as {res.get('name')} ✓")
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
    r_dlat = ft.TextField(label="Drop-off Lat (optional)", width=180)
    r_dlng = ft.TextField(label="Drop-off Lng (optional)", width=180)

    def do_request_ride(_):
        if not r_user_id.value or not r_pick.value or not r_drop.value:
            toast("User ID, Pickup, and Drop-off are required.", Colors.RED_400); return
        try:
            uid = int(r_user_id.value)
            plat = float(r_plat.value); plng = float(r_plng.value)
            dlat = float(r_dlat.value) if r_dlat.value.strip() else None
            dlng = float(r_dlng.value) if r_dlng.value.strip() else None
        except ValueError:
            toast("User ID must be int; lat/lng must be numeric.", Colors.RED_400); return
        try:
            res = api.create_ride(uid, r_pick.value, r_drop.value, plat, plng, dlat, dlng)
            put_session("last_action", "request_ride")
            put_session("last_payload", {
                "user_id": uid, "pickup": r_pick.value, "dropoff": r_drop.value,
                "pickup_lat": plat, "pickup_lng": plng, "dropoff_lat": dlat, "dropoff_lng": dlng
            })
            put_session("last_response", res)
            page.go("/confirm")
        except Exception as e:
            toast(f"Ride request failed: {e}", Colors.RED_400)

    def ride_new_view():
        return ft.View(
            route="/ride/new",
            controls=[
                ft.Text("Request Ride", size=22, weight="bold"),
                ft.Row([r_user_id, r_pick, r_drop], spacing=10),
                ft.Row([r_plat, r_plng, r_dlat, r_dlng], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Submit", on_click=do_request_ride),
                    ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/")),
                ], spacing=10),
            ],
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

        avg_text = "—" if avg is None else f"{avg} min"

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
                toast(f"Loaded {len(users_table.rows)} users ✓")
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
                toast(f"Loaded {len(drivers_table.rows)} drivers ✓")
            except Exception as e:
                toast(f"Failed to load drivers: {e}", Colors.RED_400)

        return ft.View(
            route="/admin",
            controls=[
                ft.Text("Admin Analytics", size=22, weight="bold"),
                ft.Text(f"Average wait time: {avg_text}", size=16),
                ft.Divider(),
                ft.Text("Rides per day", size=18, weight="bold"),
                ft.Column(rows, spacing=6),
                ft.Divider(),
                ft.Text("User / Driver Details", size=18, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("Load Users", on_click=refresh_users),
                    ft.ElevatedButton("Load Drivers", on_click=refresh_drivers),
                    ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/")),
                ], spacing=12),
                ft.Divider(),
                ft.Text("Users", weight="bold"),
                users_table,
                ft.Divider(),
                ft.Text("Drivers", weight="bold"),
                drivers_table,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Register Driver ----------------
    d_name = ft.TextField(label="Driver Name", width=240)
    d_phone = ft.TextField(label="Phone", width=180)
    d_vehicle = ft.TextField(label="Vehicle Type", width=160)
    d_plate = ft.TextField(label="Plate Number", width=160)
    d_lat = ft.TextField(label="Initial Lat (optional)", width=150)
    d_lng = ft.TextField(label="Initial Lng (optional)", width=150)

    def do_register_driver(_):
        if not d_name.value or not d_vehicle.value or not d_plate.value:
            toast("Name, Vehicle, Plate are required.", Colors.RED_400); return
        try:
            la = float(d_lat.value) if d_lat.value.strip() else None
            ln = float(d_lng.value) if d_lng.value.strip() else None
        except ValueError:
            toast("Initial lat/lng must be numeric.", Colors.RED_400); return
        try:
            res = api.create_driver(d_name.value, d_phone.value, d_vehicle.value, d_plate.value, la, ln)
            put_session("last_action", "register_driver")
            put_session("last_payload", {"name": d_name.value, "phone": d_phone.value, "vehicle": d_vehicle.value, "plate": d_plate.value, "lat": la, "lng": ln})
            put_session("last_response", res)
            page.go("/confirm")
        except Exception as e:
            toast(f"Register driver failed: {e}", Colors.RED_400)

    def driver_new_view():
        return ft.View(
            route="/driver/new",
            controls=[
                ft.Text("Register Driver", size=22, weight="bold"),
                ft.Row([d_name, d_phone, d_vehicle, d_plate], spacing=10),
                ft.Row([d_lat, d_lng], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Submit", on_click=do_register_driver),
                    ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/")),
                ], spacing=10),
            ],
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

    def do_list_rides(_):
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
            toast(f"Loaded {len(rides_table.rows)} rides ✓")
        except Exception as e:
            toast(f"List rides failed: {e}", Colors.RED_400)

    def my_rides_view():
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
        action = get_session("last_action", "—")
        payload = get_session("last_payload", {})
        response = get_session("last_response", {})

        # handle optional static map url from backend
        url = response.get("static_map_url")
        if url:
            static_img.src = url
            static_img.visible = True
        else:
            static_img.visible = False

        return ft.View(
            route="/confirm",
            controls=[
                ft.Text("Action Completed", size=22, weight="bold"),
                ft.Text(f"Action: {action}", size=16),
                ft.Text("Submitted:", size=16, weight="bold"),
                ft.Container(content=ft.Text(json.dumps(payload, indent=2), selectable=True),
                             bgcolor=Colors.GREY_100, padding=10, width=800),
                ft.Text("Response:", size=16, weight="bold"),
                ft.Container(content=ft.Text(json.dumps(response, indent=2), selectable=True),
                             bgcolor=Colors.GREY_100, padding=10, width=800),
                static_img,
                ft.Row([ft.ElevatedButton("Back to Home", on_click=lambda e: page.go("/"))]),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    # ---------------- Router ----------------
    def route_change(route: ft.RouteChangeEvent):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view())
        elif page.route == "/user/new":
            page.views.append(user_new_view())
        elif page.route == "/ride/new":
            page.views.append(ride_new_view())
        elif page.route == "/driver/new":
            page.views.append(driver_new_view())
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
            page.views.append(login_view())
        elif page.route == "/login/admin":
            page.views.append(login_view())
        elif page.route == "/register/user":
            page.views.append(user_new_view())
        elif page.route == "/register/driver":
            page.views.append(driver_new_view())
        else:
            page.views.append(home_view())
        page.update()

    def view_pop(view: ft.ViewPopEvent):
        page.views.pop()
        page.go(page.views[-1].route if page.views else "/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")  # start at home

ft.app(target=main)
