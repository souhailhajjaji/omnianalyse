from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, scenarios, user_stories, user_stories_requirements

app = FastAPI(title="OmniAnalyse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(user_stories.router, prefix="/userstories", tags=["userstories"])
app.include_router(user_stories_requirements.router, prefix="/requirements", tags=["requirements"])

@app.get("/")
def root():
    return {"message": "OmniAnalyse API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}