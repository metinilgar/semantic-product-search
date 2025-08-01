"""
Vector Service for embedding generation and Qdrant operations
"""
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny
from app.settings import settings
from app.schemas import QdrantSearchResult

logger = logging.getLogger(__name__)


class VectorService:
    """Service for vector operations using Gemini embeddings and Qdrant"""
    
    def __init__(self):
        """Initialize the vector service"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize Gemini client with new API
        self.client = genai.Client(api_key=settings.gemini_api_key)
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection_name
        
        # Initialize collection if it doesn't exist
        self._ensure_collection_exists()
        
        logger.info(f"Vector Service initialized with Qdrant at {settings.qdrant_url}")
        logger.info(f"Using collection: {self.collection_name}")
    
    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists"""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                
                # Create collection with vector configuration
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.qdrant_vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    async def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """
        Generate embedding for given text using Gemini
        
        Args:
            text: Input text to embed
            task_type: Task type for embedding (RETRIEVAL_QUERY for search, RETRIEVAL_DOCUMENT for indexing)
            
        Returns:
            List of embedding values
            
        Raises:
            ValueError: If embedding generation fails
        """
        try:
            logger.debug(f"Generating embedding for text with task_type {task_type}: {text[:100]}...")
            
            # Generate embedding using new Gemini API with config
            result = self.client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=text,
                config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=settings.qdrant_vector_size)
            )
            
            if not result or not hasattr(result, 'embeddings') or not result.embeddings:
                raise ValueError("Failed to generate embedding")
            
            # Extract the embedding values using the new format
            embedding = result.embeddings[0].values
            
            logger.debug(f"Generated embedding of size: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise ValueError(f"Failed to generate embedding: {e}")
    
    async def index_product(self, product_data: Dict[str, Any]) -> bool:
        """
        Index a product in Qdrant
        
        Args:
            product_data: Product information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Build text for embedding
            text_for_embedding = self._build_product_text(product_data)
            
            # Generate embedding
            vector = await self.generate_embedding(text_for_embedding)
            
            # Prepare point for Qdrant
            point = PointStruct(
                id=product_data["product_id"],
                vector=vector,
                payload={
                    "title": product_data["title"],
                    "description": product_data["description"],
                    "category": product_data["category"],
                    "gender": product_data["gender"],
                    "tags": product_data["tags"],
                    "price": product_data["price"],
                    "image_url": product_data["image_url"]
                }
            )
            
            # Upsert to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Product {product_data['product_id']} indexed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing product {product_data.get('product_id', 'unknown')}: {e}")
            return False
    
    async def search_products(
        self, 
        query_vector: List[float], 
        gender: str, 
        product_types: List[str],
        limit: int = None
    ) -> List[QdrantSearchResult]:
        """
        Search products in Qdrant using vector similarity and filters
        
        Args:
            query_vector: Query embedding vector
            gender: Gender filter
            product_types: Product types filter
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            if limit is None:
                limit = settings.search_max_results
            
            # Build filter conditions
            filter_conditions = []
            
            # Gender filter
            filter_conditions.append(
                FieldCondition(
                    key="gender",
                    match=MatchValue(value=gender)
                )
            )
            
            # Product types filter (match any tag)
            if product_types:
                filter_conditions.append(
                    FieldCondition(
                        key="tags",
                        match=MatchAny(any=product_types)
                    )
                )
            
            # Build complete filter
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            logger.info(f"Searching with gender={gender}, types={product_types}, limit={limit}")
            
            # Perform search
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit,
                score_threshold=settings.search_score_threshold
            )
            
            # Convert to our result format
            results = []
            for result in search_results:
                results.append(QdrantSearchResult(
                    id=str(result.id),
                    payload=result.payload,
                    score=result.score
                ))
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def _build_product_text(self, product_data: Dict[str, Any]) -> str:
        """
        Build text representation of product for embedding
        
        Args:
            product_data: Product information
            
        Returns:
            Formatted text string
        """
        tags_str = ", ".join(product_data.get("tags", []))
        
        text = (
            f"{product_data['title']}. "
            f"{product_data['description']}. "
            f"Category: {product_data['category']}. "
            f"Gender: {product_data['gender']}. "
            f"Tags: {tags_str}. "
            f"Price: {product_data['price']}."
        )
        
        return text
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}


# Global service instance
vector_service = VectorService()