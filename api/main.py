"""
COGNIGUARD REST API
Run with: uvicorn api.main:app --reload
Test at: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
from pathlib import Path

# Tell Python where to find cogniguard
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import ClaimAnalyzer
from cogniguard.claim_analyzer import ClaimAnalyzer


# What user sends to us
class AnalyzeRequest(BaseModel):
    text: str


# What we send back
class AnalyzeResponse(BaseModel):
    text: str
    is_perturbed: bool
    robustness_score: float
    perturbations_count: int
    perturbations: List[dict]
    normalized_claim: str
    recommendations: List[str]


# Create the API
app = FastAPI(
    title="CogniGuard API",
    description="AI Safety & Misinformation Detection API",
    version="1.0.0",
)

# Allow requests from any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create analyzer once
analyzer = None

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = ClaimAnalyzer()
    return analyzer


# HOME PAGE
@app.get("/")
async def home():
    return {
        "message": "Welcome to CogniGuard API!",
        "docs": "Go to /docs for documentation",
        "health": "Go to /health to check status",
    }


# HEALTH CHECK
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "API is running!"
    }

@app.get("/perturbation-types")
async def get_perturbation_types():
#"""
#Learn about the 6 perturbation types.

#text

#Visit: http://localhost:8000/perturbation-types
#"""

    return {
    "title": "The 6 Perturbation Types",
    "based_on": "ACL 2025 Paper: 'When Claims Evolve'",
    "total_types": 6,
    "types": [
        {
            "number": 1,
            "name": "CASING",
            "emoji": "🔤",
            "description": "Changing text capitalization",
            "low_noise": "TrueCasing (normal)",
            "high_noise": "ALL UPPERCASE or all lowercase",
            "example": "THE VACCINE IS SAFE!!!",
            "why_used": "Some systems are case-sensitive"
        },
        {
            "number": 2,
            "name": "TYPOS",
            "emoji": "✏️",
            "description": "Intentional spelling errors",
            "low_noise": "Minor typo (vacine)",
            "high_noise": "Leetspeak (v4cc1ne), slang (vaxx)",
            "example": "Th3 v4ccine is s4fe",
            "why_used": "Keyword filters look for exact matches"
        },
        {
            "number": 3,
            "name": "NEGATION",
            "emoji": "🚫",
            "description": "Adding negative words",
            "low_noise": "Single negation (is not)",
            "high_noise": "Double negation (not untrue)",
            "example": "It is not untrue that it works",
            "why_used": "AI gets confused by multiple negatives"
        },
        {
            "number": 4,
            "name": "ENTITY_REPLACEMENT",
            "emoji": "👤",
            "description": "Replacing names with vague terms",
            "low_noise": "1 entity replaced",
            "high_noise": "All entities replaced",
            "example": "According to the agency...",
            "why_used": "Fact-checkers search for specific names"
        },
        {
            "number": 5,
            "name": "LLM_REWRITE",
            "emoji": "🤖",
            "description": "AI paraphrasing",
            "low_noise": "Slight rewording",
            "high_noise": "Complete restructure",
            "example": "Furthermore, it is worth noting that...",
            "why_used": "Each rewrite is unique, can't match database"
        },
        {
            "number": 6,
            "name": "DIALECT",
            "emoji": "🌍",
            "description": "Regional English variants",
            "variants": [
                "African American English (AAE)",
                "Nigerian Pidgin",
                "Singlish (Singapore)",
                "Jamaican Patois"
            ],
            "example_aae": "The vaccine be safe fr fr no cap",
            "example_pidgin": "Na true talk, the vaccine dey safe",
            "why_used": "Most AI trained only on Standard English"
        }
    ]
}



# MAIN ANALYZE ENDPOINT
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        claim_analyzer = get_analyzer()
        result = claim_analyzer.analyze(request.text)
        
        perturbations = []
        for p in result.perturbations_detected:
            perturbations.append({
                "type": p.perturbation_type.value,
                "noise_level": p.noise_budget.value,
                "confidence": round(p.confidence, 2),
                "explanation": p.explanation,
                "evidence": p.evidence,
            })
        
        return AnalyzeResponse(
            text=request.text,
            is_perturbed=result.is_perturbed,
            robustness_score=round(result.robustness_score, 2),
            perturbations_count=len(perturbations),
            perturbations=perturbations,
            normalized_claim=result.normalized_claim,
            recommendations=result.recommendations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# EXAMPLES
@app.get("/examples")
async def examples():
    return {
        "examples": [
            {"text": "The vaccine is safe.", "expected": "CLEAN"},
            {"text": "THE VACCINE IS SAFE!!!", "expected": "CASING"},
            {"text": "Th3 v4ccine is s4fe", "expected": "TYPOS"},
            {"text": "It is not untrue that it works", "expected": "NEGATION"},
            {"text": "The vaccine be safe fr fr no cap", "expected": "DIALECT"},
        ]
    }


# RUN THE API
if __name__ == "__main__":
    import uvicorn
    print("Starting CogniGuard API...")
    print("Go to: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)