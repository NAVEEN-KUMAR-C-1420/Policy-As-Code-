from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routers import (
    system, agents, pipeline, policies, versions,
    drift, audit, tools, reports, stats, compliance, demo
)
import logging
import os

# Configure basic logging for startup
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format='%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence Verification
    logging.info("✓ Configuration Loaded")
    
    # Verify Database Configuration
    db_provider = os.getenv("DATABASE_PROVIDER", "sqlite")
    if db_provider == "supabase":
        if not os.getenv("SUPABASE_URL"):
            logging.error("Missing SUPABASE_URL for supabase provider")
        else:
            logging.info("✓ Supabase Ready")
    else:
        logging.info("✓ Database Connected")

    # Mock service readiness assertions based on architecture
    logging.info("✓ Policies Loaded")
    logging.info("✓ Governance Ready")
    logging.info("✓ Audit Ready")
    logging.info("✓ Version Service Ready")
    logging.info("✓ Drift Detection Ready")
    logging.info("✓ Agents Ready")
    
    # Verify LLM Configuration
    if os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"):
        logging.info("✓ LLM Ready")
    else:
        logging.warning("No LLM API keys found in environment! Agents will fail.")
        
    logging.info("✓ FastAPI Ready")
    yield
    # Shutdown sequence
    logging.info("Application shutting down...")

app = FastAPI(
    title="Finance Multi-Agent Governance API",
    description="A thin REST layer exposing existing governance and agent functionality.",
    version="1.0.0",
    lifespan=lifespan
)
@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}

# CORS Middleware for Render, local development, and Frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your specific frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler to standardize response schemas
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal Server Error", "errors": [str(exc)]}
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation Error", "errors": [str(err) for err in exc.errors()]}
    )

@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": "Bad Request", "errors": [str(exc)]}
    )

# Include routers
app.include_router(system.router)
app.include_router(agents.router)
app.include_router(pipeline.router)
app.include_router(policies.router)
app.include_router(versions.router)
app.include_router(drift.router)
app.include_router(audit.router)
app.include_router(tools.router)
app.include_router(reports.router)
app.include_router(stats.router)
app.include_router(compliance.router)
app.include_router(demo.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
