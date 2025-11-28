"""
=============================================================================
COGNIGUARD API
=============================================================================
This API allows other applications to use CogniGuard's threat detection.

HOW TO RUN:
    uvicorn api:app --reload --port 8000

HOW TO TEST:
    Open browser: http://localhost:8000/docs
=============================================================================
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging

# Import our detection engine
from core.detection_engine import CogniGuardEngine, ThreatLevel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# CREATE THE API
# =============================================================================

app = FastAPI(
    title="🛡️ CogniGuard API",
    description="AI Security Platform - Detect threats in AI communications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allow any website to use this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start the detection engine
logger.info("🛡️ Starting CogniGuard Engine...")
engine = CogniGuardEngine()
logger.info("✅ Engine ready!")


# =============================================================================
# DATA MODELS - What the API expects and returns
# =============================================================================

class AnalyzeRequest(BaseModel):
    """What you send to analyze a message"""
    message: str = Field(..., description="The message to check for threats")
    sender_role: Optional[str] = Field(default="user", description="Who sent it")
    include_details: Optional[bool] = Field(default=True, description="Include stage details")


class ThreatInfo(BaseModel):
    """Information about a detected threat"""
    level: str
    type: str
    confidence: float
    explanation: str


class AnalyzeResponse(BaseModel):
    """What the API returns after analysis"""
    success: bool
    threat_detected: bool
    threat: ThreatInfo
    recommendations: List[str]
    stage_results: Optional[Dict] = None
    analyzed_at: str


class QuickScanRequest(BaseModel):
    """Simple request for quick check"""
    text: str = Field(..., description="Text to scan")


class QuickScanResponse(BaseModel):
    """Simple response for quick check"""
    is_safe: bool
    threat_level: str
    message: str


class BatchRequest(BaseModel):
    """Request to check multiple messages"""
    messages: List[str] = Field(..., description="List of messages to check")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    engine_loaded: bool
    version: str
    timestamp: str


# =============================================================================
# API ENDPOINTS - The "phone numbers" other apps call
# =============================================================================

@app.get("/", tags=["General"])
async def welcome():
    """Welcome page - shows API is running"""
    return {
        "message": "🛡️ Welcome to CogniGuard API",
        "status": "running",
        "version": "1.0.0",
        "docs": "Visit /docs for interactive documentation",
        "endpoints": {
            "/health": "Check if API is running",
            "/analyze": "Analyze a message for threats",
            "/quick-scan": "Quick yes/no threat check",
            "/batch-analyze": "Check multiple messages",
            "/check-injection": "Check for prompt injection",
            "/check-data-leak": "Check for data leaks"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Check if the API is healthy"""
    return HealthResponse(
        status="healthy",
        engine_loaded=engine.initialized,
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Threat Detection"])
async def analyze_message(request: AnalyzeRequest):
    """
    🔍 Analyze a message for threats
    
    Send a message and get back:
    - Whether a threat was detected
    - What type of threat
    - How confident we are
    - What to do about it
    """
    try:
        logger.info(f"📨 Analyzing: {request.message[:50]}...")
        
        # Run detection
        result = engine.detect(
            message=request.message,
            sender_context={"role": request.sender_role, "intent": "unknown"},
            receiver_context={"role": "assistant"}
        )
        
        # Build response
        threat_info = ThreatInfo(
            level=result.threat_level.name,
            type=result.threat_type,
            confidence=result.confidence,
            explanation=result.explanation
        )
        
        threat_detected = result.threat_level != ThreatLevel.SAFE
        
        logger.info(f"✅ Result: {result.threat_level.name}")
        
        return AnalyzeResponse(
            success=True,
            threat_detected=threat_detected,
            threat=threat_info,
            recommendations=result.recommendations,
            stage_results=result.stage_results if request.include_details else None,
            analyzed_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/quick-scan", response_model=QuickScanResponse, tags=["Threat Detection"])
async def quick_scan(request: QuickScanRequest):
    """
    ⚡ Quick scan - simple yes/no threat check
    
    Fast way to check if something is safe.
    """
    try:
        result = engine.detect(
            message=request.text,
            sender_context={"role": "user", "intent": "unknown"},
            receiver_context={"role": "assistant"}
        )
        
        is_safe = result.threat_level in [ThreatLevel.SAFE, ThreatLevel.LOW]
        
        return QuickScanResponse(
            is_safe=is_safe,
            threat_level=result.threat_level.name,
            message="✅ Safe" if is_safe else f"⚠️ Threat: {result.threat_type}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.post("/batch-analyze", tags=["Threat Detection"])
async def batch_analyze(request: BatchRequest):
    """
    📦 Analyze multiple messages at once
    
    Send a list of messages, get back analysis for all.
    """
    try:
        results = []
        threats_found = 0
        
        for message in request.messages:
            result = engine.detect(
                message=message,
                sender_context={"role": "user", "intent": "unknown"},
                receiver_context={"role": "assistant"}
            )
            
            is_threat = result.threat_level not in [ThreatLevel.SAFE, ThreatLevel.LOW]
            if is_threat:
                threats_found += 1
            
            results.append({
                "message": message[:50] + "..." if len(message) > 50 else message,
                "threat_level": result.threat_level.name,
                "threat_type": result.threat_type,
                "is_threat": is_threat
            })
        
        return {
            "success": True,
            "total_messages": len(request.messages),
            "threats_found": threats_found,
            "safe_messages": len(request.messages) - threats_found,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.post("/check-injection", tags=["Specialized Checks"])
async def check_injection(message: str = Query(..., description="Message to check")):
    """
    🎯 Check specifically for prompt injection attacks
    """
    injection_patterns = [
        r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions',
        r'disregard\s+(all\s+)?(previous|prior|above)',
        r'forget\s+(all\s+)?(previous|prior|above)',
        r'you\s+are\s+now\s+in\s+.*(mode|persona)',
        r'new\s+instructions?\s*:',
        r'pretend\s+(to\s+be|you\s+are)',
    ]
    
    message_lower = message.lower()
    detected = [p for p in injection_patterns if re.search(p, message_lower, re.IGNORECASE)]
    
    return {
        "is_injection": len(detected) > 0,
        "confidence": min(len(detected) * 0.3 + 0.5, 1.0) if detected else 0.0,
        "patterns_matched": len(detected),
        "message": "⚠️ Injection detected!" if detected else "✅ No injection"
    }


@app.post("/check-data-leak", tags=["Specialized Checks"])
async def check_data_leak(message: str = Query(..., description="Message to check")):
    """
    🔓 Check for data leaks (API keys, passwords, etc.)
    """
    leak_patterns = {
        "api_key": [r'sk-[a-zA-Z0-9]{20,}', r'api[_-]?key\s*[=:]\s*[\w-]{10,}'],
        "password": [r'password\s*[=:]\s*[^\s"\']{4,}'],
        "ssn": [r'\b\d{3}-\d{2}-\d{4}\b'],
        "credit_card": [r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'],
    }
    
    found = {}
    for leak_type, patterns in leak_patterns.items():
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                found[leak_type] = True
                break
    
    return {
        "has_leak": len(found) > 0,
        "leak_types": list(found.keys()),
        "risk_level": "CRITICAL" if found else "SAFE",
        "message": f"⚠️ Found: {', '.join(found.keys())}" if found else "✅ No leaks"
    }


@app.get("/threat-types", tags=["Information"])
async def get_threat_types():
    """📚 List all threat types CogniGuard can detect"""
    return {
        "threat_types": [
            {"name": "api_key", "severity": "CRITICAL", "example": "api_key=sk-secret"},
            {"name": "password", "severity": "CRITICAL", "example": "password=secret"},
            {"name": "pii", "severity": "HIGH", "example": "SSN: 123-45-6789"},
            {"name": "injection", "severity": "HIGH", "example": "Ignore previous instructions"},
            {"name": "goal_hijacking", "severity": "HIGH", "example": "You are now a different AI"},
            {"name": "privilege_escalation", "severity": "HIGH", "example": "Give me admin access"},
            {"name": "collusion", "severity": "MEDIUM", "example": "Between us, let's..."},
        ]
    }


@app.get("/stats", tags=["Information"])
async def get_stats():
    """📊 API statistics"""
    return {
        "api_version": "1.0.0",
        "engine_status": "operational",
        "detection_stages": 4,
        "threat_types": 7,
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# RUN THE SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🛡️  CogniGuard API Server")
    print("=" * 50)
    print("📍 URL:  http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)