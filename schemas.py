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
    
class NotesCreate(BaseModel):
    title : str
    description : str
    category_id : int

class NotesRead(BaseModel):
    id : int
    title : str
    description : str
    category : str

class NoteCategoryCreate(BaseModel):
     name : str

class NoteCategoryRead(BaseModel):
    id : int
    name : str
