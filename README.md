# API REST de recomendaciones MovieLens

API REST para exponer las recomendaciones generadas con K-Means y Apache Spark.

## Estructura

```text
api-recomendations/
  api.py
  requirements.txt
  data/
    recommendations.json
    evaluation_metrics.json
  scripts/
    build_api_data.py
  frontend/
```

## Ejecutar localmente

```powershell
python -m pip install -r requirements.txt
uvicorn api:app --host 127.0.0.1 --port 8000
```

En Docker (ver `Dockerfile`) la API expone el puerto 8080.

## Frontend de prueba

El frontend estatico esta en `front/`. Para abrirlo localmente:

```powershell
cd front
python -m http.server 5500
```

Luego visita:

```text
http://127.0.0.1:5500
```

Si la API esta desplegada en otra URL, edita `front/app.js` y cambia `API_BASE_URL`.

## Endpoints

- `GET /recommendations`: devuelve todas las recomendaciones.
- `GET /recommendations/{user_id}`: devuelve las recomendaciones de un usuario.

Ejemplos:

```powershell
curl http://127.0.0.1:8000/recommendations
curl http://127.0.0.1:8000/recommendations/1
curl http://127.0.0.1:8000/recommendations/999999
```

## Formato de respuesta

```json
{
  "user_id": 1,
  "cluster": 12,
  "recommendations": [
    {
      "movie_id": 1243,
      "movie_title": "Rosencrantz and Guildenstern Are Dead (1990)",
      "score": 5.0
    }
  ]
}
```

## Regenerar datos

Desde la raiz del proyecto principal, ejecuta primero:

```powershell
python spark-kmeans.py
```

Luego, desde esta carpeta:

```powershell
python scripts/build_api_data.py
```

El script espera que exista `../output/api_recommendations_k15.json`.

## CORS

Por defecto la API permite cualquier origen para facilitar el laboratorio. Para restringirlo:

```powershell
$env:CORS_ORIGINS = "https://tu-frontend.com,https://otro-dominio.com"
uvicorn api:app --host 127.0.0.1 --port 8000
```
