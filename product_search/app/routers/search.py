"""
Search router for product search endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    SearchRequest, SearchResponse, SearchResultItem, 
    ErrorResponse, LLMAnalysisResult
)
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search products",
    description="Search products using natural language query with LLM-powered intent extraction"
)
async def search_products(request: SearchRequest) -> SearchResponse:
    """
    Search products using natural language query
    
    This endpoint:
    1. Analyzes the query using Gemini LLM to extract intent and structure
    2. Generates embedding for the expanded query
    3. Searches Qdrant vector database with filters
    4. Returns ranked results
    
    Args:
        request: Search request with natural language query
        
    Returns:
        SearchResponse with analyzed query and ranked results
        
    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Processing search query: {request.query}")
        
        # Step 1: Analyze query using LLM
        logger.debug("Analyzing query with LLM...")
        analysis_result = await llm_service.analyze_query(request.query)
        
        logger.info(f"Query analysis - Gender: {analysis_result.gender}, "
                   f"Types: {analysis_result.product_types}, "
                   f"Expanded: {analysis_result.expanded_query[:50]}...")
        
        # Step 2: Generate embedding for expanded query
        logger.debug("Generating embedding for expanded query...")
        query_vector = await vector_service.generate_embedding(analysis_result.expanded_query)
        
        # Step 3: Search in Qdrant with filters
        logger.debug("Searching in vector database...")
        search_results = await vector_service.search_products(
            query_vector=query_vector,
            gender=analysis_result.gender,
            product_types=analysis_result.product_types
        )
        
        # Step 4: Convert results to response format
        response_results = []
        for result in search_results:
            response_results.append(SearchResultItem(
                product_id=result.id,
                title=result.payload.get("title", ""),
                price=result.payload.get("price", 0.0),
                image_url=result.payload.get("image_url", ""),
                score=result.score
            ))
        
        logger.info(f"Search completed - Found {len(response_results)} results")
        
        # Build response
        response = SearchResponse(
            query=request.query,
            gender=analysis_result.gender,
            product_types=analysis_result.product_types,
            expanded_query=analysis_result.expanded_query,
            results=response_results
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.error(f"Validation error in search: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search"
        )


@router.post(
    "/analyze",
    response_model=LLMAnalysisResult,
    summary="Analyze query only",
    description="Analyze query intent without performing actual search"
)
async def analyze_query_only(request: SearchRequest) -> LLMAnalysisResult:
    """
    Analyze query intent without performing search
    
    Useful for debugging and testing query analysis
    
    Args:
        request: Search request with query to analyze
        
    Returns:
        LLMAnalysisResult with extracted intent information
    """
    try:
        logger.info(f"Analyzing query only: {request.query}")
        
        result = await llm_service.analyze_query(request.query)
        
        logger.info(f"Analysis complete - Gender: {result.gender}, "
                   f"Types: {result.product_types}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze query"
        )