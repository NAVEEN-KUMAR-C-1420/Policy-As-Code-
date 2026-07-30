import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from api.routers import (
    system, agents, pipeline, policies, versions, global_versions,
    drift, audit, tools, reports, stats, compliance, demo
)
import logging
from contextlib import asynccontextmanager
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
    description="A thin REST layer exposing existing governance and agent functionality.",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(global_versions.router)
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
