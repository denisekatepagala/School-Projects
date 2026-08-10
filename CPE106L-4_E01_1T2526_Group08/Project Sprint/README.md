## Accessible Transportation Scheduler

## Project Overview
The **Accessible Transportation Scheduler** is an application designed to assist elderly individuals and persons with accessibility needs in scheduling rides. The system enables users to request rides, drivers to accept requests, and administrators to view ride analytics. The application uses **FastAPI** for the backend, **Flet** for the frontend, and integrates with the **Google Maps API** for location-based services.

## Key Features
- **User Role**: Request a ride and view the status of requested rides.
- **Driver Role**: Accept and view assigned rides.
- **Administrator Role**: View ride logs and generate reports.
- **Google Maps Integration**: Displays static maps showing pickup and drop-off locations.
- **Backend**: Built with **FastAPI**, using **SQLite** for data storage and Google Maps APIs for distance and routing.

## System Architecture
The system is based on a **Model-View-Controller (MVC)** architecture:
- **Presentation Layer**: Built with **Flet** for creating the user interface.
- **Business Logic Layer**: FastAPI handles the backend logic, including ride requests, user management, and ride assignments.
- **Data Access Layer**: SQLite is used for storing user, driver, and ride data, with SQLModel for ORM-based database interaction.

## Requirements

### Prerequisites
- **Python 3.8+**
- A **Google Maps API Key** (for route and map integration).


## 01 Database & Backend | Member Assigned: Denise Pagala

This section serves as the backend server built with FastAPI and SQLite (using SQLModel). This manages Users, Drivers, and Ride Requests for an accessible transport scheduling system.


### Installing Dependencies
Follow these steps to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/denisekatepagala/CPE106L-4_E01_1T2526_Group-8.git
   cd 01_Database_&_Backend

   
2. **Create a virtual environment**: 
    ```bash
   
    python3 -m venv .venv
    source .venv/bin/activate  # For macOS or Linux
    venv\Scripts\activate     # For Windows

3. **Install dependencies**:

    ```bash
    pip install fastapi uvicorn sqlmodel
    # or for full system requirements:
    pip install -r requirements.txt

