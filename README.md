# Wildfire Building Damage Predictor (Full-Stack ML + CI/CD)

**Author:** YOUR_NAME  |  **Course:** DevOps Lab 6, Air University (BSSE)

A Flask API and an Angular form that serve a Random Forest which predicts whether a building is
**damaged (1) or not damaged (0)** after a California wildfire. The model reproduces the
*comprehensive model* of Bar, Li & Banerjee, "Explaining building damage from wildfires in
California", *Science Advances* 12, eaed4197 (2026), trained on CAL FIRE DINS inspection records
(100,228 buildings, 2013-2024).

- Repository: https://github.com/YOUR_USERNAME/YOUR_REPO
- Static demo (GitHub Pages): https://YOUR_USERNAME.github.io/YOUR_REPO/

> **Disclaimer.** This is an educational reproduction, not an operational wildfire or insurance
> risk tool. Do not use its output for real decisions.

## Model and provenance

| Item | Value |
|---|---|
| Task | Binary classification (1 = damage, 0 = no damage) |
| Algorithm | `RandomForestClassifier` (200 trees, entropy, random_state=123) |
| Preprocessing | Median imputation (`SimpleImputer`) saved inside the pipeline |
| Class balancing | SMOTE on the training split only (not needed at prediction time) |
| Training data | `CalDins_upd_extractions_subset_03.csv` (not committed; 37 MB, see paper's data links) |
| Saved artifact | `backend/models/model_bundle.joblib` (pipeline + feature list + class labels + version) |
| Hold-out result | 70/30 random split: accuracy 0.926, F1 0.936, ROC-AUC 0.980 |

The hold-out score uses a plain random split. The paper's stricter 200 m spatial cross-validation
reports about 88 % accuracy for this model, which is the more honest estimate of real-world skill.

### The 21 input features (exact order)

Aspect, Elevation, Slope, TRI, EVH, EVT, WUI_Area, BuildingDensity, BTF, Frs_Area, RoadLength,
PFTk9, CBFR, prcp, MaxRH, Srad, tdmean, WD, Tmax, VPD, WS10m.
`PFTk9` may be empty (it is imputed). `Tmax` is in Kelvin. `CBFR` is a 0-10 flammability rating.

## Versions used

Python 3.14, Node.js 24.15.0, npm 11.12.1, Angular CLI 22.2.3, scikit-learn/pandas/numpy as pinned
in `backend/requirements.txt` (the saved model must be loaded with the same scikit-learn version).

## Run locally (Windows PowerShell)

```powershell
# one-time setup, from the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd frontend; npm ci; cd ..

# Terminal 1 - Flask API (http://127.0.0.1:5000)
python backend\app.py

# Terminal 2 - Angular (http://localhost:4200, proxies /api to Flask)
cd frontend
ng serve --proxy-config proxy.conf.json --open
```

Retrain (optional): put the CSV in `data\` and run `python backend\train_model.py`.

## Tests

```powershell
python -m pytest -v backend/tests        # 13 tests: structure + API
python backend\test_pipeline.py          # direct model check
cd frontend; npm test -- --watch=false   # 3 Angular unit tests
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | status and model version |
| GET | `/features` | feature names and observed ranges |
| POST | `/predict` | JSON with all 21 features, returns label, probabilities, warnings |

## CI/CD

- `.github/workflows/ci.yml`: backend tests (including model-dependent API tests, because the
  38 MB model bundle is committed) and the Angular unit tests and production build.
- `.github/workflows/pages.yml`: builds Angular and deploys it to GitHub Pages.

## Deployment limitation

GitHub Pages serves only static files. It **cannot run Flask or the model**, so on the public page
the form renders but the Predict button is disabled with a notice. Live predictions work only
locally. Public predictions would need a separately hosted HTTPS backend.

## Project structure

```
backend/   app.py, train_model.py, make_payload.py, test_pipeline.py, tests/, models/
frontend/  Angular 22 app (feature-schema.ts, prediction.service.ts, app.*)
data/      sample_inputs.csv (one non-sensitive record)
docs/      environment.txt and evidence screenshots
.github/workflows/  ci.yml, pages.yml
```