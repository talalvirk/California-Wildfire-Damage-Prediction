"""
Stage 4 - Train Model 00 (Comprehensive) and save backend/models/model_bundle.joblib

Run from the project root (venv active):
    python backend\\train_model.py

Needs:  data/CalDins_upd_extractions_subset_03.csv
Creates:
    backend/models/model_bundle.joblib   (pipeline + features + task + version)
    backend/feature_metadata.json        (min / median / max per feature, for the Angular form)
    data/sample_inputs.csv               (one non-sensitive example row)
"""
from pathlib import Path
import json

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "CalDins_upd_extractions_subset_03.csv"
OUT_MODEL = ROOT / "backend" / "models" / "model_bundle.joblib"
OUT_META = ROOT / "backend" / "feature_metadata.json"
OUT_SAMPLE = ROOT / "data" / "sample_inputs.csv"

# 200 trees keeps the file near 50 MB (GitHub rejects files over 100 MB).
# The paper used 2000 trees, which would be roughly 10x larger.
N_TREES = 200
SEED = 123

# Model 00 (Comprehensive) = the 21 predictors, in this exact order.
FEATURES = [
    "Aspect", "Elevation", "Slope", "TRI", "EVH", "EVT",
    "WUI_Area", "BuildingDensity", "BTF", "Frs_Area", "RoadLength", "PFTk9",
    "CBFR",
    "prcp", "MaxRH", "Srad", "tdmean", "WD", "Tmax", "VPD", "WS10m",
]
TARGET = "Damage01"  # 1 = damaged, 0 = no damage

# ---------------------------------------------------------------- load
df = pd.read_csv(DATA_FILE)
missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
if missing:
    raise SystemExit(f"CSV is missing columns: {missing}")

X = df[FEATURES].astype(float)
y = df[TARGET].astype(int)
print(f"Rows: {len(df)} | features: {len(FEATURES)} | damaged share: {y.mean():.3f}")

# ---------------------------------------------------------------- split (70/30, as in the paper)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=SEED, stratify=y
)

# ---------------------------------------------------------------- fit preprocessing on TRAIN only
imputer = SimpleImputer(strategy="median")
X_train_imp = imputer.fit_transform(X_train)

# SMOTE balances the TRAINING data only. It is not needed at prediction time.
X_bal, y_bal = SMOTE(random_state=SEED).fit_resample(X_train_imp, y_train)

rf = RandomForestClassifier(
    n_estimators=N_TREES, criterion="entropy", random_state=SEED, n_jobs=-1
)
rf.fit(X_bal, y_bal)

# Assemble a pipeline from the already-fitted steps: raw row -> impute -> predict
pipeline = Pipeline([("impute", imputer), ("model", rf)])

# ---------------------------------------------------------------- quick sanity metrics on held-out 30%
pred = pipeline.predict(X_test)
proba = pipeline.predict_proba(X_test)[:, 1]
print("Hold-out 30% (random split, NOT the paper's spatial CV):")
print(f"  accuracy  {accuracy_score(y_test, pred):.3f}")
print(f"  precision {precision_score(y_test, pred):.3f}")
print(f"  recall    {recall_score(y_test, pred):.3f}")
print(f"  f1        {f1_score(y_test, pred):.3f}")
print(f"  roc_auc   {roc_auc_score(y_test, proba):.3f}")

# ---------------------------------------------------------------- save bundle
bundle = {
    "pipeline": pipeline,
    "features": FEATURES,
    "task": "classification",
    "model_version": "1.0-model00-comprehensive",
    "classes": {"0": "No damage", "1": "Damage"},
}
OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(bundle, OUT_MODEL, compress=3)
print(f"Saved {OUT_MODEL}  ({OUT_MODEL.stat().st_size / 1e6:.1f} MB)")
if OUT_MODEL.stat().st_size > 95e6:
    print("WARNING: file is close to / above GitHub's 100 MB limit. Lower N_TREES.")

# ---------------------------------------------------------------- metadata for the Angular form (Stage 9.1)
meta = {}
for f in FEATURES:
    col = X[f]
    meta[f] = {
        "min": float(col.min()),
        "p01": float(col.quantile(0.01)),
        "median": float(col.median()),
        "p99": float(col.quantile(0.99)),
        "max": float(col.max()),
        "allow_missing": bool(col.isna().any()),
    }
OUT_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(f"Saved {OUT_META}")

# ---------------------------------------------------------------- one sample row (no coordinates, no IDs)
X_test.head(1).to_csv(OUT_SAMPLE, index=False)
print(f"Saved {OUT_SAMPLE}  (actual label for this row: {int(y_test.iloc[0])})")