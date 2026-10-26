from pathlib import Path
import re

import cv2
import pytesseract

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)


# ============================================================
# SETTINGS
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\SDD\MAPUA PROJECTS\CPE200-2_Thesis Folder"
    r"\Tesseract\tesseract.exe"
)

IMAGE_PATH = Path(
    r"C:\Users\SDD\MAPUA PROJECTS\CPE179P_E01_1Q2627"
    r"\CPE179P_E01_Final Project"
    r"\project_sprint 2 (Dataset)"
    r"\ocr_dataset\train\images\en_00000001.jpg"
)

TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-tl"


# ============================================================
# LOAD TRANSLATION MODEL
# ============================================================

print()
print("===================================")
print("LOADING TRANSLATION MODEL")
print("===================================")

print("Model:", TRANSLATION_MODEL)
print("Please wait...")

tokenizer = AutoTokenizer.from_pretrained(
    TRANSLATION_MODEL
)

translation_model = AutoModelForSeq2SeqLM.from_pretrained(
    TRANSLATION_MODEL
)

print("Translation model loaded successfully!")


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):

    print()
    print("Preprocessing image...")

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return processed


# ============================================================
# OCR ENGINE
# ============================================================

def ocr_engine(image):

    print()
    print("Running Tesseract OCR...")

    text = pytesseract.image_to_string(
        image,
        config="--psm 12 --oem 3"
    )

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    text = " ".join(lines)

    return text.strip()


# ============================================================
# CLEAN OCR
# ============================================================

def clean_ocr_text(text):

    print()
    print("Cleaning OCR result...")

    # Remove repeated spaces
    text = " ".join(text.split())

    # Fix OCR dash artifacts
    text = text.replace("—~", "-")
    text = text.replace("~—", "-")
    text = text.replace("~~", "-")

    # Normalize dashes
    text = text.replace("—", "-")
    text = text.replace("–", "-")

    # Remove spaces before punctuation
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace(" :", ":")
    text = text.replace(" ;", ";")

    # Remove duplicate punctuation
    text = text.replace("..", ".")
    text = text.replace("::", ":")

    return text.strip()


# ============================================================
# TRANSLATE ONE SENTENCE
# ============================================================

def translate_sentence(text):

    if not text.strip():
        return ""

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    outputs = translation_model.generate(
        **inputs,
        max_length=128,
        num_beams=5
    )

    translated = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return translated.strip()


# ============================================================
# TRANSLATION ENGINE
# ============================================================

def translate_to_tagalog(text):

    print()
    print("Translating English → Tagalog...")

    # --------------------------------------------------------
    # Detect Bible-style references
    # Example:
    # Daniel 7: 12
    # --------------------------------------------------------

    reference_pattern = r"\b[A-Z][a-z]+\s+\d+\s*:\s*\d+\b"

    reference_match = re.search(
        reference_pattern,
        text
    )

    reference = None

    if reference_match:

        reference = reference_match.group(
            0
        ).strip()

        # Remove reference from translation text
        translation_text = text.replace(
            reference,
            ""
        ).strip()

    else:

        translation_text = text

    # --------------------------------------------------------
    # Remove leftover dash before reference
    # --------------------------------------------------------

    translation_text = translation_text.rstrip(
        " -—~"
    ).strip()

    # --------------------------------------------------------
    # Split into sentences
    # --------------------------------------------------------

    sentences = re.split(
        r"(?<=[.!?])\s+",
        translation_text
    )

    translated_sentences = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        translated = translate_sentence(
            sentence
        )

        if translated:
            translated_sentences.append(
                translated
            )

    # --------------------------------------------------------
    # Combine translated sentences
    # --------------------------------------------------------

    result = " ".join(
        translated_sentences
    )

    # --------------------------------------------------------
    # Add reference back
    # --------------------------------------------------------

    if reference:

        if result:
            result += " - " + reference

        else:
            result = reference

    return result


# ============================================================
# MAIN PROGRAM
# ============================================================

print()
print("===================================")
print("ENGLISH → TAGALOG OCR SYSTEM")
print("===================================")


# ============================================================
# CHECK IMAGE
# ============================================================

if not IMAGE_PATH.exists():

    print()
    print("ERROR: Image not found.")
    print()
    print("Image path:")
    print(IMAGE_PATH)

    raise SystemExit


# ============================================================
# LOAD IMAGE
# ============================================================

print()
print("===================================")
print("LOADING IMAGE")
print("===================================")

image = cv2.imread(
    str(IMAGE_PATH)
)

if image is None:

    print("ERROR: Could not read image.")

    raise SystemExit


height, width = image.shape[:2]

print("Image loaded successfully.")
print("Image size:", width, "x", height)


# ============================================================
# PREPROCESS
# ============================================================

processed = preprocess_image(
    image
)


# ============================================================
# SAVE DEBUG IMAGE
# ============================================================

cv2.imwrite(
    "ocr_debug.png",
    processed
)

print()
print("Preprocessed image saved as: ocr_debug.png")


# ============================================================
# OCR
# ============================================================

raw_english_text = ocr_engine(
    processed
)


print()
print("===================================")
print("RAW OCR RESULT")
print("===================================")

print(raw_english_text)


# ============================================================
# CLEAN OCR
# ============================================================

english_text = clean_ocr_text(
    raw_english_text
)


print()
print("===================================")
print("CLEANED OCR RESULT")
print("===================================")

print(english_text)


# ============================================================
# CHECK OCR
# ============================================================

if not english_text:

    print()
    print("No text was detected.")

    raise SystemExit


# ============================================================
# TRANSLATION
# ============================================================

tagalog_text = translate_to_tagalog(
    english_text
)


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("===================================")
print("FINAL RESULT")
print("===================================")

print()
print("English:")
print(english_text)

print()
print("Tagalog:")
print(tagalog_text)

print()
print("===================================")
print("TEST COMPLETE")
print("===================================")
