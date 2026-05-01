import json
import shutil
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
API_DIR = SCRIPT_DIR.parent
PROJECT_DIR = API_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "output"
DATA_DIR = API_DIR / "data"

BEST_K = 15
API_READY_SOURCE = OUTPUT_DIR / f"api_recommendations_k{BEST_K}.json"
METRICS_SOURCE = OUTPUT_DIR / "evaluation_metrics.json"
RECOMMENDATIONS_TARGET = DATA_DIR / "recommendations.json"
METRICS_TARGET = DATA_DIR / "evaluation_metrics.json"


def validate_recommendations(data: Any) -> None:
    if not isinstance(data, list):
        raise ValueError("El JSON de recomendaciones debe ser una lista")

    required_user_keys = {"user_id", "cluster", "recommendations"}
    required_movie_keys = {"movie_id", "movie_title", "score"}

    for user_item in data:
        if not isinstance(user_item, dict):
            raise ValueError("Cada usuario debe ser un objeto JSON")
        missing_user_keys = required_user_keys - user_item.keys()
        if missing_user_keys:
            raise ValueError(f"Faltan campos de usuario: {sorted(missing_user_keys)}")
        if not isinstance(user_item["recommendations"], list):
            raise ValueError("recommendations debe ser una lista")
        for recommendation in user_item["recommendations"]:
            if not isinstance(recommendation, dict):
                raise ValueError("Cada recomendacion debe ser un objeto JSON")
            missing_movie_keys = required_movie_keys - recommendation.keys()
            if missing_movie_keys:
                raise ValueError(f"Faltan campos de recomendacion: {sorted(missing_movie_keys)}")


def main() -> None:
    if not API_READY_SOURCE.exists():
        raise SystemExit(
            f"No existe {API_READY_SOURCE}.\n"
            "Primero vuelve a ejecutar spark-kmeans.py para generar el JSON API-ready."
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with API_READY_SOURCE.open("r", encoding="utf-8") as source_file:
        recommendations = json.load(source_file)
    validate_recommendations(recommendations)

    with RECOMMENDATIONS_TARGET.open("w", encoding="utf-8") as target_file:
        json.dump(recommendations, target_file, indent=2, ensure_ascii=False)
        target_file.write("\n")

    if METRICS_SOURCE.exists():
        shutil.copyfile(METRICS_SOURCE, METRICS_TARGET)

    print(f"Recomendaciones copiadas: {RECOMMENDATIONS_TARGET}")
    print(f"Usuarios incluidos: {len(recommendations)}")
    if METRICS_TARGET.exists():
        print(f"Metricas copiadas: {METRICS_TARGET}")


if __name__ == "__main__":
    main()
