# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.models.user import Base
from app.api.auth import router as auth_router
from app.core.database import engine

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Шаблоны и статика
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
static_dir = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # (инициализация БД остаётся, если нужна)
    yield

app = FastAPI(title="Meeting AI Service", lifespan=lifespan)

# Подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.include_router(auth_router)

# Эндпоинты для UI
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# app/main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.core.security import decode_token  # у тебя уже есть

# ... остальной код ...

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, token: str = None):
    # Проверяем, авторизован ли пользователь
    if not token:
        token = request.cookies.get("access_token")
    
    if token:
        try:
            # Убираем "Bearer " если есть
            if token.startswith("Bearer "):
                token = token[7:]
            user_data = decode_token(token)
            return templates.TemplateResponse("home.html", {
                "request": request,
                "user_email": user_data.email,
                "access_token": token
            })
        except:
            pass
    
    # Если не авторизован — редирект на логин
    return templates.TemplateResponse("login.html", {"request": request})