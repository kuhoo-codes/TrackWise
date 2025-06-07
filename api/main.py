from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from pydantic import BaseModel
from typing import Optional, List
from models import Item as DBItem
import execjs
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables with defaults
PORT = int(os.getenv("PORT", "8000"))
CLIENT_URL = os.getenv("CLIENT_URL")


# Read the documentation from the JavaScript file
def read_docs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    docs_path = os.path.join(current_dir, "config", "docs.js")

    with open(docs_path, "r") as file:
        js_code = file.read()

    # Create a JavaScript context and execute the code
    ctx = execjs.compile(
        """
        const module = {exports: {}};
        const require = (path) => {
            if (path === './swagger') return require_swagger();
            if (path === './itemDocs') return require_itemDocs();
            if (path === './healthDocs') return require_healthDocs();
        };
        function require_swagger() {
            const module = {exports: {}};
            %s
            return module.exports;
        }
        function require_itemDocs() {
            const module = {exports: {}};
            %s
            return module.exports;
        }
        function require_healthDocs() {
            const module = {exports: {}};
            %s
            return module.exports;
        }
        %s
        module.exports;
    """
        % (
            open(os.path.join(current_dir, "config", "swagger.js")).read(),
            open(os.path.join(current_dir, "config", "itemDocs.js")).read(),
            open(os.path.join(current_dir, "config", "healthDocs.js")).read(),
            js_code,
        )
    )

    return ctx.eval("module.exports")


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


# Initialize FastAPI with the documentation
app = FastAPI(**read_docs())

# Create tables
Base.metadata.create_all(bind=engine)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CLIENT_URL],
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
    return {"message": "FastAPI with PostgreSQL is running!", "port": PORT}


@app.get("/api/items", response_model=List[ItemResponse])
async def get_items(db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return items


@app.post("/api/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = DBItem(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
