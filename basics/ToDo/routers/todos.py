from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
from starlette import status

router = APIRouter()

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

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str=Field(min_length=3, max_length=100)
    priority: int=Field(gt=0, lt=6)
    complete: bool 
    
@router.get("/", status_code = status.HTTP_200_OK)
async def read_all(user: user_dependency, 
                   db: db_dependency):
    """
    Return all todos for the current user.

    This endpoint is protected by the same authentication as the other endpoints in this router.

    Args:
    - user (dict): The currently authenticated user, passed in via the `user_dependency`.
    - db (Session): The database session to use, passed in via the `db_dependency`.

    Returns:
    - List[Todos]: A list of all todos for the current user.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,
                    db: db_dependency, 
                    id: int = Path(gt=0)):
    """
    Return a single todo given the id.

    This endpoint is protected by the same authentication as the other endpoints in this router.

    Args:
    - user (dict): The currently authenticated user, passed in via the `user_dependency`.
    - db (Session): The database session to use, passed in via the `db_dependency`.
    - id (int): The id of the todo to retrieve, passed in via the path parameter.

    Returns:
    - Todos: The todo object for the given id, or a 404 if not found.
    """
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo_model


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, 
                      db: db_dependency, 
                      todoRequest: TodoRequest):
    """
    Create a new todo.

    This endpoint is protected by the same authentication as the other endpoints in this router.

    Args:
    - user (dict): The currently authenticated user, passed in via the `user_dependency`.
    - db (Session): The database session to use, passed in via the `db_dependency`.
    - todoRequest (TodoRequest): The request body containing the details of the new todo.

    Returns:
    - Todos: The newly created todo object.

    Raises:
    - HTTPException: If the user is not authenticated.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = Todos(**todoRequest.dict(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

    
@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency, 
                      todoRequest: TodoRequest, 
                      id: int=Path(gt=0)):
    """
    Update a todo with the provided details.

    This endpoint is protected by the same authentication as the other endpoints in this router.

    Args:
    - user (dict): The currently authenticated user, passed in via the `user_dependency`.
    - db (Session): The database session to use, passed in via the `db_dependency`.
    - todoRequest (TodoRequest): The request body containing the details to update the todo.
    - id (int): The id of the todo to update, passed in via the path parameter.

    Returns:
    - Todos: The updated todo object.

    Raises:
    - HTTPException: If the user is not authenticated or if the todo is not found.
    """
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="todo not found")
    todo_model.title = todoRequest.title
    todo_model.description = todoRequest.description
    todo_model.priority = todoRequest.priority
    todo_model.complete = todoRequest.complete
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, 
                      db: db_dependency, 
                      id: int = Path(gt=0)):
    """
    Delete a todo with the given id.

    This endpoint is protected by the same authentication as the other endpoints in this router.

    Args:
    - user (dict): The currently authenticated user, passed in via the `user_dependency`.
    - db (Session): The database session to use, passed in via the `db_dependency`.
    - id (int): The id of the todo to delete, passed in via the path parameter.

    Returns:
    - Todos: The deleted todo object.

    Raises:
    - HTTPException: If the user is not authenticated or if the todo is not found.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_model = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="todo not found")
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
    db.refresh(todo_model)
    return todo_model
