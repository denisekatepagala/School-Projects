import json
from pathlib import Path

from PIL import Image


DATASET_DIR = Path("ocr_dataset")


def check_split(name):

    split_dir = DATASET_DIR / name
    annotations_file = split_dir / "annotations.jsonl"
    images_dir = split_dir / "images"

    print()
    print(f"===== {name.upper()} =====")

    records = []

    with annotations_file.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    print(f"Annotations: {len(records)}")

    missing = 0
    invalid = 0

    for record in records:

        filename = Path(record["image"]).name
        image_path = images_dir / filename

        if not image_path.exists():
            missing += 1
            continue

        try:
            with Image.open(image_path) as image:
                image.verify()
        except Exception:
            invalid += 1

    print(f"Missing images: {missing}")
    print(f"Invalid images: {invalid}")

    if records:
        first = records[0]

        print()
        print("Example:")
        print("Image:", first["image"])
        print("Text:", first["text"])


def main():

    print()
    print("===================================")
    print("CHECKING OCR DATASET")
    print("===================================")

    check_split("train")
    check_split("validation")

    print()
    print("===================================")
    print("CHECK COMPLETE")
    print("===================================")


if __name__ == "__main__":
    main()