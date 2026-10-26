"""Stage 6 - Flask API for the wildfire building-damage model (Model 00)

Run from the project root:
    python backend\\app.py
Endpoints:
    GET  /health    -> service + model status
    GET  /features  -> feature names and observed ranges (used by the Angular form)
    POST /predict   -> JSON with all 21 features, returns the prediction
"""
from pathlib import Path
import json
import math

import joblib
import pandas as pd
from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model_bundle.joblib"
META_PATH = BASE_DIR / "feature_metadata.json"

app = Flask(__name__)

bundle = joblib.load(MODEL_PATH)
MODEL = bundle["pipeline"]
FEATURES = bundle["features"]
CLASSES = bundle["classes"]
VERSION = bundle["model_version"]
META = json.loads(META_PATH.read_text(encoding="utf-8")) if META_PATH.exists() else {}

# Only features that are empty in the training data may be sent as null
NULLABLE = {f for f, m in META.items() if m.get("allow_missing")}


def error(message, status=400, **extra):
    return jsonify({"error": message, **extra}), status


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model_version": VERSION,
            "task": bundle["task"],
            "n_features": len(FEATURES),
        }
    )


@app.get("/features")
def features():
    return jsonify(
        {
            "features": FEATURES,
            "nullable": sorted(NULLABLE),
            "metadata": META,
        }
    )


@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("Request body must be a JSON object")

    missing = [f for f in FEATURES if f not in data]
    unknown = [k for k in data if k not in FEATURES]
    if missing or unknown:
        return error("Invalid fields", missing=missing, unknown=unknown)

    row, problems, warnings = [], {}, []
    for f in FEATURES:
        v = data[f]
        if v is None:
            if f in NULLABLE:
                row.append(float("nan"))  # median imputer fills it
            else:
                problems[f] = "value is required"
                row.append(float("nan"))
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            problems[f] = "must be a number"
            row.append(float("nan"))
            continue
        if not math.isfinite(v):
            problems[f] = "must be a finite number"
            row.append(float("nan"))
            continue
        row.append(float(v))
        m = META.get(f)
        if m and not (m["min"] <= v <= m["max"]):
            warnings.append(
                f"{f}={v} is outside the range seen in training ({m['min']:.4g} to {m['max']:.4g})"
            )
    if problems:
        return error("Invalid values", fields=problems)

    frame = pd.DataFrame([row], columns=FEATURES)
    pred = int(MODEL.predict(frame)[0])
    proba = MODEL.predict_proba(frame)[0]

    return jsonify(
        {
            "prediction": pred,
            "label": CLASSES[str(pred)],
            "probability_damage": round(float(proba[1]), 4),
            "probability_no_damage": round(float(proba[0]), 4),
            "model_version": VERSION,
            "warnings": warnings,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
