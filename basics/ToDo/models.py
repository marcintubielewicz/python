from .database import Base 
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users(Base):
    __tablename__="users"
    
    id = Column(Integer, primary_key=True, index=True)  
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String)


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Integer, default=1)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey(Users.id))