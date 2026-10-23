from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import LayaEngine

app = FastAPI(title="Freelancer Protection Radar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[*] Initializing LAYA Engine for API server...")
engine = LayaEngine()

class JobAnalysisRequest(BaseModel):
    job_text: str

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "engine": "LAYA (ModernBERT)",
        "device": "CPU"
    }

@app.post("/analyze")
def analyze_job(request: JobAnalysisRequest):
    text = request.job_text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    
    analysis = engine.analyze_full_job(text)
    return analysis

@app.get("/v1/models")
def dummy_models():
    return {"data": [{"id": "laya-decision-model"}]}
