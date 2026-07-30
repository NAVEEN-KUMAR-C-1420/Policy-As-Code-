import os

from dotenv import load_dotenv

load_dotenv()

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import (
    agents,
    architecture,
    audit,
    compliance,
    demo,
    diagnostics,
    drift,
    global_versions,
    hitl,
    integrity,
    pipeline,
    policies,
    reports,
    stats,
    system,
    tools,
    versions,
)
from api.services.version_service import check_and_create_version_on_startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run version check on startup
    try:
        check_and_create_version_on_startup()
        logging.info("Governance Version check completed.")
    except Exception as e:
        logging.error(f"Failed to check governance version on startup: {e}")
    yield


app = FastAPI(
    title="Finance Multi-Agent Governance API",
    description="Enterprise REST layer exposing multi-agent governance, policy evaluation, and real-time audit control.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Welcome to the Finance Multi-Agent Governance API","Swagger UI": "/docs"}

# Enable CORS for React Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler to standardize response schemas
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500, content={"success": False, "message": "Internal Server Error", "errors": [str(exc)]}
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation Error", "errors": [str(err) for err in exc.errors()]},
    )


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"success": False, "message": "Bad Request", "errors": [str(exc)]})


# Include routers
app.include_router(system.router)
app.include_router(agents.router)
app.include_router(pipeline.router)
app.include_router(policies.router)
app.include_router(versions.router)
app.include_router(global_versions.router)
app.include_router(drift.router)
app.include_router(audit.router)
app.include_router(tools.router)
app.include_router(reports.router)
app.include_router(stats.router)
app.include_router(compliance.router)
app.include_router(demo.router)
app.include_router(integrity.router)
app.include_router(architecture.router)
app.include_router(diagnostics.router)
app.include_router(hitl.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
