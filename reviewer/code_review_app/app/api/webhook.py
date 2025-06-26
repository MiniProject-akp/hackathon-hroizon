from fastapi import APIRouter, HTTPException, Request
import hmac
import hashlib
import os
from app.services.huggingface import analyze_code
from app.services.github import get_pr_diff, post_pr_comment

router = APIRouter()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret123")

def verify_signature(payload: bytes, signature: str) -> bool:
    computed = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={computed}", signature)

@router.post("/webhook")
async def webhook_endpoint(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    payload = await request.body()
    if not signature or not verify_signature(payload, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    event = request.headers.get("X-GitHub-Event")
    if event == "pull_request":
        data = await request.json()
        action = data.get("action")
        if action in ["opened", "synchronize"]:
            owner = data["repository"]["owner"]["login"]
            repo = data["repository"]["name"]
            pull_number = data["pull_request"]["number"]
            issue_number = data["pull_request"]["number"]
            try:
                diff = await get_pr_diff(owner, repo, pull_number)
                feedback = await analyze_code(diff, language=None)
                await post_pr_comment(owner, repo, issue_number, feedback)
                return {"status": "ok"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ignored"} 