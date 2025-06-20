from pydantic import BaseModel , EmailStr

class UserCreate(BaseModel):
    username : str
    email : EmailStr
    hashed_password : str

class UserRead(BaseModel):
    id : int
    username : str
    email : EmailStr

class Token(BaseModel):
    access_token : str
    token_type : str
    