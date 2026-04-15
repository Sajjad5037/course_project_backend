from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext

app = FastAPI()

# -----------------------------
# CORS (allow frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Database setup
# -----------------------------
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------------
# Password hashing
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password_custom(password: str):
    return pwd_context.hash(password)

def verify_password_custom(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------------
# DB Model
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# Request schema
# -----------------------------
class LoginRequest(BaseModel):
    email: str
    password: str

# -----------------------------
# DB dependency
# -----------------------------
def get_db_session_custom():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db_session_custom)):
    user = db.query(User).filter(User.email == data.email).first()

    if user and verify_password_custom(data.password, user.password):
        return {
            "success": True,
            "message": "Login successful",
            "token": "fake-jwt-token"  # upgrade later
        }

    return {
        "success": False,
        "message": "Invalid credentials"
    }

# -----------------------------
# Seed user (run once manually)
# -----------------------------
@app.get("/create-test-user")
def create_test_user(db: Session = Depends(get_db_session_custom)):
    existing_user = db.query(User).filter(User.email == "admin@test.com").first()

    if existing_user:
        return {"message": "User already exists"}

    new_user = User(
        email="admin@test.com",
        password=hash_password_custom("1234")
    )

    db.add(new_user)
    db.commit()

    return {"message": "Test user created"}
