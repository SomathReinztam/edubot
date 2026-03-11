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


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse  # Embed UserResponse
