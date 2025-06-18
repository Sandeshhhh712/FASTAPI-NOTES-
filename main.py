from fastapi import FastAPI , Depends, HTTPException

#database related
from sqlmodel import SQLModel , create_engine, Session , Field , select
from typing import Annotated
from datetime import date
from pydantic import BaseModel

#security related
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "c11f063cc287cd50b8c2533d4de602de81ec2fb8f46c024735939e989be9b7a6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token :str
    token_type :str

#Database Models

class UserBase(SQLModel):
    username : str = Field(index=True)
    email : str | None = Field(default=None)

class User(UserBase , table=True):
    id :int | None = Field(default=None , primary_key=True)
    password : str

class Userinput(UserBase):
    password: str
        

class NotesBase(SQLModel):
    title : str | None = None
    description : str | None = None

class Notes(NotesBase , table = True):
    id: int | None = Field(default=None, primary_key=True)
    date_added : date = Field(default_factory=date.today)

class NotesCreate(NotesBase):
    date_added : date = Field(default_factory=date.today)

class NoteUpdate(NotesBase):
    pass


#Database settings

database_name = "Notes.db"
database_url = f"sqlite:///{database_name}"
connect_args = {'check_same_thread':False}
engine = create_engine(database_url , connect_args=connect_args)

#Dependencies

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDependency = Annotated[Session , Depends(get_session)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(session: SessionDependency , username:str , password: str):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404 , detail=('User Not Found'))
    if not verify_password(password, user.password):
        raise HTTPException(status_code=404 , detail=('The id and password doesnt match'))
    return user


# Fastapi instance

app = FastAPI()

@app.on_event("startup")
def create_database():
    create_db()


# Endpoints for note app

@app.post("/create_notes", tags=['Note'], response_model=Notes)
def create_note(note: NotesCreate, session: SessionDependency):
    new_note = Notes(**note.dict())  # we convert a non table like model data into the format of our note model.
    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return new_note


@app.get('/get_notes' , tags=['Note'] , response_model=list[Notes])
def get_note(session: SessionDependency):
    notes = session.exec(select(Notes)).all()
    return notes

@app.get('/get_notes/{notes_id}' , tags=['Note'], response_model=Notes)
def get_notes(notes_id : int,session: SessionDependency):
    note = session.get(Notes , notes_id)
    if not note:
        raise HTTPException (status_code=404 , detail="Note Not Found")
    return note

@app.delete('/delete_note/{notes_id}' , tags=['Note'])
def delete_notes(notes_id : int , session : SessionDependency):
    note = session.get(Notes , notes_id)
    if not note:
        raise HTTPException (status_code=404 , detail="Note not found")
    session.delete(note)
    session.commit()
    return{'Deleted':True}

@app.patch('/update_note/{notes_id}', tags=['Note'] , response_model=Notes)
def update_note(notes_id : int , session : SessionDependency , Note: NoteUpdate):
    note = session.get(Notes,notes_id)
    if not note:
        raise HTTPException (status_code=404 , detail= "Note does not exist")
    note_data = Note.model_dump(exclude_unset=True)
    note.sqlmodel_update(note_data)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

# Endpoints for user 

@app.post('/user_register' , tags=['User'], response_model=UserBase)
def register(usermodel : Userinput , session:SessionDependency):
    hash_password= get_password_hash(usermodel.password)
    usermodel.password = hash_password
    new_user = User(**usermodel.dict())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post('/user_login', tags=['User'])
def login(usermodel: Userinput, session: SessionDependency):
    user = authenticate_user(session, usermodel.username, usermodel.password)
    return {"message": "Welcome", "username": user.username}
