from pydantic import BaseModel

class UserCreate(BaseModel):
    username:str
    password:str

class UserLogin(BaseModel):
    username:str
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    role:str

class UserUpdate(BaseModel):
    role:str

class PasswordUpdate(BaseModel):
    password:str

class RefreshTokenRequest(BaseModel):
    refresh_token:str