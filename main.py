#Librerias necesarias
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv
# Importa el router de otros lubros
from routers.encuesta import router as encuesta_router


# 1) Inicializamos la app
app = FastAPI()
load_dotenv()

# 2) Directorios base
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# 3) Montar archivos estáticos (/static/css/...)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 4) Cargar plantillas Jinja2 para páginas plantillas HTML
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 5) Rutas raíz de la aplicación
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 6) router de encuesta
app.include_router(encuesta_router)

# Rutas para otras páginas
@app.get("/paginas/{nombre_pagina}")
def inicio(nombre_pagina: str, request: Request):
    file_path = TEMPLATES_DIR / "pages" / f"{nombre_pagina}.html"
    if file_path.exists():
        return templates.TemplateResponse(f"pages/{nombre_pagina}.html", {"request": request})
    return RedirectResponse("/")
