import flet as ft
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def main(page: ft.Page):
    page.title = "Accessible Transportation Scheduler"
    page.theme_mode = "light"
    page.window_width = 900
    page.window_height = 600

    def placeholder_action(action_name):
        print(f"Placeholder: {action_name} (DB logic not yet implemented)")

    def user_view():
        return ft.Column([
            ft.Text("User Dashboard", size=22, weight="bold"),
            ft.TextField(label="Name"),
            ft.TextField(label="Contact Number"),
            ft.TextField(label="Email"),
            ft.TextField(label="Pickup Location"),
            ft.TextField(label="Drop-off Location"),
            ft.ElevatedButton("Request Ride", on_click=lambda e: placeholder_action("Request Ride")),
            ft.ElevatedButton("View My Rides", on_click=lambda e: placeholder_action("View Rides")),
            ft.ElevatedButton("Back to Main Dashboard", on_click=lambda e: show_main_dashboard())
        ])

    def driver_view():
        driver_id_field = ft.TextField(label="Driver ID", value="1")
        rides_column = ft.Column()
        
        def load_assigned_rides(e):
            try:
                driver_id = int(driver_id_field.value)
                response = requests.get(f"{API_BASE_URL}/rides/", params={"driver_id": driver_id})
                
                if response.status_code == 200:
                    rides = response.json()
                    rides_column.controls.clear()
                    
                    if not rides:
                        rides_column.controls.append(
                            ft.Text("No assigned rides", size=14, color="gray")
                        )
                    else:
                        for ride in rides:
                            ride_card = ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Ride #{ride['id']}", weight="bold"),
                                    ft.Text(f"Status: {ride['status']}", size=12),
                                    ft.Text(f"User ID: {ride['user_id']}", size=12),
                                    ft.Text(f"Pickup: {ride['pickup_location']}", size=12),
                                    ft.Text(f"Dropoff: {ride['dropoff_location']}", size=12),
                                    ft.Text(f"Scheduled: {ride['scheduled_time']}", size=12),
                                    ft.Text(f"Fare: ${ride.get('fare', 'N/A')}", size=12, weight="bold"),
                                ]),
                                border=ft.border.all(1, "lightgray"),
                                border_radius=8,
                                padding=12,
                                margin=ft.margin.symmetric(vertical=5)
                            )
                            rides_column.controls.append(ride_card)
                    
                    page.update()
                else:
                    rides_column.controls.clear()
                    rides_column.controls.append(
                        ft.Text(f"Error loading rides: {response.status_code}", color="red")
                    )
                    page.update()
            except Exception as ex:
                rides_column.controls.clear()
                rides_column.controls.append(
                    ft.Text(f"Error: {str(ex)}", color="red")
                )
                page.update()
        
        return ft.Column([
            ft.Text("Driver Dashboard", size=22, weight="bold"),
            ft.Divider(),
            ft.Text("Driver Information", size=16, weight="bold"),
            ft.TextField(label="Driver Name"),
            ft.TextField(label="Vehicle Type"),
            ft.TextField(label="Plate Number"),
            ft.ElevatedButton("Register Driver", on_click=lambda e: placeholder_action("Register Driver")),
            ft.Divider(),
            ft.Text("Assigned Rides", size=16, weight="bold"),
            driver_id_field,
            ft.ElevatedButton("Load Assigned Rides", on_click=load_assigned_rides),
            ft.Container(
                content=ft.ListView([rides_column], expand=True),
                height=300,
                border=ft.border.all(1, "lightgray"),
                border_radius=8
            ),
            ft.ElevatedButton("Back to Main Dashboard", on_click=lambda e: show_main_dashboard())
        ], scroll="auto")

    def admin_view():
        return ft.Column([
            ft.Text("Administrator Dashboard", size=22, weight="bold"),
            ft.ElevatedButton("Generate Reports", on_click=lambda e: placeholder_action("Generate Reports")),
            ft.ElevatedButton("View Ride Logs", on_click=lambda e: placeholder_action("View Ride Logs")),
            ft.ElevatedButton("Back to Main Dashboard", on_click=lambda e: show_main_dashboard())
        ])

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