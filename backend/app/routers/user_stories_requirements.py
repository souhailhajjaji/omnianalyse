from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.groq_service import generate_user_stories_from_requirements
import os

router = APIRouter()

USER_STORIES_FILE = "/home/souhail/projectss/omnianalyse/user-stories.md"


class RequirementsInput(BaseModel):
    content: str
    save_to_file: bool = True


@router.post("/generate-from-requirements")
async def generate_user_stories_from_text_requirements(body: RequirementsInput):
    """
    Generate user stories from text requirements using AI (llama-3.1-8b-instant).
    
    Accepts:
    - Text requirements in French or English
    - Format: .md, plain text, or any specification format
    
    Returns:
    - User stories in Agile format
    - Automatically saved to user-stories.md if save_to_file=True
    """
    if not body.content or not body.content.strip():
        raise HTTPException(status_code=400, detail="No requirements content provided")
    
    try:
        ai_output = await generate_user_stories_from_requirements(body.content)
        
        user_stories = ai_output
        
        if body.save_to_file:
            with open(USER_STORIES_FILE, 'w', encoding='utf-8') as f:
                f.write(user_stories)
        
        return {
            "status": "success",
            "user_stories": user_stories,
            "saved": body.save_to_file,
            "file_path": USER_STORIES_FILE if body.save_to_file else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-from-text")
async def generate_from_text(requirements: str):
    """
    Simple endpoint that accepts raw text requirements.
    
    Query parameter:
    - requirements: Text string with requirements
    
    Example:
    /userstories/generate-from-text?requirements=L'utilisateur doit pouvoir se connecter...
    """
    if not requirements or not requirements.strip():
        raise HTTPException(status_code=400, content={"error": "No requirements provided"})
    
    try:
        ai_output = await generate_user_stories_from_requirements(requirements)
        
        with open(USER_STORIES_FILE, 'w', encoding='utf-8') as f:
            f.write(ai_output)
        
        return {
            "status": "success",
            "user_stories": ai_output,
            "saved": True,
            "file_path": USER_STORIES_FILE
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))