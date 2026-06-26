import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.domain.exceptions import (
    DocumentProcessingError, LLMClientError, VectorStoreError, AgenticPlatformError
)
from src.presentation.api.routers import documents, queries

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title="Banking Agentic Platform API",
    description="Multimodal PDF extraction with Document Analyst Agent",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(DocumentProcessingError)
async def doc_processing_error_handler(request: Request, exc: DocumentProcessingError):
    return JSONResponse(status_code=422, content={"error": "DocumentProcessingError", "detail": str(exc)})

@app.exception_handler(LLMClientError)
async def llm_error_handler(request: Request, exc: LLMClientError):
    return JSONResponse(status_code=503, content={"error": "LLMClientError", "detail": str(exc)})

@app.exception_handler(VectorStoreError)
async def vector_store_error_handler(request: Request, exc: VectorStoreError):
    return JSONResponse(status_code=503, content={"error": "VectorStoreError", "detail": str(exc)})

@app.exception_handler(AgenticPlatformError)
async def platform_error_handler(request: Request, exc: AgenticPlatformError):
    return JSONResponse(status_code=500, content={"error": "AgenticPlatformError", "detail": str(exc)})

app.include_router(documents.router)
app.include_router(queries.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "0.1.0"}
