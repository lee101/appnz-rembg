import base64
import os
import threading
import urllib.request

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

PORT = int(os.environ.get("PORT", "5000"))
DEFAULT_MODEL = os.environ.get("REMBG_MODEL", "isnet-general-use")
MODELS = ["isnet-general-use", "u2net", "u2netp", "isnet-anime", "birefnet-general"]
state = {"loaded": False, "error": ""}
SESSIONS = {}
LOCK = threading.Lock()

COG_SCHEMA = {
    "outputKind": "image",
    "inputs": [
        {
            "name": "image",
            "type": "image",
            "description": "Image (https URL or data URI)",
            "required": True,
            "order": 0,
        },
        {
            "name": "model",
            "type": "string",
            "description": "Segmentation model",
            "default": DEFAULT_MODEL,
            "choices": MODELS,
            "required": False,
            "order": 1,
        },
    ],
}


def _session(name):
    if name not in SESSIONS:
        from rembg import new_session

        SESSIONS[name] = new_session(name)
    return SESSIONS[name]


def _load():
    try:
        _session(DEFAULT_MODEL)
        state["loaded"] = True
    except Exception as e:
        state["error"] = str(e)


def fetch_bytes(v):
    if not isinstance(v, str) or not v:
        raise HTTPException(status_code=400, detail="missing image")
    if v.startswith("data:"):
        return base64.b64decode(v.partition(",")[2])
    if v.startswith(("http://", "https://")):
        with urllib.request.urlopen(v, timeout=120) as r:
            return r.read()
    return base64.b64decode(v)


app = FastAPI(title="appnz-rembg", openapi_url=None)


@app.on_event("startup")
def startup():
    threading.Thread(target=_load, daemon=True).start()


@app.get("/health-check")
def health_check():
    if state["error"]:
        return {"status": "SETUP", "error": state["error"]}
    return {"status": "READY" if state["loaded"] else "SETUP"}


@app.get("/healthz")
def healthz():
    if not state["loaded"]:
        return JSONResponse({"status": "loading", "error": state["error"]}, status_code=503)
    return {"status": "ok"}


@app.get("/openapi.json")
def openapi_json():
    return COG_SCHEMA


@app.post("/predictions")
def predictions(payload: dict):
    if not state["loaded"]:
        return JSONResponse(
            {"status": "failed", "error": state["error"] or "model loading"},
            status_code=503,
        )
    body = payload.get("input") or {}
    model = body.get("model") or DEFAULT_MODEL
    if model not in MODELS:
        return JSONResponse(
            {"status": "failed", "error": f"model must be one of: {', '.join(MODELS)}"},
            status_code=400,
        )
    try:
        from rembg import remove

        data = fetch_bytes(body.get("image"))
        with LOCK:
            out = remove(data, session=_session(model))
        b64 = base64.b64encode(out).decode("ascii")
        return {"status": "succeeded", "output": f"data:image/png;base64,{b64}"}
    except HTTPException as e:
        return JSONResponse({"status": "failed", "error": e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse({"status": "failed", "error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
