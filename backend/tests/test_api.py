"""Stage 7 - automated API tests. Run from the project root:  python -m pytest backend/tests -v"""
import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture()
def payload():
    return json.loads((BACKEND / "test_payload.json").read_text(encoding="utf-8"))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "ok"
    assert body["n_features"] == 21


def test_features_endpoint(client):
    r = client.get("/features")
    assert r.status_code == 200
    assert len(r.get_json()["features"]) == 21


def test_predict_valid(client, payload):
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    body = r.get_json()
    assert body["prediction"] in (0, 1)
    assert body["label"] in ("No damage", "Damage")
    assert abs(body["probability_damage"] + body["probability_no_damage"] - 1) < 0.001


def test_predict_known_sample_is_no_damage(client, payload):
    body = client.post("/predict", json=payload).get_json()
    assert body["prediction"] == 0


def test_predict_allows_null_pftk9(client, payload):
    payload["PFTk9"] = None
    assert client.post("/predict", json=payload).status_code == 200


def test_predict_rejects_null_required_field(client, payload):
    payload["Elevation"] = None
    r = client.post("/predict", json=payload)
    assert r.status_code == 400
    assert "Elevation" in r.get_json()["fields"]


def test_predict_missing_field(client, payload):
    del payload["Slope"]
    r = client.post("/predict", json=payload)
    assert r.status_code == 400
    assert r.get_json()["missing"] == ["Slope"]


def test_predict_unknown_field(client, payload):
    payload["colour"] = 1
    r = client.post("/predict", json=payload)
    assert r.status_code == 400
    assert r.get_json()["unknown"] == ["colour"]


def test_predict_text_value(client, payload):
    payload["Tmax"] = "hot"
    r = client.post("/predict", json=payload)
    assert r.status_code == 400
    assert "Tmax" in r.get_json()["fields"]


def test_predict_not_json(client):
    r = client.post("/predict", data="hello", content_type="text/plain")
    assert r.status_code == 400


def test_out_of_range_gives_warning(client, payload):
    payload["Elevation"] = 99999
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    assert r.get_json()["warnings"]
