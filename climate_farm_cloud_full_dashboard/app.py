from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory
import os, joblib
import numpy as np, pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import train as trainer
import data_fetcher

# ===================== Paths =====================
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "devsecret"
ALLOWED_EXT = {"csv"}

# ===================== Helpers =====================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

# ===================== Index =====================
@app.route("/")
def index():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    return render_template(
        "index.html",
        model_present=os.path.exists(MODEL_PATH),
        data_files=files,
        sample={
            "soil_moisture": 0.2,
            "soil_temp": 20,
            "air_temp": 25,
            "humidity": 60,
            "rain_24h": 0,
            "evapotranspiration": 3
        }
    )

# ===================== Predict API =====================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    def f(k, d):
        try:
            return float(data.get(k, d))
        except:
            return d

    features = [
        f("soil_moisture", 0.2),
        f("soil_temp", 20),
        f("air_temp", 25),
        f("humidity", 60),
        f("rain_24h", 0),
        f("evapotranspiration", 3)
    ]

    model = load_model()

    if model is None:
        deficit = max(0, 0.5 - features[0])
        volume = round(deficit * (features[5] + 5) * 2, 2)
        return jsonify({
            "model": "fallback",
            "volume_l_per_m2": volume,
            "schedule": {
                "start": datetime.utcnow().isoformat() + "Z",
                "duration_min": int(30 * deficit + 10)
            }
        })

    pred = float(model.predict(np.array(features).reshape(1, -1))[0])
    return jsonify({
        "model": "trained",
        "volume_l_per_m2": pred,
        "schedule": {
            "start": datetime.utcnow().isoformat() + "Z",
            "duration_min": int(max(5, pred * 6))
        }
    })

# ===================== Health Check =====================
@app.route("/healthz")
def healthz():
    return jsonify({
        "service": "Climate Aware Cloud AI",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

# ===================== Predict GUI =====================
@app.route("/predict-ui")
def predict_ui():
    return render_template("predict_ui.html")

# ===================== NOAA Upload =====================
@app.route("/upload_noaa", methods=["POST"])
def upload_noaa():
    file = request.files.get("file")
    if not file or not allowed_file(file.filename):
        return redirect(url_for("index"))

    path = os.path.join(DATA_DIR, secure_filename(file.filename))
    file.save(path)

    df = pd.read_csv(path)
    fig = df.select_dtypes(include=["number"]).plot(subplots=True).figure
    fig.savefig(os.path.join(STATIC_DIR, "stats.png"))

    return redirect(url_for("index"))

# ===================== Fetch NOAA =====================
@app.route("/fetch_noaa", methods=["POST"])
def fetch_noaa():
    d = request.get_json() or request.form
    df = data_fetcher.fetch_noaa_station_data(d["station"], d["start"], d["end"])
    name = f"noaa_{d['station']}_{d['start']}_{d['end']}.csv"
    df.to_csv(os.path.join(DATA_DIR, name), index=False)
    return jsonify({"rows": len(df)})

# ===================== Train =====================
@app.route("/train", methods=["POST"])
def train_endpoint():
    d = request.get_json() or request.form
    trainer.train(d.get("filename"))
    return jsonify({"status": "trained"})

# ===================== Data Preview =====================
@app.route("/data_preview")
def data_preview():
    f = request.args.get("filename")
    if not f:
        f = next((x for x in os.listdir(DATA_DIR) if x.endswith(".csv")), None)
    df = pd.read_csv(os.path.join(DATA_DIR, f))
    return jsonify({
        "filename": f,
        "columns": df.columns.tolist(),
        "preview": df.head(20).to_dict(orient="records")
    })

# ===================== Data Numeric =====================
@app.route("/data_numeric")
def data_numeric():
    f = request.args.get("filename")
    if not f:
        f = next((x for x in os.listdir(DATA_DIR) if x.endswith(".csv")), None)
    df = pd.read_csv(os.path.join(DATA_DIR, f))
    num = df.select_dtypes(include=["number"]).fillna(0)
    x = df["DATE"].astype(str).tolist() if "DATE" in df.columns else list(range(len(num)))
    return jsonify({"x": x, "series": {c: num[c].tolist() for c in num.columns}})

# ===================== Irrigation Dashboard =====================
@app.route("/irrigation_schedule")
def irrigation_schedule():
    return render_template("irrigation_schedule.html")

# ===================== Static =====================
@app.route("/static/<path:f>")
def static_files(f):
    return send_from_directory(STATIC_DIR, f)

# ===================== Run =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
