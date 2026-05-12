from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str


class SFDInput(BaseModel):
    content: str
    min_stories: int = 60
    save_to_file: bool = True


class SFDAnalysisResult(BaseModel):
    project_name: str
    actors: list
    modules: list
    functional_requirements: list
    user_stories_count: int