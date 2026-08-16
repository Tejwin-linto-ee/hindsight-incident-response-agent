"""
Hindsight Enterprise REST & Real-Time WebSocket API Server
===========================================================
High-performance asynchronous server providing programmatic access to:
- Incident Investigation & Root Cause Analysis
- Autonomous Mitigation & Playbook Execution
- Machine Learning Telemetry Prediction & Failure Risk Scoring
- Semantic Organizational Memory Recall
- SRE Copilot Interactive Chat & Automated Actions
- Real-time Telemetry WebSocket Streams
- Role-Based Authentication, Rate Limiting & Audit Trails
"""

import asyncio
from datetime import datetime, timezone
import json
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Depends, HTTPException, Security, WebSocket, WebSocketDisconnect, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent import IncidentResponseAgent
from app.auth import SecurityManager
from app.failure_predictor import FailurePredictor
from app.hindsight_memory import IncidentMemory
from app.incident_history import IncidentHistory
from app.memory_engine import MemoryEngine
from app.sre_chat import SRECopilot
from app.telemetry_simulator import TelemetrySimulator
from app.alert_dispatcher import AlertDispatcher

app = FastAPI(
    title="Hindsight Incident Intelligence Enterprise API",
    description="Mission-critical automated incident response, ML telemetry forecasting, and persistent memory API.",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for modern frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security_bearer = HTTPBearer(auto_error=False)


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class AuthRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "admin"})
    password: str = Field(..., json_schema_extra={"example": "admin123"})


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    tenant_id: str


class TelemetryInput(BaseModel):
    cpu_percent: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 85.5})
    memory_percent: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 92.0})
    disk_percent: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 65.0})
    db_connections: float = Field(..., ge=0.0, json_schema_extra={"example": 94.0})
    db_pool_usage: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 96.0})
    api_latency_ms: float = Field(..., ge=0.0, json_schema_extra={"example": 1200.0})
    error_rate: float = Field(..., ge=0.0, json_schema_extra={"example": 8.5})
    request_rate: float = Field(..., ge=0.0, json_schema_extra={"example": 1800.0})
    queue_depth: float = Field(..., ge=0.0, json_schema_extra={"example": 140.0})
    network_latency_ms: float = Field(..., ge=0.0, json_schema_extra={"example": 85.0})
    traffic_growth_percent: float = Field(..., json_schema_extra={"example": 25.0})


class IncidentInvestigationRequest(BaseModel):
    incident_description: str = Field(..., min_length=5, json_schema_extra={"example": "Payment API returning HTTP 503 errors. Connection pool exhausted."})
    telemetry: Optional[TelemetryInput] = None
    trigger_alert: bool = Field(default=False, description="Whether to dispatch alert to configured webhooks")


class AutonomousMitigationRequest(BaseModel):
    incident_description: str = Field(..., json_schema_extra={"example": "Redis cache memory saturation causing latency spikes"})
    auto_approve: bool = Field(default=False, description="Execute non-destructive actions without manual gate")


