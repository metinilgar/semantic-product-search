"""
Pydantic models for request and response schemas
"""
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator


class ProductIndexRequest(BaseModel):
    """Request schema for POST /products/index"""
    product_id: str = Field(..., description="Unique identifier for the product")
    title: str = Field(..., description="Product title", min_length=1, max_length=200)
    description: str = Field(..., description="Product description", min_length=1, max_length=1000)
    category: str = Field(..., description="Product category", min_length=1, max_length=50)
    gender: Literal["male", "female", "unisex"] = Field(..., description="Target gender")
    tags: List[str] = Field(..., description="Product tags", min_length=1)
    price: float = Field(..., description="Product price", ge=0)
    image_url: str = Field(..., description="Product image URL")
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if not v:
            raise ValueError('Tags list cannot be empty')
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    @field_validator('category')
    def validate_category(cls, v):
        return v.strip().lower()


class ProductIndexResponse(BaseModel):
    """Response schema for POST /products/index"""
    status: str = Field(..., description="Operation status")
    product_id: str = Field(..., description="Indexed product ID")


class SearchRequest(BaseModel):
    """Request schema for POST /search"""
    query: str = Field(..., description="Natural language search query", min_length=1, max_length=500)


class LLMAnalysisResult(BaseModel):
    """Schema for LLM analysis result"""
    gender: Literal["male", "female", "unisex"] = Field(..., description="Detected gender preference")
    product_types: List[str] = Field(..., description="Top 3-5 relevant product types")
    expanded_query: str = Field(..., description="Expanded search query")
    
    @field_validator('product_types')
    def validate_product_types(cls, v):
        if not v:
            raise ValueError('Product types list cannot be empty')
        return [ptype.strip().lower() for ptype in v if ptype.strip()]


class SearchResultItem(BaseModel):
    """Individual search result item"""
    product_id: str = Field(..., description="Product identifier")
    title: str = Field(..., description="Product title")
    price: float = Field(..., description="Product price")
    image_url: str = Field(..., description="Product image URL")
    score: float = Field(..., description="Relevance score")


class SearchResponse(BaseModel):
    """Response schema for POST /search"""
    query: str = Field(..., description="Original search query")
    gender: Literal["male", "female", "unisex"] = Field(..., description="Detected gender")
    product_types: List[str] = Field(..., description="Detected product types")
    expanded_query: str = Field(..., description="Expanded search query")
    results: List[SearchResultItem] = Field(..., description="Search results")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# Qdrant specific models
class QdrantPoint(BaseModel):
    """Qdrant point structure"""
    id: str
    vector: List[float]
    payload: dict


class QdrantSearchResult(BaseModel):
    """Qdrant search result"""
    id: str
    payload: dict
    score: float