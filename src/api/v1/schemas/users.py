from pydantic import BaseModel


class NewUser(BaseModel):
    name: str
    email: str
    password: str


class NewUserResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str