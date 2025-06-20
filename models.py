from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel,table=True):
    id :int = Field(default=None , primary_key=True)
    username: str = Field(index=True,unique=True)
    email : str
    hashed_password : str