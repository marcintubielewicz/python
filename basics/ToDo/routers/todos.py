from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from routers import auth

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str=Field(min_length=3, max_length=100)
    priority: int=Field(gt=0, lt=6)
    complete: bool 
    
    
@router.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@router.get("/todo/{id}")
async def read_todo(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo_model


@router.post("/todo, status_code=status.HTTP_201_CREATED")
async def create_todo(db: db_dependency, todoRequest: TodoRequest):
    todo_model = Todos(**todoRequest.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

    
@router.put("/todo/{id}")
async def update_todo(db: db_dependency, todoRequest: TodoRequest, id: int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
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

@router.delete("/todo/{id}")
async def delete_todo(db: db_dependency, todoRequest: TodoRequest, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="todo not found")
    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
    db.refresh(todo_model)
    return todo_model