"""
LLM Service for query analysis using Gemini 2.5 Flash Lite
"""
import logging
from typing import Dict, Any, Optional
from google import genai
from app.settings import settings
from app.schemas import LLMAnalysisResult
from app.prompts import get_query_analysis_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Gemini LLM for query analysis"""
    
    def __init__(self):
        """Initialize the LLM service"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Yeni Google Genai Client kullanımı
        self.client = genai.Client(api_key=settings.gemini_api_key)
        
        logger.info(f"LLM Service initialized with model: {settings.gemini_model_name}")
    

    
    async def analyze_query(self, query: str) -> LLMAnalysisResult:
        """
        Analyze user query and extract structured information
        
        Args:
            query: Natural language search query
            
        Returns:
            LLMAnalysisResult with extracted information
            
        Raises:
            ValueError: If analysis fails or returns invalid format
        """
        try:
            logger.info(f"Analyzing query: {query}")
            
            prompt = get_query_analysis_prompt(query)
            
            # Generate response using Gemini with structured output
            response = self.client.models.generate_content(
                model=settings.gemini_model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": LLMAnalysisResult,
                },
            )
            
            if not response.parsed:
                logger.warning("No parsed response from LLM, using fallback")
                return LLMAnalysisResult(**self._fallback_analysis(query))
            
            # Doğrudan parsed nesneyi al (artık Pydantic validation otomatik)
            result = response.parsed
            
            # LLM "null" string değerini döndürebilir, bunu None'a çevirelim
            if result.gender == "null":
                result.gender = None
            
            logger.info(f"Query analysis complete: gender={result.gender}, "
                       f"types={result.product_types}, expanded={result.expanded_query[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            # Return fallback analysis
            return LLMAnalysisResult(**self._fallback_analysis(query))
    
    def _fallback_analysis(self, query: str) -> Dict[str, Any]:
        """
        Provide a basic fallback analysis when LLM fails
        
        Args:
            query: Original search query
            
        Returns:
            Basic analysis dictionary
        """
        logger.warning("Using fallback analysis")
        
        query_lower = query.lower()
        
        # Simple gender detection
        gender = None
        if any(word in query_lower for word in ["erkek", "adam", "bay", "men", "man", "male", "him", "his"]):
            gender = "male"
        elif any(word in query_lower for word in ["kadın", "bayan", "women", "woman", "female", "her", "hers"]):
            gender = "female"
        
        # Simple product type detection
        product_types = []
        common_types = ["takım_elbise", "gömlek", "ayakkabı", "elbise", "pantolon", "ceket", 
                       "kravat", "saat", "kemer", "mont", "etek", "bluz", "çanta"]
        for ptype in common_types:
            if ptype in query_lower:
                product_types.append(ptype)
        
        if not product_types:
            product_types = ["giyim"]
        
        # Take only first 3-5 types
        product_types = product_types[:5]
        
        return {
            "gender": gender,
            "product_types": product_types,
            "expanded_query": f"{query} giyim moda kıyafet"
        }


# Global service instance
llm_service = LLMService()