from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel  
from ..models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..database import SessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import json

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

def load_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

config = load_config('ToDo/config.json')

SECRET_KEY = config.get('SECRET_KEY')
ALGORITHM = config.get('ALGORITHM')

if ALGORITHM is None:
    raise ValueError("ALGORITHM is not set in the configuration file")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    role: str
    phone_number: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
def get_db():
    """
    Dependency that returns a database session.
    
    This dependency is used as a generator to create a new database session
    and then close it when the generator is exhausted.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, 
                      password: str, 
                      db):
    """
    Authenticate a user given their username and password.

    Args:
        username (str): The user's username.
        password (str): The user's password.
        db (Session): The database session to use.

    Returns:
        Users: The user's database model if authentication is successful, otherwise False.
    """
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):   
        return False
    return user
    
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    """
    Generate an access token for the given user.

    Args:
        username (str): The username of the user.
        user_id (int): The ID of the user.
        role (str): The role of the user.
        expires_delta (timedelta): The expiry time delta for the token.

    Returns:
        str: The generated access token.
    """
    encode = {"sub": username, 
              "id": user_id, 
              "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Return the current user given the provided access token.

    Args:
        token (str): The access token to validate and extract the user from.

    Returns:
        dict: The user's details, containing the keys "username", "id", and "role".

    Raises:
        HTTPException: If the token is invalid, or if the user is not found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Could not validate credentials")
        return {"username": username, 
                "id": user_id, 
                "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Could not validate credentials")
        
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, 
                      create_user_request: CreateUserRequest):
    """
    Create a new user.

    Args:
        db (Session): The database session to use.
        create_user_request (CreateUserRequest): The user's details to create.

    Returns:
        None
    """
    create_user_model = Users(
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.hashed_password),
        role=create_user_request.role,
        is_active=True,
        phone_number = create_user_request.phone_number
    )
    
    db.add(create_user_model)
    db.commit()
    
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    """
    Login for access token.

    Args:
        form_data (OAuth2PasswordRequestForm, Depends): The form data containing the username and password.
        db (Session): The database session.

    Returns:
        dict: The access token details, including the token and token type.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    user = authenticate_user(form_data.username, 
                             form_data.password, 
                             db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")   
    token = create_access_token(user.username, 
                                user.id, 
                                user.role, 
                                timedelta(minutes=20))    
    return {'access_token': token, 'token_type': 'bearer'}
