from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel  
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWSError

router = APIRouter()

SECRET_KEY = '77c70fd8c583d8bd2a4f782ba680fe1b7051a81086c8474dd25aaf81ed35ecbf' # openssl rand -hex 32
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    role: str
    
class token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):   
        return False
    return user
    
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    # if expires_delta:
    #     expires = datetime.now(timezone.utc) + expires_delta
    # else:
    #     expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
        
@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, 
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    db.add(create_user_model)
    db.commit()
    
@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")   
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))    
    return {'access_token': token, 'token_type': 'bearer'}
