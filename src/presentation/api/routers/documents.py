from fastapi import APIRouter, Depends, HTTPException
from src.presentation.api.schemas.request_schemas import IngestRequest
from src.presentation.api.schemas.response_schemas import IngestResponse
from src.application.services.document_ingestion_service import DocumentIngestionService
from src.presentation.api.dependencies import get_ingestion_service
from src.domain.exceptions import DocumentProcessingError, VectorStoreError

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

@router.post("/ingest", response_model=IngestResponse, status_code=202)
def ingest_document(
    request: IngestRequest,
    svc: DocumentIngestionService = Depends(get_ingestion_service)
):
    try:
        message = svc.ingest(request.file_path)
        return IngestResponse(message=message)
    except DocumentProcessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except VectorStoreError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
