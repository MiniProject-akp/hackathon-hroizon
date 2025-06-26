import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "hf_abc123DUMMYtoken")
HF_ENDPOINT = "https://api-inference.huggingface.co/models/your-username/bug-detector-finetuned"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def analyze_code(code: str, language: str | None) -> str:
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        payload = {"inputs": code}
        if language:
            payload["parameters"] = {"language": language}
        response = await client.post(HF_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        # Hugging Face API may return a list or dict depending on model
        if isinstance(result, list):
            return result[0]["generated_text"]
        return result["generated_text"] 