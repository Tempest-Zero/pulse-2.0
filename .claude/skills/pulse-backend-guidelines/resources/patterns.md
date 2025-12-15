# Backend Code Patterns

## Router Pattern

```python
# routers/example_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.base import get_db
from schema.example import ExampleCreate, ExampleResponse
from crud import example_crud

router = APIRouter(prefix="/examples", tags=["examples"])

@router.get("/", response_model=list[ExampleResponse])
def list_examples(db: Session = Depends(get_db)):
    return example_crud.get_all(db)

@router.post("/", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
def create_example(data: ExampleCreate, db: Session = Depends(get_db)):
    return example_crud.create(db, data)
```

## Model Pattern

```python
# models/example.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="examples")
```

## CRUD Pattern

```python
# crud/example_crud.py
from sqlalchemy.orm import Session
from models.example import Example
from schema.example import ExampleCreate

def get_all(db: Session, user_id: int = None) -> list[Example]:
    query = db.query(Example)
    if user_id:
        query = query.filter(Example.user_id == user_id)
    return query.all()

def create(db: Session, data: ExampleCreate) -> Example:
    item = Example(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
```

## Schema Pattern

```python
# schema/example.py
from pydantic import BaseModel, Field
from datetime import datetime

class ExampleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class ExampleCreate(ExampleBase):
    pass

class ExampleResponse(ExampleBase):
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
```

## Auth Dependency Pattern

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.auth import verify_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload
```

## Adding New Router to main.py

```python
# In main.py
from routers.example_router import router as example_router

app.include_router(example_router)
```