class MemoryRetainRequest(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Payment Gateway Connection Timeout"})
    description: str = Field(..., json_schema_extra={"example": "HikariCP connection pool exhausted due to unindexed query."})
    resolution: str = Field(..., json_schema_extra={"example": "Scaled connection pool from 50 to 150 and deployed composite index."})
    tags: List[str] = Field(default_factory=list, json_schema_extra={"example": ["database", "p1", "payment"]})
    service: str = Field(default="payment-service")


class CopilotChatRequest(BaseModel):
    message: str = Field(..., json_schema_extra={"example": "What is the current database pool saturation and recommended mitigation?"})
    session_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


# ============================================================
# SECURITY & AUTHENTICATION DEPENDENCIES
# ============================================================

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Dict[str, Any]:
    if not credentials:
        # Default anonymous demo access if no bearer token provided
        return {"username": "admin", "role": "sre_lead", "tenant_id": "default"}
    token = credentials.credentials
    try:
        user = SecurityManager.verify_token(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
# REST API ENDPOINTS
# ============================================================

@app.get("/health", tags=["System"])
async def health_check():
    """System health check and operational status."""
    return {
        "status": "healthy",
        "service": "Hindsight Incident Intelligence Platform",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.5.0",
        "capabilities": [
            "ai_incident_triage",
            "ml_telemetry_forecasting",
            "semantic_memory_recall",
            "autonomous_runbook_execution",
            "realtime_telemetry_stream",
            "alert_dispatching",
        ],
    }


@app.post("/api/v1/auth/login", response_model=AuthResponse, tags=["Authentication"])
async def login(auth: AuthRequest):
    """Authenticate and obtain session access token."""
    user, msg = SecurityManager.authenticate(auth.username, auth.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    
    token = f"token_{user['username']}_{datetime.now(timezone.utc).timestamp()}"
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user.get("role", "SRE"),
        "tenant_id": user.get("tenant_id", "default"),
    }


@app.post("/api/v1/incidents/investigate", tags=["Incidents"])
async def investigate_incident(
    req: IncidentInvestigationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Perform deep AI incident investigation using Hindsight organizational memory,
    historical resolution matching, and real-time telemetry ML prediction.
    """
    agent = IncidentResponseAgent()
    telemetry_dict = req.telemetry.model_dump() if req.telemetry else None

    result = agent.investigate(
        incident=req.incident_description,
        telemetry=telemetry_dict,
    )

    if req.trigger_alert and result.get("analysis_json"):
        alert_result = AlertDispatcher.dispatch_all(result["analysis_json"])
        result["alerts_dispatched"] = alert_result

    # Log security audit trail
    SecurityManager.log_event(
        event_type="INCIDENT_INVESTIGATED",
        actor=current_user["username"],
        details=f"Investigated: {req.incident_description[:80]}",
        status="SUCCESS",
    )

    return result


@app.post("/api/v1/incidents/autonomous-mitigate", tags=["Incidents"])
async def autonomous_mitigate(
    req: AutonomousMitigationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Autonomous AI mitigation pipeline: classifies failure, generates mitigation steps,
    and executes non-destructive actions.
    """
    agent = IncidentResponseAgent()
    mitigation_res = agent.autonomous_mitigate(
        incident=req.incident_description,
        auto_approve=req.auto_approve,
    )
    return mitigation_res


@app.post("/api/v1/telemetry/predict", tags=["ML Telemetry"])
async def predict_telemetry_failure(telemetry: TelemetryInput):
    """
    Predict failure type, risk score, and early warnings using the calibrated ML ensemble.
    """
    predictor = FailurePredictor()
    prediction = predictor.predict(telemetry.model_dump())
    return prediction


@app.get("/api/v1/memory/search", tags=["Organizational Memory"])
async def search_memory(query: str, top_k: int = 5):
    """
    Semantic search over historical incident memories stored in Hindsight.
    """
    memory = IncidentMemory()
    results = memory.find_similar_incidents(query, top_k=top_k)
    structured = MemoryEngine.process_and_rank_memories(results, query=query, limit=top_k)
    return {
        "query": query,
        "results_count": len(structured),
        "memories": structured,
    }


@app.post("/api/v1/memory/retain", tags=["Organizational Memory"])
async def retain_memory(
    req: MemoryRetainRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Retain a new resolved incident into Hindsight persistent organizational memory.
    """
    memory = IncidentMemory()
    doc_id = memory.retain_incident(
        title=req.title,
        description=req.description,
        resolution=req.resolution,
        tags=req.tags,
        service=req.service,
    )
    return {
        "status": "retained",
        "memory_id": doc_id,
        "title": req.title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/copilot/chat", tags=["SRE Copilot"])
async def copilot_chat(req: CopilotChatRequest):
    """
    Interactive SRE Copilot chat for incident assistance, diagnostic queries, and remediation advice.
    """
    copilot = SRECopilot()
    response = copilot.ask(
        user_message=req.message,
    )
    return {"reply": response}


@app.get("/api/v1/audit/logs", tags=["Audit & Governance"])
async def get_audit_logs(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieve security audit trails and operational execution history."""
    logs = SecurityManager.get_audit_logs()
    return {"audit_logs": logs}


# ============================================================
# REAL-TIME WEBSOCKET TELEMETRY STREAM
# ============================================================

@app.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """
    Real-time live WebSocket stream emitting telemetry metrics, failure risk probabilities,
    and anomaly detection scores at 1Hz.
    """
    await websocket.accept()
    simulator = TelemetrySimulator()
    predictor = FailurePredictor()

    try:
        while True:
            metrics = simulator.generate_sample()
            prediction = predictor.predict(metrics)
            
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "telemetry": metrics,
                "prediction": {
                    "failure_risk": prediction.get("failure_risk", 0),
                    "predicted_type": prediction.get("predicted_failure_type", "none"),
                    "risk_level": prediction.get("risk_level", "LOW"),
                },
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Entry point to run the API server via Uvicorn."""
    import uvicorn
    uvicorn.run("app.api_server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run_server()
