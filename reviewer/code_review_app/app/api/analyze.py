from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.huggingface import analyze_code

router = APIRouter()

class CodeInput(BaseModel):
    code: str
    language: str | None = None

@router.post("/analyze")
async def analyze_endpoint(input: CodeInput):
    if len(input.code) > 10_000:
        raise HTTPException(status_code=400, detail="Code too long")
    try:
        feedback = await analyze_code(input.code, input.language)
        return {"markdown_feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 