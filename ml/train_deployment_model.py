import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

DATASET = "data/Data_Train.xlsx"
MODEL_FILE = "ml/deployment_model.pkl"


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("=" * 60)
print("FLIGHT FARE - DEPLOYMENT MODEL")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_excel(DATASET)

print("Original dataset:", df.shape)


# ============================================================
# CLEAN DATA
# ============================================================

df = df.dropna().copy()

print("After cleaning:", df.shape)


# ============================================================
# DATE FEATURES
# ============================================================

df["Date_of_Journey"] = pd.to_datetime(
    df["Date_of_Journey"],
    dayfirst=True
)

df["Journey_Day"] = df["Date_of_Journey"].dt.day

df["Journey_Month"] = df["Date_of_Journey"].dt.month


# ============================================================
# SELECT ONLY FEATURES AVAILABLE IN OUR APPLICATION
# ============================================================

features = [
    "Airline",
    "Source",
    "Destination",
    "Journey_Day",
    "Journey_Month"
]

X = df[features]

y = df["Price"]


print("\nFeatures used:")
print(features)

print("\nTarget:")
print("Price")


# ============================================================
# CATEGORICAL / NUMERICAL FEATURES
# ============================================================

categorical_features = [
    "Airline",
    "Source",
    "Destination"
]

numerical_features = [
    "Journey_Day",
    "Journey_Month"
]


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining samples:", len(X_train))
print("Testing samples :", len(X_test))


# ============================================================
# RANDOM FOREST
# ============================================================

print()
print("=" * 60)
print("TRAINING DEPLOYMENT MODEL")
print("=" * 60)

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)


model.fit(
    X_train,
    y_train
)


# ============================================================
# EVALUATION
# ============================================================

predictions = model.predict(X_test)


mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)


print()
print("Deployment Model Results")
print()
print("MAE  :", round(mae, 2))
print("RMSE :", round(rmse, 2))
print("R²   :", round(r2, 4))


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_FILE
)


print()
print("=" * 60)
print("DEPLOYMENT MODEL SAVED")
print("=" * 60)

print("Model:", MODEL_FILE)

print("=" * 60)