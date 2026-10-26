'''
Project Sprint 1
1.0 Expected Output/ Notes
- User inputs English sentence, system translates to Tagalog
- Allows for multiple inputs
- System is more accurate if user will input in sentence form rather than single words only
- System is case sensitive, specifically to names

2.0 Requirements needed
- Python 3.13
- transformers==4.57.3
- torch==2.9.1
- sentencepiece==0.2.1
- requests==2.32.5
'''

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "Helsinki-NLP/opus-mt-en-tl"

print("Loading English → Tagalog translation model...")
print("Please wait...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

print("\nModel loaded successfully!")
print("English → Tagalog Translator")
print("Type 'exit' to stop.\n")


def translate_to_tagalog(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    outputs = model.generate(
        **inputs,
        max_length=128
    )

    return tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )


while True:
    english_text = input("English: ")

    if english_text.lower() == "exit":
        print("Program ended.")
        break

    if not english_text.strip():
        print("Please enter some text.\n")
        continue

    try:
        tagalog_text = translate_to_tagalog(english_text)
        print("Tagalog:", tagalog_text)
        print()

    except Exception as error:
        print("Translation error:", error)
        print()
