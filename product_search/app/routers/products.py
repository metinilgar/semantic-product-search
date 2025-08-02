"""
Products router for product indexing endpoints
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas import ProductIndexRequest, ProductIndexResponse, BatchIndexRequest, BatchIndexResponse, BatchIndexItem, ErrorResponse
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.post(
    "/index",
    response_model=ProductIndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Index a product",
    description="Ingest one new product or update an existing one in the vector database"
)
async def index_product(request: ProductIndexRequest) -> ProductIndexResponse:
    """
    Index a product for search
    
    This endpoint:
    1. Concatenates product fields into a text blob
    2. Generates embedding using Gemini embedding model
    3. Stores in Qdrant vector database with metadata
    
    Args:
        request: Product information to index
        
    Returns:
        ProductIndexResponse with operation status
        
    Raises:
        HTTPException: If indexing fails
    """
    try:
        logger.info(f"Indexing product: {request.product_id}")
        
        # Convert request to dictionary
        product_data = request.model_dump()
        
        # Index the product using vector service
        success = await vector_service.index_product(product_data)
        
        if not success:
            logger.error(f"Failed to index product: {request.product_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index product {request.product_id}"
            )
        
        logger.info(f"Successfully indexed product: {request.product_id}")
        
        return ProductIndexResponse(
            status="indexed",
            product_id=request.product_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.error(f"Validation error indexing product {request.product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error indexing product {request.product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during product indexing"
        )


@router.post(
    "/batch_index",
    response_model=BatchIndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch index products",
    description="Index multiple products at once for improved performance"
)
async def batch_index_products(request: BatchIndexRequest) -> BatchIndexResponse:
    """
    Batch index multiple products for search
    
    This endpoint:
    1. Processes multiple products simultaneously
    2. Generates embeddings for each product using Gemini embedding model
    3. Batch stores them in Qdrant vector database with metadata
    4. Returns detailed results for each product
    
    Args:
        request: Batch request containing list of products to index
        
    Returns:
        BatchIndexResponse with detailed results for each product
        
    Raises:
        HTTPException: If validation fails or processing encounters errors
    """
    try:
        logger.info(f"Starting batch indexing for {len(request.products)} products")
        
        # Convert products to dictionaries
        products_data = [product.model_dump() for product in request.products]
        
        # Batch index products using vector service
        batch_result = await vector_service.batch_index_products(products_data)
        
        # Convert results to response format
        batch_items = []
        for result in batch_result["results"]:
            batch_items.append(BatchIndexItem(
                product_id=result["product_id"],
                status=result["status"],
                error=result["error"]
            ))
        
        response = BatchIndexResponse(
            total_products=len(request.products),
            successful=batch_result["successful_count"],
            failed=batch_result["failed_count"],
            results=batch_items
        )
        
        logger.info(f"Batch indexing completed: {response.successful} successful, {response.failed} failed")
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in batch indexing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in batch indexing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch product indexing"
        )


@router.get(
    "/collection/info",
    summary="Get collection information",
    description="Get information about the vector database collection"
)
async def get_collection_info():
    """Get information about the vector collection"""
    try:
        info = await vector_service.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collection information"
        )