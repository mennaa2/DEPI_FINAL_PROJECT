# 🤰 Maternal Care Platform

An AI-powered maternal healthcare platform developed with **Python**, **Streamlit**, and **Machine Learning** to support pregnant women through intelligent risk prediction, pregnancy tracking, AI-assisted guidance, and automated medical report analysis.

## 🚀 Live Demo

🔗 https://depifinalproject-r4.streamlit.app/

---

# 📖 Overview

Maternal Care Platform is a full-stack web application designed to improve maternal healthcare awareness by integrating Artificial Intelligence, Machine Learning, Computer Vision, and Data Visualization into a single user-friendly platform.

The application predicts maternal health risks using a trained Random Forest model, enables users to monitor pregnancy progress, stores prediction history, provides AI-powered educational assistance, and automatically extracts medical information from uploaded laboratory reports using Optical Character Recognition (OCR).

---

# ✨ Features

## 🔐 User Authentication
- Secure user registration and login
- Password hashing using bcrypt
- Session management
- Personalized user dashboard

---

## 🤖 AI Risk Prediction

Predicts maternal risk level based on clinical information including:

- Age
- Systolic Blood Pressure
- Diastolic Blood Pressure
- Blood Sugar
- Body Temperature
- Heart Rate

Prediction Classes:

- 🟢 Low Risk
- 🟡 Moderate Risk
- 🔴 High Risk

Powered by a trained Random Forest Machine Learning model.

---

## 🤰 Pregnancy Tracker

- Calculate pregnancy week
- Estimate due date
- Weekly pregnancy progress
- Pregnancy milestones

---

## 📊 Prediction History

Each user's prediction history is stored securely.

Features include:

- Previous predictions
- Blood pressure trends
- Risk distribution
- Interactive charts
- CSV export

---

## 💬 AI Health Assistant

An AI-powered assistant that provides educational guidance on pregnancy-related topics including:

- Pregnancy nutrition
- Blood pressure
- Blood sugar
- Warning signs
- General maternal health
- Lifestyle recommendations

---

## 🧾 Medical Report Scanner

Users can upload laboratory reports as images or PDF files.

The system automatically:

- Preprocesses images
- Performs OCR text extraction
- Extracts medical measurements
- Generates a medical summary
- Auto-fills prediction values

---

## ❤️ Health Tips

Provides personalized educational recommendations covering:

- Nutrition
- Exercise
- Blood pressure management
- Blood sugar awareness
- Healthy pregnancy practices

---

# 🛠 Technologies Used

### Programming
- Python

### Web Framework
- Streamlit

### Machine Learning
- Scikit-learn
- Random Forest

### Database
- SQLite

### Computer Vision
- OpenCV

### OCR
- Tesseract OCR

### PDF Processing
- PyMuPDF

### Data Analysis
- Pandas
- NumPy

### Data Visualization
- Plotly

### Security
- bcrypt

---

# 📂 Project Structure

```
Maternal_Care/
│
├── ai_assistant/
├── auth/
├── database/
├── report_scanner/
├── pages/
├── models/
├── data/
├── assets/
├── app.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/your-username/Maternal-Care.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# 🧠 Machine Learning Model

The prediction system is powered by a trained Random Forest classifier that estimates maternal health risk using patient vital signs and clinical indicators.

---

# 📄 Medical Report Processing Pipeline

```
Medical Report
      │
      ▼
Image Preprocessing
      │
      ▼
OCR Extraction
      │
      ▼
Medical Data Parsing
      │
      ▼
Medical Summary
      │
      ▼
Risk Prediction
```

---

# 🎯 Future Improvements

- Deep Learning prediction models
- Mobile application
- Doctor dashboard
- Cloud database integration
- Arabic language support
- Real-time monitoring

---

## 👨‍💻 Development Team

- **Mennatallah Mohsen**
- **Aisha Samir**
- **Rola Hany**
- **Menna Akram**
- **Habiba Ashraf**

**Track:** Data Science & Artificial Intelligence

---

# 📄 License

This project was developed for educational and graduation project purposes.
