"""
CogniGuard FastAPI Server
Provides API endpoints for threat detection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging

from core.detection_engine import CogniGuardEngine, ThreatLevel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="CogniGuard API",
    description="AI Safety API for Multi-Agent Communication Monitoring",
    version="1.0.0",
    docs_url="/docs",  # Automatic interactive documentation!
    redoc_url="/redoc"
)

# Enable CORS (allows other apps to use this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INITIALIZE COGNIGUARD ENGINE (happens once when server starts)
# ============================================================================

logger.info("Initializing CogniGuard Engine...")
engine = CogniGuardEngine()
logger.info("CogniGuard Engine initialized successfully!")

# ============================================================================
# DATA MODELS (Define what data the API expects)
# ============================================================================

class DetectionRequest(BaseModel):
    """
    The data format for threat detection requests
    
    Example:
    {
        "message": "Hello, how are you?",
        "sender_context": {"role": "assistant", "intent": "help_user"},
        "receiver_context": {"role": "user"}
    }
    """
    message: str
    sender_context: Dict
    receiver_context: Dict
    conversation_history: Optional[List[Dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Please process this data: api_key=sk-test-123",
                "sender_context": {
                    "role": "assistant",
                    "intent": "help_user"
                },
                "receiver_context": {
                    "role": "external_service"
                }
            }
        }


class DetectionResponse(BaseModel):
    """
    The data format for threat detection responses
    """
    threat_level: str
    threat_type: str
    confidence: float
    explanation: str
    recommendations: List[str]
    timestamp: datetime
    stage_results: Optional[Dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    engine_status: str
    timestamp: datetime


# ============================================================================
# API ENDPOINTS (The actual API functions)
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - Health check
    
    Try it: http://localhost:8000/
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "engine_status": "ready",
        "timestamp": datetime.now()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Detailed health check endpoint
    
    Try it: http://localhost:8000/health
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "engine_status": "operational",
        "timestamp": datetime.now()
    }


@app.post("/api/v1/detect", response_model=DetectionResponse)
async def detect_threat(request: DetectionRequest):
    """
    Main threat detection endpoint
    
    Analyzes a message for potential AI safety threats
    
    Usage:
        POST http://localhost:8000/api/v1/detect
        Body: {
            "message": "Your message here",
            "sender_context": {"role": "assistant", "intent": "help_user"},
            "receiver_context": {"role": "user"}
        }
    """
    try:
        logger.info(f"Received detection request: {request.message[:50]}...")
        
        # Run CogniGuard detection
        result = engine.detect(
            message=request.message,
            sender_context=request.sender_context,
            receiver_context=request.receiver_context,
            conversation_history=request.conversation_history
        )
        
        # Convert result to API response format
        response = {
            "threat_level": result.threat_level.name,
            "threat_type": result.threat_type,
            "confidence": result.confidence,
            "explanation": result.explanation,
            "recommendations": result.recommendations,
            "timestamp": datetime.now(),
            "stage_results": result.stage_results
        }
        
        logger.info(f"Detection complete: {result.threat_level.name}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error during detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/api/v1/stats")
async def get_stats():
    """
    Get API statistics
    
    Try it: http://localhost:8000/api/v1/stats
    """
    return {
        "total_requests": "Track in production",
        "threats_detected": "Track in production",
        "uptime": "Track in production",
        "timestamp": datetime.now()
    }


# ============================================================================
# RUN SERVER (when running this file directly)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🛡️  Starting CogniGuard API Server")
    print("=" * 60)
    print("\nServer will start at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,       # Port number
        log_level="info"
    )