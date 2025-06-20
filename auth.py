from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session , select
from models import User
from jose import JWTError , jwt
from fastapi import Depends, HTTPException
from database import get_session

SECRET_KEY = "cc678a716a5ffb4a06141799d45c4e6b0c09379ff6fd0baefc62ac67cc0563e6"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = 30

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate(username: str , password: str , session: Session):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
        
def create_access_token(data:dict , expires_delta : timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+(expires_delta or timedelta(minutes=15))
    to_encode.update({'exp':expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

#In jwt our token has 3 things , the signed user , expiry date and some random text 
# in create access token function , we first copy the user data which will be signed in the token , for example username and then we add the expiry date and time in it and make it a signed token

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
             raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    except JWTError:
         raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
         raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return user

#In here the oauth2_scheme is responsible for extracting token from the authorization header , the session establishes a database connection , and the credential_exception is for multiple error handles 
# payload uses jwt function to decode the token searching for the u