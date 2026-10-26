import json
import random
import shutil
from pathlib import Path


DATASET_DIR = Path("ocr_dataset")
IMAGES_DIR = DATASET_DIR / "images"
ANNOTATIONS_FILE = DATASET_DIR / "annotations.jsonl"

TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "validation"

TRAIN_IMAGES = TRAIN_DIR / "images"
VAL_IMAGES = VAL_DIR / "images"

TRAIN_ANNOTATIONS = TRAIN_DIR / "annotations.jsonl"
VAL_ANNOTATIONS = VAL_DIR / "annotations.jsonl"

TRAIN_RATIO = 0.80

RANDOM_SEED = 42


def main():

    print()
    print("===================================")
    print("SPLITTING OCR DATASET")
    print("===================================")

    records = []

    with ANNOTATIONS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            record = json.loads(line)
            records.append(record)

    print(f"Total samples: {len(records)}")

    random.seed(RANDOM_SEED)
    random.shuffle(records)

    train_count = int(
        len(records) * TRAIN_RATIO
    )

    train_records = records[:train_count]
    val_records = records[train_count:]

    TRAIN_IMAGES.mkdir(
        parents=True,
        exist_ok=True
    )

    VAL_IMAGES.mkdir(
        parents=True,
        exist_ok=True
    )

    with TRAIN_ANNOTATIONS.open(
        "w",
        encoding="utf-8"
    ) as file:

        for record in train_records:

            filename = Path(
                record["image"]
            ).name

            source = IMAGES_DIR / filename
            destination = TRAIN_IMAGES / filename

            shutil.copy2(
                source,
                destination
            )

            output_record = {
                "image": f"images/{filename}",
                "text": record["text"]
            }

            file.write(
                json.dumps(
                    output_record,
                    ensure_ascii=False
                ) + "\n"
            )

    with VAL_ANNOTATIONS.open(
        "w",
        encoding="utf-8"
    ) as file:

        for record in val_records:

            filename = Path(
                record["image"]
            ).name

            source = IMAGES_DIR / filename
            destination = VAL_IMAGES / filename

            shutil.copy2(
                source,
                destination
            )

            output_record = {
                "image": f"images/{filename}",
                "text": record["text"]
            }

            file.write(
                json.dumps(
                    output_record,
                    ensure_ascii=False
                ) + "\n"
            )

    print()
    print("===================================")
    print("SPLIT COMPLETE")
    print("===================================")

    print(
        f"Training samples:   {len(train_records)}"
    )

    print(
        f"Validation samples: {len(val_records)}"
    )

    print()
    print("Training folder:")
    print(TRAIN_DIR)

    print()
    print("Validation folder:")
    print(VAL_DIR)


if __name__ == "__main__":
    main()