import json
import re
from collections import Counter
from pathlib import Path


RECOGNIZER_FILE = Path("../dataset/recognizer.jsonl")
VOCABULARY_FILE = Path("vocabulary.txt")

VOCABULARY_SIZE = 100


def extract_words(text):
    return re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text.lower()
    )


def main():

    counter = Counter()

    with RECOGNIZER_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = record.get("text", "").strip()

            if not text:
                continue

            words = extract_words(text)

            counter.update(words)

    top_words = counter.most_common(VOCABULARY_SIZE)

    with VOCABULARY_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        for word, count in top_words:
            file.write(word + "\n")

    print()
    print("===================================")
    print("VOCABULARY CREATED")
    print("===================================")
    print(f"Vocabulary size: {len(top_words)}")
    print(f"Output: {VOCABULARY_FILE}")
    print()
    print("Words:")
    print("-----------------------------------")

    for number, (word, count) in enumerate(
        top_words,
        start=1
    ):
        print(f"{number:3}. {word:<20} {count}")


if __name__ == "__main__":
    main()