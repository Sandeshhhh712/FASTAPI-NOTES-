from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from database import create_db
from schemas import UserRead, UserCreate ,Token , NotesCreate , NotesRead , NoteCategoryCreate , NoteCategoryRead
from database import get_session
from sqlmodel import Session, select
from auth import get_password_hash, authenticate , create_access_token , ACCESS_TOKEN_EXPIRE,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from models import User , Notes , NoteCategory

app = FastAPI()

@app.on_event("startup")
def create_database():
    create_db()

@app.post("/register" , response_model=UserRead , tags=['User'])
def register(user:UserCreate , session: Session = Depends(get_session)):
    hashed= get_password_hash(user.hashed_password)
    new_user = User(username=user.username , email=user.email , hashed_password=hashed)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post("/token" , response_model=Token , tags=['User'])
def login(form_data : OAuth2PasswordRequestForm = Depends() , session:Session = Depends(get_session)):
    user = authenticate(form_data.username , form_data.password , session)
    if not user:
        raise HTTPException(status_code=401 , detail="Provided credentials dont match")
    access_token = create_access_token(data={"sub":user.username},expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE))
    return {'access_token':access_token , "token_type":"bearer"}

@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Note Category endpoints

@app.post("/create_note_category" , response_model=NoteCategoryRead , tags=['NoteCategory'])
def create_note_category(note_category : NoteCategoryCreate , authenticate :User = Depends(get_current_user), session : Session = Depends(get_session)):
    new_category = NoteCategory(**note_category.dict())
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category

@app.get("/get_note_category"  , tags=['NoteCategory']) 
def get_note_category(authenticate: User = Depends(get_current_user) , session: Session = Depends(get_session)):
    note_category = session.exec(select(NoteCategory)).all()
    return note_category

@app.delete("/delete_note_category/{category_id}" , tags = ['NoteCategory'])
def delete_note_category(category_id : int , authenticate: User = Depends(get_current_user) , session: Session = Depends(get_session)):
    delete = session.get(NoteCategory ,category_id)
    session.delete(delete)
    session.commit()
    return {"Deleted":"null"}

#Note Endpoints

@app.post("/create_Notes" , response_model=NotesRead , tags=['Note'])
def create_note(note:NotesCreate , session: Session = Depends(get_session) , authenticate : User = Depends(get_current_user)):
    new_note = Notes(title= note.title , description= note.description , category_id=note.category_id)
    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return new_note

@app.get("/get_notes" , tags=['Note'])
def get_note(session : Session = Depends(get_session) , authenticate: User = Depends(get_current_user)):
    notes = session.exec(select(Notes)).all()
    return notes

@app.delete("/delete_notes/{note_id}" , tags=['Note'])
def delete_note(note_id : int , session : Session = Depends(get_session) , authenticate : User = Depends(get_current_user)):
    delete = session.get(Notes , note_id)
    session.delete(delete)
    session.commit()
    return {'Deleted':'null'}

@app.get("/get_note/{note_id}" , tags=['Note'])
def get_note(note_id : int , session : Session = Depends(get_session) , authenticate : User = Depends(get_current_user)):
    single_note = session.get(Notes,note_id)
    return single_note

@app.patch("/edit_notes/{note_id}" , tags=['Note'])
def edit_note(note : Notes , note_id : int , authenticate : User =Depends(get_current_user), session : Session = Depends(get_session)):
    note_data = session.exec(select(Notes))