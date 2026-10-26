import json
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel,
    Trainer,
    TrainingArguments,
)


# ===================================
# PATHS
# ===================================

DATASET_DIR = Path("ocr_dataset")

TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "validation"

TRAIN_ANNOTATIONS = TRAIN_DIR / "annotations.jsonl"
VAL_ANNOTATIONS = VAL_DIR / "annotations.jsonl"

MODEL_NAME ="models/trocr-ocr"

OUTPUT_DIR = Path("models/trocr-ocr")


# ===================================
# DATASET
# ===================================

class OCRDataset(Dataset):

    def __init__(self, annotations_file, images_dir, processor):

        self.images_dir = images_dir
        self.processor = processor

        self.records = []

        with annotations_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                self.records.append(
                    json.loads(line)
                )

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):

        record = self.records[index]

        image_path = (
            self.images_dir /
            Path(record["image"]).name
        )

        text = record["text"]

        image = Image.open(
            image_path
        ).convert("RGB")

        pixel_values = self.processor(
            images=image,
            return_tensors="pt"
        ).pixel_values.squeeze(0)

        labels = self.processor.tokenizer(
            text,
            padding="max_length",
            max_length=128,
            truncation=True,
            return_tensors="pt"
        ).input_ids.squeeze(0)

        labels[
            labels == self.processor.tokenizer.pad_token_id
        ] = -100

        return {
            "pixel_values": pixel_values,
            "labels": labels,
        }


# ===================================
# MAIN
# ===================================

def main():

    print()
    print("===================================")
    print("TR OCR TRAINING")
    print("===================================")

    print()
    print("Loading processor...")

    processor = TrOCRProcessor.from_pretrained(
        MODEL_NAME
    )

    print("Loading model...")

    model = VisionEncoderDecoderModel.from_pretrained(
        MODEL_NAME)

    model.config.decoder_start_token_id = (processor.tokenizer.cls_token_id)

    model.config.pad_token_id = (processor.tokenizer.pad_token_id)

    model.config.eos_token_id = (processor.tokenizer.sep_token_id)

    print()
    print("Preparing datasets...")

    train_dataset = OCRDataset(
        TRAIN_ANNOTATIONS,
        TRAIN_DIR / "images",
        processor
    )

    validation_dataset = OCRDataset(
        VAL_ANNOTATIONS,
        VAL_DIR / "images",
        processor
    )

    print(
        f"Training samples: {len(train_dataset)}"
    )

    print(
        f"Validation samples: {len(validation_dataset)}"
    )

    print()
    print("Creating training configuration...")

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),

        num_train_epochs=3,

        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,

        learning_rate=5e-5,

        logging_steps=10,

        save_strategy="epoch",

        eval_strategy="epoch",

        save_total_limit=2,

        report_to="none",

        fp16=False,

        dataloader_num_workers=0,

        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,

        train_dataset=train_dataset,
        eval_dataset=validation_dataset,

        processing_class=processor,
    )

    print()
    print("===================================")
    print("STARTING TRAINING")
    print("===================================")

    trainer.train()

    print()
    print("===================================")
    print("SAVING MODEL")
    print("===================================")

    trainer.save_model(
        str(OUTPUT_DIR)
    )

    processor.save_pretrained(
        str(OUTPUT_DIR)
    )

    print()
    print("Training complete!")
    print(f"Model saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()