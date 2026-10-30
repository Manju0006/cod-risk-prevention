
import pandas as pd
import joblib
import json

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "cleaned_orders.csv"
MODEL_FILE = BASE_DIR / "models" / "rto_model.pkl"
METRICS_FILE = BASE_DIR / "reports" / "model_metrics.json"


def train_model():

    print("\n========== RTO MODEL TRAINING ==========")

    # Load cleaned data
    df = pd.read_csv(DATA_FILE)

    # Convert date and sort chronologically
    df["order_datetime"] = pd.to_datetime(
        df["order_datetime"],
        errors="coerce"
    )

    df = df.sort_values("order_datetime").reset_index(drop=True)

    # Input features
    numeric_features = [
        "order_value",
        "num_items",
        "customer_prior_orders",
        "customer_prior_rto",
        "order_hour",
        "order_month",
        "order_dayofweek"
    ]

    categorical_features = [
        "city",
        "state",
        "utm_source",
        "courier"
    ]

    features = numeric_features + categorical_features

    X = df[features]
    y = df["rto"]

    # Chronological 80:20 split
    split_index = int(len(df) * 0.80)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    # Numerical preprocessing
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Categorical preprocessing
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("numeric", numeric_transformer, numeric_features),
        ("categorical", categorical_transformer,
         categorical_features)
    ])

    # ML pipeline
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=2000))
    ])

    # Train
    print("\nTraining Logistic Regression...")

    model.fit(X_train, y_train)

    # Predictions
    probabilities = model.predict_proba(X_test)[:, 1]

    predictions = (probabilities >= 0.5).astype(int)

    # Evaluation
    accuracy = accuracy_score(y_test, predictions)
    auc = roc_auc_score(y_test, probabilities)

    avg_precision = average_precision_score(
        y_test,
        probabilities
    )

    print("\n========== MODEL PERFORMANCE ==========")

    print("Accuracy:", round(accuracy, 4))
    print("ROC-AUC:", round(auc, 4))
    print("Average Precision:", round(avg_precision, 4))

    print("\nClassification Report:")

    print(classification_report(
        y_test,
        predictions,
        target_names=["Delivered", "RTO"],
        zero_division=0
    ))

    print("\nConfusion Matrix:")

    print(confusion_matrix(y_test, predictions))

    # Save model
    joblib.dump(model, MODEL_FILE)

    # Save metrics
    metrics = {
        "model": "Logistic Regression",
        "accuracy": float(accuracy),
        "roc_auc": float(auc),
        "average_precision": float(avg_precision),
        "training_records": len(X_train),
        "testing_records": len(X_test),
        "threshold": 0.5
    }

    with open(METRICS_FILE, "w") as file:
        json.dump(metrics, file, indent=4)

    print("\nModel saved successfully!")
    print("Metrics saved successfully!")


if __name__ == "__main__":
    train_model()
