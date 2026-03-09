from pydantic import BaseModel

class NewUser(BaseModel):
    name : str
    email : str
    password : str

class NewUserResponse(BaseModel):
    message : str

