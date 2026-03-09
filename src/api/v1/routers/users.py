from fastapi import APIRouter, HTTPException
from src.database.crud.crud import CrudHelper
from src.database.crud.schema import UserNotFoundError
from ..schemas import users

router = APIRouter(prefix="/users", tags=["Users"])
crud = CrudHelper()


@router.post("/", response_model=users.NewUserResponse)
async def new_user_api(body: users.NewUser):
    crud.new_user(name=body.name, email=body.email, password=body.password)
    return users.NewUserResponse(message="Nuevo usuario creado")


@router.post("/login", response_model=users.UserResponse)
async def login_api(body: users.LoginRequest):
    try:
        user = crud.login(email=body.email, password=body.password)
        return users.UserResponse(**user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/{user_id}", response_model=users.UserResponse)
async def get_user_api(user_id: int):
    try:
        user = crud.get_user(user_id=user_id)
        return users.UserResponse(**user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
