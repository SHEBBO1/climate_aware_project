import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ===================== Config =====================
MODEL_OUT = "model.pkl"

# ===================== Synthetic Data =====================
def generate_synthetic(n=1500, random_state=42):
    rng = np.random.RandomState(random_state)

    soil_moisture = rng.uniform(0.05, 0.6, n)
    soil_temp = rng.uniform(5, 35, n)
    air_temp = rng.uniform(5, 40, n)
    humidity = rng.uniform(20, 95, n)
    rain_24h = rng.exponential(1.5, n)
    evapotranspiration = rng.uniform(0.5, 7.0, n)

    target = np.clip(
        (0.5 - soil_moisture) * (evapotranspiration + 3) * 2 - rain_24h * 0.3,
        0,
        None
    )

    return pd.DataFrame({
        "soil_moisture": soil_moisture,
        "soil_temp": soil_temp,
        "air_temp": air_temp,
        "humidity": humidity,
        "rain_24h": rain_24h,
        "evapotranspiration": evapotranspiration,
        "volume_l_per_m2": target
    })

# ===================== Train =====================
def train(data_path=None):
    if data_path and os.path.exists(data_path):
        print(f"Loading dataset from {data_path}")
        df = pd.read_csv(data_path)

        required = [
            "soil_moisture",
            "soil_temp",
            "air_temp",
            "humidity",
            "rain_24h",
            "evapotranspiration",
            "volume_l_per_m2"
        ]

        missing = [c for c in required if c not in df.columns]

        if missing:
            print("Missing columns detected, attempting target derivation...")
            if "soil_moisture" in df.columns and "evapotranspiration" in df.columns:
                df = df.copy()
                df["volume_l_per_m2"] = (
                    (0.5 - df["soil_moisture"]).clip(0)
                    * (df["evapotranspiration"] + 3)
                    * 2
                    - df.get("rain_24h", 0) * 0.3
                )
            else:
                print("Insufficient data — generating synthetic dataset.")
                df = generate_synthetic()
    else:
        print("No CSV provided — generating synthetic dataset.")
        df = generate_synthetic()

    features = [
        "soil_moisture",
        "soil_temp",
        "air_temp",
        "humidity",
        "rain_24h",
        "evapotranspiration"
    ]

    X = df[features].values
    y = df["volume_l_per_m2"].values

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=1
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=1
    )

    model.fit(X_train, y_train)

    val_pred = model.predict(X_val)
    rmse = np.sqrt(((val_pred - y_val) ** 2).mean())
    print(f"Validation RMSE: {rmse:.4f}")

    joblib.dump(model, MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")

# ===================== Run =====================
if __name__ == "__main__":
    train()
