import json
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "recommendations.json"

logger = logging.getLogger("uvicorn.error")

ERROR_LOAD_PREFIX = "No se pudieron cargar las recomendaciones"
ERROR_USER_NOT_FOUND = "Usuario no encontrado"

ALLOWED_METHODS = ["GET"]
ALLOWED_HEADERS = ["*"]


def _parse_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "*").strip()
    if raw_origins == "*":
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(
    title="Movie Recommendations API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=False,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

_recommendations: list[dict[str, Any]] | None = None
_recommendations_by_user: dict[int, dict[str, Any]] = {}
_load_error: str | None = None


def _validate_recommendations_payload(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError("data/recommendations.json debe contener una lista")
    return payload


def _build_user_index(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    index: dict[int, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or "user_id" not in item:
            raise ValueError("cada elemento debe incluir user_id")
        index[int(item["user_id"])] = item
    return index


def _load_recommendations() -> None:
    global _recommendations, _recommendations_by_user, _load_error

    try:
        logger.info("Cargando recomendaciones desde %s", DATA_FILE)
        with DATA_FILE.open("r", encoding="utf-8") as file:
            raw_payload = json.load(file)

        data = _validate_recommendations_payload(raw_payload)
        index = _build_user_index(data)

        _recommendations = data
        _recommendations_by_user = index
        _load_error = None

        logger.info(
            "Recomendaciones cargadas: %s usuarios", len(_recommendations_by_user)
        )
    except Exception as exc:
        _recommendations = None
        _recommendations_by_user = {}
        _load_error = str(exc)

        logger.exception("No se pudieron cargar las recomendaciones")


def _ensure_data_loaded() -> list[dict[str, Any]]:
    if _recommendations is None:
        detail = ERROR_LOAD_PREFIX
        if _load_error:
            detail = f"{detail}: {_load_error}"
        raise HTTPException(status_code=500, detail=detail)
    return _recommendations


@app.on_event("startup")
def startup() -> None:
    logger.info("Iniciando Movie Recommendations API")
    _load_recommendations()


@app.get("/recommendations")
def get_all_recommendations() -> list[dict[str, Any]]:
    return _ensure_data_loaded()


@app.get("/recommendations/{user_id}")
def get_user_recommendations(user_id: int) -> dict[str, Any]:
    _ensure_data_loaded()
    user_recommendations = _recommendations_by_user.get(user_id)
    if user_recommendations is None:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    return user_recommendations
