# English-to-Tagalog OCR Translation System Using Deep Learning and Raspberry Pi

> This project proposes an English-to-Tagalog OCR Translation System that uses Optical Character Recognition (OCR) and deep learning to recognize printed English text and translate it into Tagalog. The system integrates a Flet-based graphical user interface, a FastAPI backend, and a Raspberry Pi 4B connected to a USB camera. It aims to provide users with an accessible way to capture printed text, extract its contents, and obtain a Tagalog translation through image processing and text translation.

**Repository:** `CPE179P_E01_1Q2627_Group01`

---

## 01 Contributors

- **Cristel Anthonette Estilo**
- **Justin Chandler Ngo**
- **Denise Kate Pagala**

---

## 02 Project Preview

The system captures printed English text using a USB camera connected to the Raspberry Pi 4B. The captured image is processed by an OCR model to recognize the text, which is then translated into Tagalog and displayed through the graphical user interface.

Sample:
![The image presents the sample output of English to Tagalog translation using photo upload](images/sample.JPG)

---

## 03 Features

- **Image Capture** – Captures printed English text using a USB camera connected to the Raspberry Pi 4B.
- **Optical Character Recognition (OCR)** – Uses a trained TrOCR model to recognize and extract English text from captured images.
- **English-to-Tagalog Translation** – Translates recognized English text into Tagalog using the configured translation method.
- **Graphical User Interface** – Uses Flet to display captured images, recognized English text, and Tagalog translations.
- **Backend API Integration** – Uses FastAPI to handle requests between the laptop frontend and Raspberry Pi backend.
- **Raspberry Pi Integration** – Uses the Raspberry Pi 4B for camera capture and supported OCR and translation operations.
- **Text Result Display** – Displays the recognized English text alongside its corresponding Tagalog translation.
- **Image-Based Processing** – Processes individual captured images instead of continuously analyzing a live camera feed.

---

## 04 Built With

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| PyTorch | Deep learning framework |
| Hugging Face Transformers | Provides the transformer model implementation |
| TrOCR | OCR model for printed text recognition |
| FastAPI | Backend API development |
| Uvicorn | Runs the FastAPI server |
| Flet | Graphical user interface |
| Requests | HTTP communication between frontend and backend |
| Pillow | Image handling and processing |
| SentencePiece | Text tokenization support |
| Raspberry Pi 4B | Hardware platform for camera capture and processing |
| USB Camera | Captures printed English text |

---

## 05 Project Structure

```text
CPE179P_E01_1Q2627_Group01/
│
├── Project Sprint 1/
│   ├── source code/
│   ├── Project Schedule (Updated)
│   └── Project Documentation (Updated)
│
├── Project Sprint 2/
│   ├── source code/
│   └── README.md
│
├── Project Sprint 3/
│   ├── source code/
│   ├── Project Schedule (Updated)
│   └── Project Documentation (Updated)
│
├── dataset/
│   ├── images/
│   └── detector_subset_100.jsonl
│
├── images
│
├── source codes/
|   ├── frontend
|   ├── backend
|   └── requirements.txt
│
└── README.md
```

**Note:** This is a suggested project structure. Update the folders according to the actual files included in the final repository. The model directory should contain the trained model files required for inference. Dataset files only need to be included if they are intended to be distributed with the project.

---

## 06 Requirements

The project uses the following Python libraries:

```text
flet==1.0.3
fastapi==0.115.12
uvicorn==0.34.0
opencv-python==4.11.0.86
Pillow==11.1.0
pytesseract==0.3.13
requests==2.32.5
deep-translator==1.11.4
googletrans==4.0.2
python-multipart==0.0.20
transformers==4.57.3
sentencepiece==0.2.1
```

### Hardware Requirements

- Raspberry Pi 4B
- Compatible Raspberry Pi OS
- USB camera
- Laptop or computer for running the frontend
- Wi-Fi network connection shared by the laptop and Raspberry Pi

**Note:** Verify the compatibility of the selected PyTorch and Transformers versions with the Python version and operating system on each device. The frontend and backend may require separate dependency files.

---

## 07 Installation

