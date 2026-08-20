"""HTTP wrapper around the detection module, for the UI to call.

Thin layer over inference_test.predict()/predict_batch() -- no inference
logic duplicated here. config.py's paths (OUTPUT_DIR, dataset paths) are all
relative to the repo root, so run this from the repo root with --app-dir
(not from src/training/, which would resolve those paths wrong):

    uvicorn serve:app --reload --port 8000 --app-dir src/training
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import OUTPUT_DIR
from inference_test import DEFAULT_THRESHOLD, predict, predict_batch
from mitigate import mitigate as run_mitigation

METRICS_PATH = Path(OUTPUT_DIR) / "eval_metrics.json"

app = FastAPI(title="BiasLens detection service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectRequest(BaseModel):
    text: str
    threshold: float = DEFAULT_THRESHOLD


class DetectBatchRequest(BaseModel):
    texts: list[str]
    threshold: float = DEFAULT_THRESHOLD


class MitigateRequest(BaseModel):
    text: str
    label: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/detect")
def detect(req: DetectRequest) -> dict:
    return predict(req.text, threshold=req.threshold)


@app.post("/detect/batch")
def detect_batch(req: DetectBatchRequest) -> list[dict]:
    return predict_batch(req.texts, threshold=req.threshold)


@app.post("/mitigate")
def mitigate(req: MitigateRequest) -> dict:
    try:
        return run_mitigation(req.text, label=req.label)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/metrics")
def metrics() -> dict:
    if not METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="No eval_metrics.json yet -- run evaluate.py first")
    with open(METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)
