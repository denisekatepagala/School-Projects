
import base64
import io
import os
import threading

import cv2
import pytesseract
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from transformers import pipeline

app = FastAPI(title="English to Tagalog OCR Translator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Raspberry Pi Linux Tesseract location
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

MODEL_NAME = "Helsinki-NLP/opus-mt-en-tl"

translator = None
translator_lock = threading.Lock()


def get_translator():
    """Load the translation model only when it is first needed."""
    global translator

    if translator is None:
        with translator_lock:
            if translator is None:
                translator = pipeline(
                    "translation",
                    model=MODEL_NAME,
                )

    return translator


def encode_image(image):
    """Convert an OpenCV image to a Base64 JPEG string."""
    success, buffer = cv2.imencode(".jpg", image)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Could not encode the captured image.",
        )

    return base64.b64encode(buffer.tobytes()).decode("utf-8")


def preprocess_image(image):
    """Prepare an image to improve OCR readability."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enlarge small printed text
    height, width = gray.shape
    if width < 1200:
        scale = 1200 / width
        gray = cv2.resize(
            gray,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_CUBIC,
        )

    # Improve contrast
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    return gray


def extract_text(image):
    """Run Tesseract OCR on an OpenCV image."""
    processed = preprocess_image(image)

    text = pytesseract.image_to_string(
        processed,
        lang="eng",
        config="--psm 6",
    )

    return text.strip()


def translate_text(text):
    """Translate recognized English text into Tagalog."""
    if not text.strip():
        return ""

    model = get_translator()
    result = model(text, max_length=512)

    return result[0]["translation_text"].strip()


def process_image_bytes(image_bytes):
    """Decode image bytes, perform OCR, and translate the text."""
    image_array = __import__("numpy").frombuffer(
        image_bytes,
        dtype=__import__("numpy").uint8,
    )

    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image could not be opened.",
        )

    english_text = extract_text(image)

    if not english_text:
        return {
            "success": False,
            "message": "No readable English text was detected.",
            "extracted_text": "",
            "translated_text": "",
        }

    tagalog_text = translate_text(english_text)

    return {
        "success": True,
        "message": "Translation complete!",
        "extracted_text": english_text,
        "translated_text": tagalog_text,
    }


@app.get("/")
def home():
    return {
        "success": True,
        "message": "English to Tagalog OCR backend is running.",
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "message": "Backend is reachable.",
    }


@app.post("/capture")
def capture_image():
    """Capture one image from the Raspberry Pi USB camera."""
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()
        raise HTTPException(
            status_code=500,
            detail="Cannot open the Raspberry Pi camera. "
                   "Check the USB connection and camera index.",
        )

    try:
        # Allow the camera a moment to initialize
        frame = None

        for _ in range(5):
            success, current_frame = camera.read()
            if success:
                frame = current_frame

        if frame is None:
            raise HTTPException(
                status_code=500,
                detail="The camera opened but could not capture an image.",
            )

        return {
            "success": True,
            "message": "Image captured!",
            "image_base64": encode_image(frame),
        }

    finally:
        camera.release()


@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """Extract English text from an uploaded image."""
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    image = cv2.imdecode(
        __import__("numpy").frombuffer(
            image_bytes,
            dtype=__import__("numpy").uint8,
        ),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a supported image.",
        )

    text = extract_text(image)

    return {
        "success": bool(text),
        "extracted_text": text,
        "message": "OCR complete." if text else "No readable text detected.",
    }


@app.post("/translate")
async def translate_image(file: UploadFile = File(...)):
    """Extract English text and translate it into Tagalog."""
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    try:
        return process_image_bytes(image_bytes)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {exc}",
        )


@app.post("/capture-and-translate")
def capture_and_translate():
    """Optional endpoint to capture and translate in one request."""
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()
        raise HTTPException(
            status_code=500,
            detail="Cannot open the Raspberry Pi camera.",
        )

    try:
        frame = None

        for _ in range(5):
            success, current_frame = camera.read()
            if success:
                frame = current_frame

        if frame is None:
            raise HTTPException(
                status_code=500,
                detail="Could not capture an image.",
            )

        image_base64 = encode_image(frame)
        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Could not encode the captured image.",
            )

        result = process_image_bytes(buffer.tobytes())
        result["image_base64"] = image_base64
        return result

    finally:
        camera.release()
