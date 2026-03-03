🛡️ AI-Driven Intrusion Detection and Prevention System (IDPS)
📌 Overview

This project is a Machine Learning-based Intrusion Detection and Prevention System designed to detect malicious network traffic in real time.

It uses XGBoost for classification and provides a dashboard interface for monitoring threats, logs, and network activity.

The system can:

Classify traffic as Normal or Attack

Automatically block suspicious IP addresses

Display logs and attack insights through a web dashboard

🚀 Features

✅ Real-time network traffic classification

✅ XGBoost-based ML model

✅ Data preprocessing & feature engineering

✅ Automatic IP blocking mechanism

✅ Interactive dashboard (Streamlit / Flask)

✅ Model & scaler persistence

✅ Attack log monitoring

🧠 Tech Stack

Programming Language:

Python

Machine Learning:

XGBoost

Scikit-learn

Pandas

NumPy

Backend / Dashboard:

Streamlit / Flask

Datasets Used:

TON-IoT

UNSW-NB15

📂 Project Structure
AI-IDPS/
│
├── main.py                # Streamlit Dashboard
├── train_2.py             # Model training script
├── model.pkl              # Trained XGBoost model
├── scaler.pkl             # Saved StandardScaler
├── dataset/               # Dataset files
├── logs/                  # Attack logs
├── requirements.txt       # Required dependencies
└── README.md              # Project documentation
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone <repository-link>
cd AI-IDPS
2️⃣ Create Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate     # For Linux/Mac
venv\Scripts\activate        # For Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
🏋️ Model Training

To train the model:

python train_2.py

This will:

Load dataset

Perform preprocessing

Train XGBoost classifier

Save model and scaler files

📊 Running the Dashboard

If using Streamlit:

streamlit run main.py

If using Flask:

python main.py

Then open in browser:

http://localhost:8501

or

http://127.0.0.1:5000
📈 Model Workflow

Data Loading

Data Cleaning & Preprocessing

Feature Engineering

Model Training (XGBoost Classifier)

Model Evaluation

Real-Time Prediction

Automated Prevention Action

🔐 Prevention Mechanism

When malicious traffic is detected:

The system flags the IP

Logs the threat

Blocks the IP automatically (simulation or firewall rule based)

📊 Future Improvements

Integrate deep learning models (LSTM for sequence-based detection)

Add SIEM integration

Deploy on cloud (AWS / Azure)

Implement real-time packet capture using Scapy

Improve dashboard analytics with charts

👨‍💻 Author

Poodari Sai Nikhil
Machine Learning & Cybersecurity Enthusiast

GitHub: https://github.com/nikhilpoodari
