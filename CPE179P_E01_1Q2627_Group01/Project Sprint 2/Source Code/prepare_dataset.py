import json
import shutil
from pathlib import Path


DATASET_DIR = Path("../dataset")
CROPS_DIR = DATASET_DIR / "crops"
RECOGNIZER_FILE = DATASET_DIR / "recognizer.jsonl"

OUTPUT_DIR = Path("ocr_dataset")
OUTPUT_IMAGES = OUTPUT_DIR / "images"
OUTPUT_ANNOTATIONS = OUTPUT_DIR / "annotations.jsonl"


def main():

    print()
    print("===================================")
    print("PREPARING OCR DATASET")
    print("===================================")

    OUTPUT_IMAGES.mkdir(
        parents=True,
        exist_ok=True
    )

    copied = 0
    skipped = 0

    with RECOGNIZER_FILE.open(
        "r",
        encoding="utf-8"
    ) as input_file:

        with OUTPUT_ANNOTATIONS.open(
            "w",
            encoding="utf-8"
        ) as output_file:

            for line in input_file:

                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                image_path = record.get(
                    "image",
                    ""
                )

                text = record.get(
                    "text",
                    ""
                ).strip()

                if not image_path or not text:
                    skipped += 1
                    continue

                filename = Path(
                    image_path
                ).name

                source_image = (
                    CROPS_DIR / filename
                )

                if not source_image.exists():
                    print(
                        f"Missing image: {filename}"
                    )
                    skipped += 1
                    continue

                destination_image = (
                    OUTPUT_IMAGES / filename
                )

                shutil.copy2(
                    source_image,
                    destination_image
                )

                output_record = {
                    "image": f"images/{filename}",
                    "text": text
                }

                output_file.write(
                    json.dumps(
                        output_record,
                        ensure_ascii=False
                    ) + "\n"
                )

                copied += 1

    print()
    print("===================================")
    print("DATASET PREPARATION COMPLETE")
    print("===================================")
    print(f"Images copied: {copied}")
    print(f"Samples skipped: {skipped}")
    print()
    print(f"Dataset: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()