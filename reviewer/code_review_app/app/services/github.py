import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "ghp_dummyGITHUBtoken12345")
BASE_URL = "https://api.github.com"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_pr_diff(owner: str, repo: str, pull_number: int) -> str:
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3.diff"}
        url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pull_number}"
        response = await client.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def post_pr_comment(owner: str, repo: str, issue_number: int, comment: str):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        payload = {"body": comment}
        response = await client.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status() 