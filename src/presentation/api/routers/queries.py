from fastapi import APIRouter, Depends, HTTPException
from src.presentation.api.schemas.request_schemas import AskRequest
from src.presentation.api.schemas.response_schemas import QueryResponse, SourceReference
from src.application.agents.document_analyst_agent import DocumentAnalystAgent
from src.application.services.knowledge_retrieval_service import KnowledgeRetrievalService
from src.presentation.api.dependencies import get_document_agent, get_retrieval_service
from src.domain.exceptions import LLMClientError, VectorStoreError
from src.domain.models.query import QueryRequest

router = APIRouter(prefix="/api/v1/queries", tags=["Queries"])

@router.post("/ask", response_model=QueryResponse)
def ask_question(
    request: AskRequest,
    agent: DocumentAnalystAgent = Depends(get_document_agent),
    retrieval_service: KnowledgeRetrievalService = Depends(get_retrieval_service)
):
    try:
        deps = {"retrieval_service": retrieval_service}
        answer = agent.run(request.question, deps)
        
        # Best-effort source retrieval based on user's original query
        query_result = retrieval_service.search(QueryRequest(question=request.question, top_k=3))
        sources = [
            SourceReference(
                section_title=c.section_title, 
                page=c.page,
                score=c.score, 
                chunk_id=c.chunk_id
            )
            for c in query_result.contexts
        ]
        
        return QueryResponse(
            answer=answer, 
            sources=sources,
            conversation_id=request.conversation_id
        )
    except LLMClientError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except VectorStoreError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
