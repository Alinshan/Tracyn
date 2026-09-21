"""
TRACYN FastAPI Application

Boots the FastAPI app, mounts the static files + Jinja2 templates,
and includes all API routes.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .api.routes import router, set_config
from .database.database import init_db
from .utils.config import load_config
from .utils.logging import setup_logger

BASE_DIR = Path(__file__).parent

app = FastAPI(
    title="TRACYN",
    description="Trace. Detect. Analyze. Defend. — Intelligent Cyber Defence Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
static_dir = BASE_DIR / "dashboard" / "static"
templates_dir = BASE_DIR / "dashboard" / "templates"
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))


@app.on_event("startup")
async def startup():
    setup_logger()
    cfg = load_config()
    init_db(cfg)
    set_config(cfg)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(router)
