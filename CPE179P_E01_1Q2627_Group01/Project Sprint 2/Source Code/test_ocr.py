from pathlib import Path

from PIL import Image
from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel,
)


MODEL_NAME = "microsoft/trocr-small-printed"

IMAGE_PATH = Path(
    "ocr_dataset/train/images/en_00000001.jpg"
)


print()
print("===================================")
print("LOADING TROCR")
print("===================================")

processor = TrOCRProcessor.from_pretrained(
    MODEL_NAME
)

model = VisionEncoderDecoderModel.from_pretrained(
    MODEL_NAME
)

print("Model loaded successfully!")

print()
print("===================================")
print("TESTING IMAGE")
print("===================================")

image = Image.open(
    IMAGE_PATH
).convert("RGB")

pixel_values = processor(
    images=image,
    return_tensors="pt"
).pixel_values

generated_ids = model.generate(
    pixel_values
)

recognized_text = processor.batch_decode(
    generated_ids,
    skip_special_tokens=True
)[0]

print()
print("Image:")
print(IMAGE_PATH)

print()
print("OCR Result:")
print(recognized_text)

print()
print("===================================")
print("TEST COMPLETE")
print("===================================")