"""
ShopSearchAgent - Main FastAPI application
"""
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.settings import settings
from app.routers import products, search


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("ShopSearchAgent starting up...")
    
    # Test services initialization
    try:
        from app.services.vector_service import vector_service
        collection_info = await vector_service.get_collection_info()
        logger.info(f"Vector service ready - Collection: {collection_info}")
    except Exception as e:
        logger.warning(f"Vector service initialization warning: {e}")
    
    logger.info("ShopSearchAgent startup complete")
    
    yield
    
    # Shutdown
    logger.info("ShopSearchAgent shutting down...")


# Create FastAPI application
app = FastAPI(
    title="ShopSearchAgent",
    description="""
    ShopSearchAgent is a modular AI service that provides intelligent product search capabilities.
    
    ## Features
    
    * **Product Indexing**: Add and update products in the vector database
    * **Natural Language Search**: Search products using natural language queries
    * **AI-Powered Intent Extraction**: Uses Gemini 2.5 Flash Lite for query analysis
    * **Vector Similarity Search**: Powered by Qdrant and Gemini embeddings
    
    ## Endpoints
    
    * `POST /products/index` - Index a new product or update existing one
    * `POST /search` - Search products using natural language
    * `POST /search/analyze` - Analyze query intent without searching
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)
app.include_router(search.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "ShopSearchAgent",
        "version": "1.0.0",
        "description": "AI-powered product search service",
        "endpoints": {
            "products": "/products/index",
            "search": "/search",
            "docs": "/docs"
        },
        "status": "running"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    try:
        from app.services.vector_service import vector_service
        
        # Check vector service
        collection_info = await vector_service.get_collection_info()
        
        return {
            "status": "healthy",
            "services": {
                "vector_db": "connected",
                "collection": collection_info.get("name", "unknown"),
                "vectors_count": collection_info.get("vectors_count", 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )