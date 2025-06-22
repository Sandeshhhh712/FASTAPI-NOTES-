from sqlmodel import SQLModel, Field , Relationship
from typing import Optional
from datetime import date, timezone

class User(SQLModel,table=True):
    id : Optional[int] = Field(default=None , primary_key=True)
    username: str = Field(index=True,unique=True)
    email : str
    hashed_password : str

class NoteCategory(SQLModel , table = True):
    id : Optional[int] = Field(default=None , primary_key=True)
    name : str

    notes: list["Notes"] = Relationship(back_populates="category")

class Notes(SQLModel , table = True):
    id : Optional[int] = Field(default=None, primary_key=True)
    title : str 
    description : str

    category_id : int = Field(foreign_key="notecategory.id")
    category : Optional[NoteCategory] = Relationship(back_populates="notes")
    date_created : date = Field(default_factory=date.today)

#we establish a reverse relattionship , a foreign key to map my two models