### 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/denisekatepagala/CPE179P_E01_1Q2627_Group01.git
cd CPE179P_E01_1Q2627_Group01
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```powershell
venv\Scripts\activate
```

**Raspberry Pi / Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

Run this command on the device where the corresponding requirements are supported.

### 4. Configure the Backend Connection

Update the backend IP address in `frontend.py` to match the Raspberry Pi's actual local network IP address.

Example:

```python
BACKEND_URL = "http://192.168.1.43:8002"
```

Make sure that the laptop and Raspberry Pi can communicate over the same network.

---

## 08 Running the Project

### 1. Start the Backend on the Raspberry Pi

Navigate to the directory containing `backend.py` and run:

```bash
uvicorn backend:app --host 0.0.0.0 --port 8002
```

The backend API documentation can be accessed through:

```text
http://RASPBERRY-PI-IP:8002/docs
```

Replace `RASPBERRY-PI-IP` with the actual IP address of the Raspberry Pi.

### 2. Start the Frontend on the Laptop

Open another terminal, activate the appropriate virtual environment, and navigate to the directory containing `frontend.py`.

Run:

```bash
python frontend.py
```

The frontend communicates with the Raspberry Pi backend using the configured IP address and port.

**Important:** Keep the backend running while using the frontend. Ensure that the IP address, port, and API endpoints match the backend implementation.

---

## 09 Usage

Follow these steps to use the system:

1. Connect the Raspberry Pi and laptop to the same Wi-Fi network.
2. Connect the USB camera to the Raspberry Pi.
3. Start the FastAPI backend on the Raspberry Pi.
4. Launch the frontend application on the laptop.
5. Position the printed English text in front of the camera.
6. Click the **Capture Image** button.
7. Allow the OCR model to process the captured image.
8. Review the recognized English text.
9. Run the translation process to convert the recognized text into Tagalog.
10. View the English text and its corresponding Tagalog translation in the application.

---

## 10 Model Performance

The OCR dataset was prepared using 300 image samples, divided into training and validation sets.

| Dataset Information | Details |
|---|---|
| Total Images | 300 |
| Training Samples | 240 |
| Validation Samples | 60 |
| Training-Validation Split | 80:20 |
| OCR Model | TrOCR |
| Deep Learning Framework | PyTorch |

### Evaluation Metrics

Final quantitative evaluation results have not yet been established. The following metrics should be measured after training and testing the model:

- **Character Error Rate (CER)** – Measures character-level recognition errors.
- **Word Error Rate (WER)** – Measures word-level recognition errors.
- **Training Loss** – Measures the model's training error.
- **Validation Loss** – Measures the model's performance on validation data.
- **Processing Time** – Measures how long the system takes to recognize text from an image.

Translation quality should be evaluated separately from OCR performance because text recognition and language translation are different tasks.

---

## 11 Limitations

1. **Limited Dataset** – The current dataset contains 300 image samples, which may limit the model's ability to recognize different fonts, layouts, and printed text conditions.

2. **Printed Text Recognition** – The system is designed for printed English text and may not perform reliably on handwritten text.

3. **Translation Quality** – The quality of the Tagalog translation depends on the selected translation method and the accuracy of the recognized English text.

4. **Network Dependency** – The laptop frontend requires network connectivity to communicate with the Raspberry Pi backend.

5. **Camera Dependency** – Image capture requires a properly connected and supported USB camera.

6. **Processing Time** – The speed of OCR processing depends on the Raspberry Pi's computing resources, model configuration, and image complexity.

7. **Single-Image Processing** – The system captures and processes individual images instead of continuously analyzing a live camera feed.

---

## 12 Future Improvements

- Expand the OCR dataset with additional words, phrases, fonts, and document layouts.
- Improve OCR accuracy through additional model training and evaluation.
- Optimize model inference for Raspberry Pi deployment.
- Improve Tagalog translation quality and sentence handling.
- Add image preprocessing to improve recognition under different lighting conditions.
- Improve the graphical interface with clearer status messages and error handling.
- Evaluate the complete system using measurable OCR and translation performance metrics.

---

**Course:** CPE179P  
**Section:** E01  
**Academic Year:** 1Q2627  
**Group:** 01

