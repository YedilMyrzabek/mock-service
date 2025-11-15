from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный кэш для аннотаций
ANNOTATIONS = {}


@app.on_event("startup")
def load_annotations():
    """
    Один раз загружаем JSON при старте приложения.
    Имя файла подставь своё (где лежит твой JSON).
    """
    global ANNOTATIONS
    json_path = Path("selected_annotations.json")  # например, в одной папке с main.py
    if not json_path.exists():
        raise RuntimeError(f"JSON file not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as f:
        ANNOTATIONS = json.load(f)


@app.post("/inspect_pd")
async def inspect_pd(file: UploadFile = File(...)):
    """
    Принимаем PDF-файл.
    Берём его имя и ищем в ANNOTATIONS.
    """
    filename = file.filename  # например "отр-22.pdf"
    # Можно дополнительно нормализовать, если надо:
    # filename = filename.strip()

    if filename not in ANNOTATIONS:
        # Ничего не нашли — возвращаем 404
        raise HTTPException(status_code=404, detail=f"Annotations for file '{filename}' not found")

    # Возвращаем только кусок, относящийся к этому файлу
    return {filename: ANNOTATIONS[filename]}
