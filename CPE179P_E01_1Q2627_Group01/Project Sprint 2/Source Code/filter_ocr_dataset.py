import json
import re
import shutil
from pathlib import Path


DATASET_DIR = Path("../dataset")
CROPS_DIR = DATASET_DIR / "crops"
RECOGNIZER_FILE = DATASET_DIR / "recognizer.jsonl"

VOCABULARY_FILE = Path("vocabulary.txt")

OUTPUT_DIR = Path("ocr_dataset")
OUTPUT_IMAGES = OUTPUT_DIR / "images"
OUTPUT_ANNOTATIONS = OUTPUT_DIR / "annotations.jsonl"


def extract_words(text):
    return re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text.lower()
    )


def load_vocabulary():

    vocabulary = set()

    with VOCABULARY_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            word = line.strip().lower()

            if word:
                vocabulary.add(word)

    return vocabulary


def main():

    print()
    print("===================================")
    print("FILTERING OCR DATASET")
    print("===================================")

    vocabulary = load_vocabulary()

    print(
        f"Vocabulary loaded: {len(vocabulary)} words"
    )

    if len(vocabulary) != 100:

        print(
            "ERROR: vocabulary.txt does not contain exactly 100 words."
        )
        return

    if not CROPS_DIR.exists():

        print(
            f"ERROR: Crops folder not found:\n{CROPS_DIR}"
        )
        return

    if not RECOGNIZER_FILE.exists():

        print(
            f"ERROR: recognizer.jsonl not found:\n{RECOGNIZER_FILE}"
        )
        return

    # Create output folders
    OUTPUT_IMAGES.mkdir(
        parents=True,
        exist_ok=True
    )

    valid_samples = 0
    rejected_samples = 0
    missing_images = 0

    with RECOGNIZER_FILE.open(
        "r",
        encoding="utf-8"
    ) as input_file:

        with OUTPUT_ANNOTATIONS.open(
            "w",
            encoding="utf-8"
        ) as output_file:

            for line_number, line in enumerate(
                input_file,
                start=1
            ):

                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)

                except json.JSONDecodeError:

                    print(
                        f"Warning: invalid JSON on line {line_number}"
                    )

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
                    continue

                words = extract_words(text)

                # Check whether every word belongs
                # to the 100-word vocabulary.
                if not all(
                    word in vocabulary
                    for word in words
                ):

                    rejected_samples += 1
                    continue

                filename = Path(
                    image_path
                ).name

                source_image = CROPS_DIR / filename

                if not source_image.exists():

                    missing_images += 1
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

                valid_samples += 1

    print()
    print("===================================")
    print("FILTERING COMPLETE")
    print("===================================")

    print(
        f"Valid samples:       {valid_samples}"
    )

    print(
        f"Rejected samples:    {rejected_samples}"
    )

    print(
        f"Missing images:      {missing_images}"
    )

    print()
    print(
        f"Output folder:       {OUTPUT_DIR}"
    )

    print(
        f"Images folder:       {OUTPUT_IMAGES}"
    )

    print(
        f"Annotations:         {OUTPUT_ANNOTATIONS}"
    )


if __name__ == "__main__":
    main()