4. **Create a .env file for environment variables (e.g., Google Maps API Key)**:

    Add your Google Maps API Key and any other necessary configurations to .env.

   ```
   GOOGLE_MAPS_API_KEY=PUT_YOUR_OWN_KEY_HERE
   USE_GOOGLE_MAPS=true
Step 5: Run the FastAPI server

    uvicorn app.main:app --reload
    
This will start the server at http://127.0.0.1:8000.
  
Note: You should see "INFO: Uvicorn running on http:..." If not working, try running it on CMD

Search in Browser: 
    
    http://127.0.0.1:8000/docs

You should see the Swagger UI with all endpoints (/users/, /drivers/, /ride-requests/)

Step 6: Run unit tests (OPTIONAL)

    pip install pytest #Install if pytest not yet installed
  
    pytest test_main.py
#
**-------------------------------------------------------- END FOR 01 Database & Backend -------------------------------------------------------**
#

## 02 Frontend (FLET) | Member Assigned: Ralph Lam

This is a simple Python app built with Flet. It simulates a basic transportation scheduler with three user roles: User, Driver, and Administrator.

- User Dashboard: Request rides and view ride history

- Driver Dashboard: Register drivers and view assigned rides
  
- Administrator Dashboard: Generate reports and view ride logs
#
**1. Setup Guide** 

Step 1. **Install Flet**:

    pip install flet

Step 2. **Run the App**:

    python "Flet_AppFINAL.py" #FINAL VERSION OF UI
    python "Flet_App.py" #GOOGLE API FREE


#
**-------------------------------------------------------- END FOR 02 Frontend (FLET) -------------------------------------------------------**
#

## 03 Algorithm, Analytics, & Integration | Member Assigned: Jm Esperanza

# Overview

The **Algorithm & Analytics** module of the **Accessible Transportation Scheduler** is responsible for implementing the core logic for routing, scheduling, and analytics. This component uses **Dijkstra's Algorithm** for route optimization and provides analytics for administrators. The algorithms are exposed through **FastAPI** endpoints, and the **Google Maps API** is integrated to provide location-based services and distance calculations. The initial frontend built using **Flet** has been connected to these exposed endpoints in the backend to allow users to interact with the system seamlessly.

## Responsibilities
- **Route Optimization**: Implement **Dijkstra’s algorithm** to find the shortest paths for ride requests based on available driver locations and pickup/drop-off points.
- **Ride Request Scheduling**: Ensure that ride requests are assigned to drivers efficiently, considering proximity and availability.
- **Analytics**: Provide statistical insights, such as average wait time, number of rides per day, and driver availability, which will be displayed on the admin dashboard.

## Key Features

1. **Route Optimization with Dijkstra’s Algorithm**:
   - Calculates the shortest path between the pickup and drop-off locations.
   - Uses **Google Maps API** to calculate real-world distances.

2. **Ride Request Scheduling**:
   - Assigns the most suitable driver to a ride request based on proximity and availability.
   - Allows administrators to manage driver assignments manually or automatically.

3. **Analytics**:
   - **Rides per day**: Number of ride requests processed each day.
   - **Average wait time**: Time between a ride request and driver arrival.
   - **Driver performance**: Information on driver availability and assigned rides.

4. **Backend Integration**:
   - The algorithms are exposed as **FastAPI endpoints**.
   - Real-time updates are provided for ride requests, driver status, and analytics.
   - **Google Maps API** is integrated for route calculations and displaying pickup/drop-off locations on static maps.

5. **Frontend Integration**:
   - The **initial Flet frontend** has been modified to interact with the backend and call the exposed endpoints for creating users, drivers, ride requests, and viewing analytics.

## Modifications to the Initial Backend

- **Integrated Route Optimization Algorithm**: Implemented **Dijkstra’s Algorithm** to calculate the shortest path between user pickup and drop-off locations.
- **Google Maps API Integration**: Integrated the **Google Maps API** to calculate distances between locations and display static maps for the users and drivers.
- **Backend Endpoints**: Exposed new endpoints for:
  - Ride request creation (`POST /ride-requests/`)
  - Route optimization (`POST /ride-requests/optimize-route`)
  - Analytics (e.g., rides per day, average wait time)

## API Endpoints for Algorithm & Analytics

### Route Optimization (Dijkstra’s Algorithm)
- **POST `/ride-requests/optimize-route`**: 
  - **Request body**: `{ "pickup_lat": float, "pickup_lng": float, "dropoff_lat": float, "dropoff_lng": float }`
  - **Response**: `{ "optimized_route": "shortest_path", "distance": float, "estimated_duration": int }`

### Ride Request Scheduling
- **POST `/ride-requests/assign-driver`**:
  - **Request body**: `{ "ride_id": int, "driver_id": int }`
  - **Response**: `{ "status": "assigned", "ride_id": int, "driver_id": int }`

### Analytics Endpoints
- **GET `/analytics/rides-per-day`**: 
  - **Response**: `{ "date": "2025-11-11", "count": int }`

- **GET `/analytics/avg-wait-time`**:
  - **Response**: `{ "avg_wait_min": float }`

## Frontend with Flet

The frontend, developed using **Flet**, interacts with the backend through the exposed endpoints. After a user logs in or signs up, they can:

1. **Request a ride** and get the shortest route calculated via the **Dijkstra’s Algorithm**.
2. **View ride requests** that are assigned to them as a driver.
3. **View analytics** as an administrator, such as rides per day and average wait time.

## Troubleshooting: Killing a Port in Use (Windows)

If you encounter a **"port already in use"** error when starting the server on **Windows**, follow these steps to free up the port:

### Step 1: Find the Process Using the Port

1. Open **Command Prompt** as **Administrator**.
2. Run the following command to find the **Process ID (PID)** using the specific port (replace `8000` with your port number if needed):

   ```bash
   netstat -ano | findstr :8000

## Troubleshooting

- **Port already in use**: If you encounter a "port already in use" error, you may need to kill the process that is using the port or run the server on a different port.
  - To kill the process on macOS:
    ```bash
    lsof -i :8000
    kill -9 <PID>
    ```
  - To change the port:
    ```bash
    uvicorn app.main:app --reload --port 8001
    ```
    

- **Missing API Key**: If you're using Google Maps for static maps, make sure you've set up your **Google Maps API Key** in the `.env` file.
- or run the app_flet.py for non Google maps version
#
**-------------------------------------------------------- END FOR 03 Algorithm, Analytics Integration -----------------------------------------**
#
