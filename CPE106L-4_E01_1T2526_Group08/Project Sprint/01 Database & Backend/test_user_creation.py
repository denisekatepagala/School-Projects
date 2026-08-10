#!/usr/bin/env python3
"""
Quick test to diagnose user creation issues.
Run this after starting the backend to see the exact error.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test 1: Get existing users
print("=" * 60)
print("Test 1: List existing users")
print("=" * 60)
try:
    resp = requests.get(f"{BASE_URL}/users/")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Create a user with the exact payload flet_app3 sends
print("\n" + "=" * 60)
print("Test 2: Create a user (same payload as flet_app3.py)")
print("=" * 60)
payload = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "priority_level": 5
}
print(f"Payload: {json.dumps(payload, indent=2)}")
try:
    resp = requests.post(f"{BASE_URL}/users/", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try with minimal payload
print("\n" + "=" * 60)
print("Test 3: Create a user (minimal payload)")
print("=" * 60)
payload_min = {
    "name": "Minimal User",
    "email": "minimal@example.com"
}
print(f"Payload: {json.dumps(payload_min, indent=2)}")
try:
    resp = requests.post(f"{BASE_URL}/users/", json=payload_min)
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Done. Check the output above for errors.")
print("=" * 60)
