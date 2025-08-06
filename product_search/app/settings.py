"""
Configuration settings for ShopSearchAgent
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from config.yaml and environment variables"""
    
    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "products"
    qdrant_vector_size: int = 1536
    qdrant_distance: str = "Cosine"
    
    # Gemini Configuration
    gemini_model_name: str = "models/gemini-2.5-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_api_key: str = ""
    
    # Search Configuration
    search_max_results: int = 10
    search_score_threshold: float = 0.7
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config() -> Settings:
    """Load configuration from config.yaml file and environment variables"""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    # Load from YAML file if it exists
    config_data = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
            
        # Flatten the YAML structure for pydantic
        if yaml_data:
            config_data.update({
                "qdrant_url": yaml_data.get("qdrant", {}).get("url", "http://localhost:6333"),
                "qdrant_collection_name": yaml_data.get("qdrant", {}).get("collection_name", "products"),
                "qdrant_vector_size": yaml_data.get("qdrant", {}).get("vector_size", 1536),
                "qdrant_distance": yaml_data.get("qdrant", {}).get("distance", "Cosine"),
                "gemini_model_name": yaml_data.get("gemini", {}).get("model_name", "models/gemini-2.5-flash-lite"),
                "gemini_embedding_model": yaml_data.get("gemini", {}).get("embedding_model", "gemini-embedding-001"),
                "search_max_results": yaml_data.get("search", {}).get("max_results", 10),
                "search_score_threshold": yaml_data.get("search", {}).get("score_threshold", 0.7),
                "log_level": yaml_data.get("logging", {}).get("level", "INFO"),
                "log_format": yaml_data.get("logging", {}).get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            })
    
    # Get Gemini API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_api_key:
        config_data["gemini_api_key"] = gemini_api_key
    
    return Settings(**config_data)


# Global settings instance
settings = load_config()