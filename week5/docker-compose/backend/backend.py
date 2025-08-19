from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import json
from redis.asyncio import Redis


# ----------------- DB setup -----------------
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# ----------------- FastAPI setup -----------------
app = FastAPI()

# ----------------- Redis setup -----------------
redis_client = None
redis = Redis(host="redis", port=6379, decode_responses=True)
# ----------------- Models -----------------
class NoteIn(BaseModel):
    title: str
    content: str

class NoteOut(NoteIn):
    id: int
    class Config:
        orm_mode = True

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)

# ----------------- Startup / Shutdown -----------------
@app.on_event("startup")
async def on_startup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # connect to redis
    global redis_client
    redis_client = await redis.from_url("redis://redis:6379", decode_responses=True)

@app.on_event("shutdown")
async def on_shutdown():
    await redis_client.close()

# ----------------- Dependency -----------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ----------------- Routes -----------------
@app.get("/")
async def home():
    return {"message": "Hello, FastAPI with Async + Redis!"}

@app.post("/notes/", response_model=NoteOut)
async def create_note(note: NoteIn, db: AsyncSession = Depends(get_db)):
    db_note = Note(**note.dict())
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)

    # Cache in Redis
    await redis_client.set(f"note:{db_note.id}", json.dumps(note.dict()))

    return db_note

@app.get("/notes/{note_id}", response_model=NoteOut)
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Try cache
    cached_note = await redis_client.get(f"note:{note_id}")
    if cached_note:
        note_dict = json.loads(cached_note)
        return {"id": note_id, **note_dict}

    # 2. DB fallback
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalars().first()

    if note:
        await redis_client.set(
            f"note:{note.id}", json.dumps({"title": note.title, "content": note.content})
        )
    return note
