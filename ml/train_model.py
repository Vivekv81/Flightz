import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# CONFIGURATION
# ============================================================

DATASET = "data/Data_Train.xlsx"

MODEL_FILE = "ml/fare_model.pkl"


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("=" * 60)
print("FLIGHT FARE PREDICTION - MODEL TRAINING")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_excel(DATASET)

print("Dataset shape:", df.shape)


# ============================================================
# DATA CLEANING
# ============================================================

print("\nChecking missing values...")

print(df.isnull().sum())

# Remove rows with missing values
df = df.dropna().copy()

print("\nShape after removing missing values:", df.shape)


# ============================================================
# DATE FEATURES
# ============================================================

df["Date_of_Journey"] = pd.to_datetime(
    df["Date_of_Journey"],
    dayfirst=True
)

df["Journey_Day"] = df["Date_of_Journey"].dt.day
df["Journey_Month"] = df["Date_of_Journey"].dt.month

df.drop("Date_of_Journey", axis=1, inplace=True)


# ============================================================
# DEPARTURE TIME FEATURES
# ============================================================

df["Dep_Hour"] = df["Dep_Time"].str.split(":").str[0].astype(int)

df["Dep_Minute"] = (
    df["Dep_Time"]
    .str.split(":")
    .str[1]
    .astype(int)
)

df.drop("Dep_Time", axis=1, inplace=True)


# ============================================================
# ARRIVAL TIME FEATURES
# ============================================================

df["Arrival_Hour"] = (
    df["Arrival_Time"]
    .str.split(":")
    .str[0]
    .astype(int)
)

df["Arrival_Minute"] = (
    df["Arrival_Time"]
    .str.split(":")
    .str[1]
    .str[:2]
    .astype(int)
)

df.drop("Arrival_Time", axis=1, inplace=True)


# ============================================================
# DURATION FEATURES
# ============================================================

def convert_duration(duration):

    hours = 0
    minutes = 0

    parts = duration.split()

    for part in parts:

        if "h" in part:
            hours = int(part.replace("h", ""))

        elif "m" in part:
            minutes = int(part.replace("m", ""))

    return hours * 60 + minutes


df["Duration_Minutes"] = df["Duration"].apply(
    convert_duration
)

df.drop("Duration", axis=1, inplace=True)


# ============================================================
# TOTAL STOPS
# ============================================================

stop_mapping = {
    "non-stop": 0,
    "1 stop": 1,
    "2 stops": 2,
    "3 stops": 3,
    "4 stops": 4
}

df["Total_Stops"] = df["Total_Stops"].map(stop_mapping)


# Remove rows where stops could not be converted

df = df.dropna(subset=["Total_Stops"])

df["Total_Stops"] = df["Total_Stops"].astype(int)


# ============================================================
# REMOVE ROUTE
# ============================================================

# Route contains information already represented by
# Source, Destination and Total_Stops.

df.drop("Route", axis=1, inplace=True)


# ============================================================
# FEATURES AND TARGET
# ============================================================

X = df.drop("Price", axis=1)

y = df["Price"]


print("\nFeatures used by the model:")
print(X.columns.tolist())

print("\nTarget: Price")


# ============================================================
# CATEGORICAL / NUMERICAL FEATURES
# ============================================================

categorical_features = [
    "Airline",
    "Source",
    "Destination",
    "Additional_Info"
]

numerical_features = [
    "Journey_Day",
    "Journey_Month",
    "Dep_Hour",
    "Dep_Minute",
    "Arrival_Hour",
    "Arrival_Minute",
    "Duration_Minutes",
    "Total_Stops"
]


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
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

print()
print("Training samples:", len(X_train))
print("Testing samples :", len(X_test))


# ============================================================
# MODEL 1 - RANDOM FOREST
# ============================================================

print()
print("=" * 60)
print("TRAINING RANDOM FOREST")
print("=" * 60)

random_forest = Pipeline(
    steps=[
        ("preprocessor", preprocessor),

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

random_forest.fit(X_train, y_train)

rf_predictions = random_forest.predict(X_test)


rf_mae = mean_absolute_error(
    y_test,
    rf_predictions
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        rf_predictions
    )
)

rf_r2 = r2_score(
    y_test,
    rf_predictions
)


print("\nRandom Forest Results")

print("MAE  :", round(rf_mae, 2))
print("RMSE :", round(rf_rmse, 2))
print("R²   :", round(rf_r2, 4))


# ============================================================
# MODEL 2 - GRADIENT BOOSTING
# ============================================================

print()
print("=" * 60)
print("TRAINING GRADIENT BOOSTING")
print("=" * 60)

gradient_boosting = Pipeline(
    steps=[
        ("preprocessor", preprocessor),

        (
            "model",
            GradientBoostingRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=5,
                random_state=42
            )
        )
    ]
)

gradient_boosting.fit(
    X_train,
    y_train
)

gb_predictions = gradient_boosting.predict(
    X_test
)


gb_mae = mean_absolute_error(
    y_test,
    gb_predictions
)

gb_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        gb_predictions
    )
)

gb_r2 = r2_score(
    y_test,
    gb_predictions
)


print("\nGradient Boosting Results")

print("MAE  :", round(gb_mae, 2))
print("RMSE :", round(gb_rmse, 2))
print("R²   :", round(gb_r2, 4))


# ============================================================
# SELECT BEST MODEL
# ============================================================

if gb_rmse < rf_rmse:

    best_model = gradient_boosting
    best_model_name = "Gradient Boosting"

else:

    best_model = random_forest
    best_model_name = "Random Forest"


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    best_model,
    MODEL_FILE
)


# ============================================================
# FINAL RESULTS
# ============================================================

print()
print("=" * 60)
print("MODEL TRAINING COMPLETE")
print("=" * 60)

print("Best model:", best_model_name)

print("Model saved to:", MODEL_FILE)

print("=" * 60)