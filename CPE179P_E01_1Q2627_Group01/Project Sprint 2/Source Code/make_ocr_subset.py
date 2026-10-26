import json
from pathlib import Path

# =========================
# FOLDER SETTINGS
# =========================

DATASET_DIR = Path("../dataset")

CROPS_DIR = DATASET_DIR / "crops"

DETECTOR_FILE = DATASET_DIR / "detector.jsonl"

RECOGNIZER_FILE = DATASET_DIR / "recognizer.jsonl"


def main():

    print("===================================")
    print("Creating recognizer.jsonl")
    print("===================================")

    if not CROPS_DIR.exists():
        print(f"ERROR: Crops folder not found:")
        print(CROPS_DIR)
        return

    if not DETECTOR_FILE.exists():
        print(f"ERROR: detector.jsonl not found:")
        print(DETECTOR_FILE)
        return

    # Get the filenames of the 300 images we actually downloaded.
    crop_files = {
        file.name
        for file in CROPS_DIR.iterdir()
        if file.suffix.lower() in [".jpg", ".jpeg", ".png"]
    }

    print(f"Crop images found: {len(crop_files)}")

    if len(crop_files) == 0:
        print("ERROR: No crop images found.")
        return

    matched = 0

    with DETECTOR_FILE.open(
        "r",
        encoding="utf-8"
    ) as detector:

        with RECOGNIZER_FILE.open(
            "w",
            encoding="utf-8"
        ) as recognizer:

            for line in detector:

                record = json.loads(line)

                image_path = record.get("image", "")

                # Example:
                # images/en_00000001.jpg
                filename = Path(image_path).name

                # Only process images that actually exist
                # in our 300-image crops folder.
                if filename not in crop_files:
                    continue

                items = record.get("items", [])

                if not items:
                    continue

                text = items[0].get("text", "").strip()

                if not text:
                    continue

                output_record = {
                    "image": f"crops/{filename}",
                    "text": text
                }

                recognizer.write(
                    json.dumps(
                        output_record,
                        ensure_ascii=False
                    ) + "\n"
                )

                matched += 1

                print(
                    f"[{matched}] {filename} -> {text}"
                )

    print()
    print("===================================")
    print("DONE")
    print("===================================")
    print(f"Images found: {len(crop_files)}")
    print(f"Annotations matched: {matched}")
    print()
    print(f"Created:")
    print(RECOGNIZER_FILE)


if __name__ == "__main__":
    main()