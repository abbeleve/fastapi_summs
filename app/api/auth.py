# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.email import send_verification_email, generate_verification_code
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db  # ← исправлено!
from datetime import timedelta
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Проверка email на валидность (простая)
    if "@" not in user.email:
        raise HTTPException(status_code=400, detail="Неверный формат email")

    # Создаём пользователя
    try:
        hashed_pw = get_password_hash(user.password)
        code = generate_verification_code()
        new_user = User(
            email=user.email,
            hashed_password=hashed_pw,
            is_verified=False,
            verification_code=code
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Отправляем код
    try:
        send_verification_email(user.email, code)
    except:
        # Можно удалить пользователя или оставить без кода
        raise HTTPException(status_code=500, detail="Не удалось отправить код")

    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str

@router.post("/verify")
def verify_email(request: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    if user.verification_code != request.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    user.is_verified = True
    user.verification_code = None  # удаляем код после использования
    db.commit()

    return {"message": "Email подтверждён!"}