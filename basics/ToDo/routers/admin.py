from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from starlette import status
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
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

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,
                   db: db_dependency):
    """
    Return all todos in the database.
    
    This endpoint is only accessible to administrators.
    """
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, 
                            detail="Unauthorized")
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    
    """
    Delete a todo by id.
    
    This endpoint is only accessible to administrators.
    
    Args:
    - user (dict): The currently authenticated user.
    - db (Session): The database session.
    - todo_id (int): The id of the todo to be deleted.
    """
    
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, 
                            detail="Unauthorized")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()