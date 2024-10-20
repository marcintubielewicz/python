from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Users
from database import SessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)

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
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=8)
    
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency,
                   db: db_dependency):
    
    """
    Return the user's details given the provided access token.

    Args:
        user (dict): The currently authenticated user, passed in via the `user_dependency`.
        db (Session): The database session to use, passed in via the `db_dependency`.

    Returns:
        Users: The user's database model, or a 401 if authentication failed.

    Raises:
        HTTPException: If authentication failed.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          user_verification: UserVerification):
    """
    Change the user's password given the provided access token and verification details.

    Args:
        user (dict): The currently authenticated user, passed in via the `user_dependency`.
        db (Session): The database session to use, passed in via the `db_dependency`.
        user_verification (UserVerification): The verification details, containing the old and new passwords.

    Returns:
        None

    Raises:
        HTTPException: If authentication failed or if the old password is incorrect.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()