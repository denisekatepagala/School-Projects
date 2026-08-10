# Development of a Deep Learning Pipeline for Automated Plant Disease Diagnosis Using Sequential CNNs

> This project proposes a Plant Disease Recognition System using CNN with TensorFlow and KerasCV that can analyze plant leaf images and determine possible diseases efficiently and accurately. The system aims to provide users with a faster and more accessible method of plant disease detection through image processing and machine learning.

---

## 01 Contributors:  
- Ethan Raphael David  
- Denise Kate Pagala  
- John Joseph Valencia
  
---
## 02 Preview

<img width="1920" height="1080" alt="CPE178P_Project Preview" src="https://github.com/user-attachments/assets/b20d9e95-3e47-4bf5-8491-4e7c3dc7dc66" />

---

## 03 Features

- *Leaf Image Upload* – Allows users to upload an image of a plant leaf for analysis.
- *Automatic Image Preprocessing* – Resizes and normalizes uploaded images to 128 × 128 pixels before classification.
- *Disease Detection* – Uses a trained Convolutional Neural Network (CNN) to classify the uploaded plant leaf into one of the supported disease categories.
- *Prediction Result Display* – Displays the detected disease along with the predicted class.
- *Confidence-Based Classification* – Uses the Softmax activation function to determine the most probable disease class.

---

## 04 Built With

- Python
- TensorFlow
- FastAPI
- Flet
- Librosa
- NumPy
- Pandas
- Matplotlib

---

## 05 Project Structure

```text
code/
├── backend/
├── frontend/
├── datasets/
├── requirements.txt
└── ...
```

---

## 06 Requirements

```txt
tensorflow==2.10.0
scikit-learn==1.3.0
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.13.0
pandas==2.1.0
librosa==0.10.1
fastapi
uvicorn[standard]
flet
requests
```

---

## 07 Installation

### 1. Clone the repository

```bash
git clone https://github.com/denisekatepagala/CPE178P_E01_3T2526_Group03.git
cd project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 08 Running the Project

### Start the backend

```bash
uvicorn main:app --reload
```

### Start the frontend

```bash
python main.py
```

---

## 09 Usage
Instructions how to use: 
1. Launch the application.
2. Go to Prediction tab.
3. Click **Upload Image**.
4. Upload a plant leaf image from the test folder.
5. Click **Predict**.
6. View the Plant, Disease detected, and Confidence level results.

---

## 10 Model Performance

After training for 20 epochs, the model achieved the following results:
- Training Accuracy: 99.71%
- Training Loss: 0.90%
- Validation Accuracy: 97.84%
- Validation Loss: 8.91%

---

## 11 Limitations
1. *Limited to the Trained Dataset* - The system can only accurately classify plant diseases that belong to the trainig dataset.
2. *Single Leaf Image Input* - The system can only accept single leaf image input and not multiple image inputs.
3. *No Treatment Recommendation Validation* - The system only shows the Plant and Plant Disease detected with the Confidence level result.

