from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Annotated

from src.database.crud.crud import CrudHelper
from src.database.crud.schema import UserNotFoundError
from ..schemas import users
from src.utils import settings

router = APIRouter(prefix="/users", tags=["Users"])
crud = CrudHelper()

# OAuth2PasswordBearer is used for handling token in request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


@router.post("/", response_model=users.NewUserResponse)
async def new_user_api(body: users.NewUser):
    crud.new_user(name=body.name, email=body.email, password=body.password)
    return users.NewUserResponse(message="Nuevo usuario creado")


@router.post("/login", response_model=users.LoginResponse)
async def login_api(body: users.LoginRequest):
    try:
        user_data = crud.login(email=body.email, password=body.password)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data["email"], "user_id": user_data["user_id"]},
            expires_delta=access_token_expires,
        )
        return users.LoginResponse(
            access_token=access_token, user=users.UserResponse(**user_data)
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/{user_id}", response_model=users.UserResponse)
async def get_user_api(user_id: int):
    try:
        user = crud.get_user(user_id=user_id)
        return users.UserResponse(**user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Placeholder for a protected route to demonstrate token usage
@router.get("/me/", response_model=users.UserResponse)
async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        user = crud.get_user(user_id=user_id)  # Re-fetch user to ensure it's valid
        if user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return users.UserResponse(**user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
