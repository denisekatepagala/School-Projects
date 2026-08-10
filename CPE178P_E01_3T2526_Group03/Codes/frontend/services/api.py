import requests

BASE_URL = "http://127.0.0.1:8000"


def predict(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/predict",
            files={"file": f},
        )

    response.raise_for_status()

    return response.json()