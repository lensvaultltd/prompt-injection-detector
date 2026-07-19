from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re

app = FastAPI(title="LLM Security Firewall")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

# Mock LLM API Endpoint (Internal Network Only)
LLM_BACKEND_URL = "http://llm-api:8080/api/chat"

# --- Security Heuristics Engine ---
def analyze_prompt(prompt: str) -> dict:
    prompt_lower = prompt.lower()
    
    # 1. Detect common Jailbreak signatures (DAN, roleplay overrides)
    jailbreak_signatures = ["ignore all previous", "you are no longer", "do anything now", "system override"]
    for sig in jailbreak_signatures:
        if sig in prompt_lower:
            return {"is_safe": False, "reason": f"Jailbreak signature detected: '{sig}'"}
            
    # 2. Detect System Prompt Extraction attempts
    extraction_regex = re.compile(r'(repeat|output|show|print|what is)(.*)(system prompt|instructions|above this line)')
    if extraction_regex.search(prompt_lower):
        return {"is_safe": False, "reason": "System prompt extraction attempt detected"}
        
    # 3. Detect potentially malicious code injection (very naive mock)
    if "os.system(" in prompt_lower or "eval(" in prompt_lower or "<script>" in prompt_lower:
        return {"is_safe": False, "reason": "Code injection attempt detected"}

    return {"is_safe": True, "reason": "Prompt passed security checks"}

@app.post("/api/v1/gateway")
def llm_gateway(req: PromptRequest):
    # 1. Intercept and Analyze
    security_analysis = analyze_prompt(req.prompt)
    
    if not security_analysis["is_safe"]:
        # Block request and return security alert
        return {
            "status": "BLOCKED",
            "security_alert": security_analysis["reason"],
            "response": None
        }
        
    # 2. Forward safe prompt to the vulnerable backend
    try:
        llm_res = requests.post(LLM_BACKEND_URL, json={"prompt": req.prompt})
        llm_data = llm_res.json()
        
        return {
            "status": "ALLOWED",
            "security_alert": None,
            "response": llm_data["response"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="LLM Backend Unreachable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
