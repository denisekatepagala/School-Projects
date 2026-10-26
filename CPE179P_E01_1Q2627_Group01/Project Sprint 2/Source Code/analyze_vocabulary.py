import json
import re
from collections import Counter
from pathlib import Path


RECOGNIZER_FILE = Path("../dataset/recognizer.jsonl")


def extract_words(text):
    """
    Extract English words while keeping contractions together.
    Examples:
        don't -> don't
        I'm   -> i'm
        you're -> you're
    """

    return re.findall(
        r"[a-zA-Z]+(?:'[a-zA-Z]+)?",
        text.lower()
    )


def main():

    counter = Counter()
    total_records = 0
    skipped_lines = 0

    with RECOGNIZER_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1
        ):

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError:
                skipped_lines += 1
                continue

            text = record.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            total_records += 1

            words = extract_words(text)

            counter.update(words)

    print()
    print("===================================")
    print("VOCABULARY ANALYSIS")
    print("===================================")

    print(
        f"Valid records: {total_records}"
    )

    print(
        f"Invalid lines skipped: {skipped_lines}"
    )

    print(
        f"Unique words found: {len(counter)}"
    )

    print()
    print("Top 150 words:")
    print("-----------------------------------")

    for number, (word, count) in enumerate(
        counter.most_common(150),
        start=1
    ):

        print(
            f"{number:3}. {word:<20} {count}"
        )


if __name__ == "__main__":
    main()