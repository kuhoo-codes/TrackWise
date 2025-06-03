from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from pydantic import BaseModel
from typing import Optional, List
from models import Item as DBItem

# Model for data validation
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "FastAPI with PostgreSQL is running on Mac!"}

@app.get("/api/items", response_model=List[ItemResponse])
async def get_items(db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return items

@app.post("/api/items", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = DBItem(
        name=item.name,
        description=item.description
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
