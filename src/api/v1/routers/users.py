from fastapi import APIRouter
from src.database.crud.crud import CrudHelper
from ..schemas import users

router = APIRouter(prefix="/users", tags=["Users"])
crud = CrudHelper()

@router.post("/", response_model=users.NewUserResponse)
async def new_user_api(body : users.NewUser):
    crud.new_user(name=body.name, email=body.email, password=body.password)
    return users.NewUserResponse(message="Nuevo usuario creado")
