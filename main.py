from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.post("/login")
def login(data: LoginRequest):
    # TEMP: Hardcoded user (replace with DB later)
    if data.email == "admin@test.com" and data.password == "1234":
        return {
            "success": True,
            "message": "Login successful",
            "token": "fake-jwt-token"
        }
    else:
        return {
            "success": False,
            "message": "Invalid credentials"
        }
