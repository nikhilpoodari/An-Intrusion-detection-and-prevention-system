# ==========================================
# AI-IDPS : Model Training & Accuracy Script
# File Name : train_2.py
# ==========================================

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from xgboost import XGBClassifier

# ------------------------------------------
# 1. LOAD DATASETS
# ------------------------------------------

print("📂 Loading datasets...")

ton_iot = pd.read_csv("ton-iot.csv")
unsw = pd.read_parquet("UNSW_NB15_testing-set.parquet")

print("TON-IoT shape:", ton_iot.shape)
print("UNSW-NB15 shape:", unsw.shape)

# ------------------------------------------
# 2. DATA CLEANING (FINAL FIX)
# ------------------------------------------

print("\n🧹 Cleaning data...")

def clean_dataframe(df):
    df = df.copy()

    # Convert categorical columns to object FIRST
    cat_cols = df.select_dtypes(include=["category"]).columns
    for col in cat_cols:
        df[col] = df[col].astype("object")

    # Numerical columns → fill with 0
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    df[num_cols] = df[num_cols].fillna(0)

    # Object columns → fill with "unknown"
    obj_cols = df.select_dtypes(include=["object"]).columns
    df[obj_cols] = df[obj_cols].fillna("unknown")

    return df

ton_iot = clean_dataframe(ton_iot)
unsw = clean_dataframe(unsw)

# Remove duplicates
ton_iot.drop_duplicates(inplace=True)
unsw.drop_duplicates(inplace=True)

# ------------------------------------------
# 3. FEATURE SELECTION
# (Numeric behavior-based IDS features only)
# ------------------------------------------

selected_features = [
    'dur',
    'spkts',
    'dpkts',
    'sbytes',
    'dbytes',
    'rate',
    'sload',
    'dload'
]

ton_features = [f for f in selected_features if f in ton_iot.columns]
unsw_features = [f for f in selected_features if f in unsw.columns]

X_ton = ton_iot[ton_features]
y_ton = ton_iot['label']

X_unsw = unsw[unsw_features]
y_unsw = unsw['label']

# ------------------------------------------
# 4. MERGE DATASETS
# ------------------------------------------

print("\n🔗 Merging datasets...")

X = pd.concat([X_ton, X_unsw], axis=0)
y = pd.concat([y_ton, y_unsw], axis=0)

print("Final feature shape:", X.shape)
print("Final label shape:", y.shape)

# ------------------------------------------
# 5. FEATURE NORMALIZATION
# ------------------------------------------

print("\n📏 Normalizing features...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

joblib.dump(scaler, "scaler.pkl")
print("✅ Scaler saved as scaler.pkl")

# ------------------------------------------
# 6. TRAIN–TEST SPLIT
# ------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# ------------------------------------------
# 7. TRAIN XGBOOST MODEL
# ------------------------------------------

print("\n🤖 Training XGBoost model...")

model = XGBClassifier(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)

joblib.dump(model, "xgboost_model_adaptive.pkl")
print("✅ Model saved as xgboost_model_adaptive.pkl")

# ------------------------------------------
# 8. ACCURACY CALCULATION
# ------------------------------------------

print("\n📊 Evaluating model...")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n✅ MODEL ACCURACY:", round(accuracy * 100, 2), "%")

# ------------------------------------------
# 9. CONFUSION MATRIX & REPORT
# ------------------------------------------

print("\n📌 CONFUSION MATRIX")
print(confusion_matrix(y_test, y_pred))

print("\n📌 CLASSIFICATION REPORT")
print(classification_report(y_test, y_pred))

# ------------------------------------------
# 10. FINAL MESSAGE
# ------------------------------------------

print("\n🎯 Training & Evaluation Completed Successfully!")
print("• Categorical handling fixed")
print("• Data cleaned safely")
print("• Features normalized")
print("• XGBoost trained")
print("• Accuracy calculated")
print("• Model & scaler saved")
