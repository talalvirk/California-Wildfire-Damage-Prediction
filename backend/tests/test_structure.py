from pathlib import Path


def test_source_files_exist():
    root = Path(__file__).resolve().parents[2]
    assert (root / "backend/app.py").exists()
    assert (root / "frontend/package.json").exists()
    assert (root / "README.md").exists()


def test_model_artifacts_are_committed():
    root = Path(__file__).resolve().parents[2]
    assert (root / "backend/models/model_bundle.joblib").exists()
    assert (root / "backend/test_payload.json").exists()
    assert (root / "backend/feature_metadata.json").exists()