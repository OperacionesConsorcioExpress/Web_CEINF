from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

# Base de directorios
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Montar recursos estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Cargar plantillas HTML
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Ruta raíz
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rutas para otras páginas
@app.get("/paginas/{nombre_pagina}")
def inicio(nombre_pagina: str, request: Request):
    file_path = TEMPLATES_DIR / "pages" / f"{nombre_pagina}.html"
    if file_path.exists():
        return templates.TemplateResponse(f"pages/{nombre_pagina}.html", {"request": request})
    return RedirectResponse("/")
