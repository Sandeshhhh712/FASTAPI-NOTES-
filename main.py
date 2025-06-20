from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from database import create_db
from schemas import UserRead, UserCreate ,Token
from database import get_session
from sqlmodel import Session
from auth import get_password_hash, authenticate , create_access_token , ACCESS_TOKEN_EXPIRE,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from models import User

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
