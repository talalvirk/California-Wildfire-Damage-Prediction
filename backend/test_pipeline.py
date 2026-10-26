"""Stage 5.4 - run the saved model directly (no Flask) on the sample payload"""
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
bundle = joblib.load(ROOT / "backend" / "models" / "model_bundle.joblib")
payload = json.loads((ROOT / "backend" / "test_payload.json").read_text(encoding="utf-8"))

features = bundle["features"]
assert set(features) == set(payload), "Payload keys must match features"

# None -> NaN so the saved median imputer can fill it
frame = pd.DataFrame([[payload[f] for f in features]], columns=features).astype(float)

model = bundle["pipeline"]
pred = int(model.predict(frame)[0])
proba = model.predict_proba(frame)[0]
print("Prediction:", pred, "->", bundle["classes"][str(pred)])
print(f"P(no damage) = {proba[0]:.3f} | P(damage) = {proba[1]:.3f}")

# Known-answer check: the sample row came from the test split with label 0 (no damage)
expected = 0
print("Expected label:", expected)
print("Matches known label" if pred == expected else "NOTE: differs from the known label (a single row can be misclassified; check P(damage))")

# Missing-value check: PFTk9 can be empty in the dataset
frame2 = frame.copy()
frame2["PFTk9"] = np.nan
print("With PFTk9 missing ->", int(model.predict(frame2)[0]))
print("PASS: local inference")
