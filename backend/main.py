"""
FastAPI Server - Airline Disruption Resolution Agent
Main entry point for the backend API.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from models import ChatRequest, ChatResponse
from agent import agent
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 SkyAssist Agent starting up...")
    logger.info(f"Groq API configured with models:")
    logger.info(f"  - Fast: {settings.GROQ_FAST_MODEL}")
    logger.info(f"  - Smart: {settings.GROQ_SMART_MODEL}")
    yield
    # Shutdown
    logger.info("🛑 SkyAssist Agent shutting down...")

# Create FastAPI app
app = FastAPI(
    title="SkyAssist - Airline Support Agent",
    description="AI-powered customer support for airline disruptions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "status": "online",
        "agent": "SkyAssist",
        "version": "1.0.0",
        "description": "Airline Disruption Resolution Agent powered by Groq AI",
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agent_ready": True,
        "groq_api_configured": bool(settings.GROQ_API_KEY),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for customer interactions.
    
    Args:
        request: ChatRequest with message and conversation history
    
    Returns:
        ChatResponse with agent response and metadata
    """
    
    try:
        logger.info(f"📨 Received message: {request.message[:50]}...")
        
        # Process message through agent
        result = agent.process_customer_message(
            customer_message=request.message,
            conversation_history=request.conversation_history
        )
        
        logger.info(f"✅ Response generated. Escalation: {result['escalation_required']}")
        
        # Return structured response
        return ChatResponse(
            response=result["response"],
            action_summary=result["action_summary"],
            escalation_required=result["escalation_required"],
            actions_taken=result["actions_taken"],
            policy_applied=result["policy_applied"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your request: {str(e)}"
        )

@app.post("/chat/batch")
async def chat_batch(requests: list[ChatRequest]):
    """
    Batch processing endpoint for multiple messages.
    Useful for testing multiple scenarios.
    """
    
    results = []
    for req in requests:
        try:
            result = agent.process_customer_message(
                customer_message=req.message,
                conversation_history=req.conversation_history
            )
            results.append({
                "message": req.message,
                "response": result["response"],
                "success": True
            })
        except Exception as e:
            results.append({
                "message": req.message,
                "error": str(e),
                "success": False
            })
    
    return {"results": results}

@app.get("/audit-log")
async def get_audit_log():
    """Get audit log of all interactions (for demo purposes)"""
    
    return {
        "conversation_id": agent.conversation_id,
        "total_interactions": len(agent.audit_log),
        "audit_entries": agent.audit_log[-10:]  # Last 10 entries
    }

@app.get("/scenarios")
async def get_test_scenarios():
    """Get predefined test scenarios"""
    
    from data import SCENARIOS
    
    return {
        "scenario_date": "Wednesday, 23 September 2026",
        "scenarios": SCENARIOS,
        "description": "Three test scenarios based on assignment brief"
    }

@app.post("/reset")
async def reset_agent():
    """Reset agent for new conversation"""
    
    global agent
    from agent import AirlineAgent
    
    agent = AirlineAgent()
    
    return {
        "status": "reset",
        "new_conversation_id": agent.conversation_id,
        "message": "Agent reset. New conversation started."
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# Startup message
@app.on_event("startup")
async def startup_event():
    logger.info("""
    ╔═══════════════════════════════════════════╗
    ║     🛫 SkyAssist Agent Started 🛫        ║
    ║                                           ║
    ║  Airline Disruption Resolution System     ║
    ║  Powered by Groq AI                       ║
    ║                                           ║
    ║  API: http://localhost:8000               ║
    ║  Docs: http://localhost:8000/docs         ║
    ╚═══════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info"
    )
