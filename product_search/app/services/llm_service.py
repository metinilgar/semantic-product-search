"""
LLM Service for query analysis using Gemini 2.5 Flash Lite
"""
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.settings import settings
from app.schemas import LLMAnalysisResult

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Gemini LLM for query analysis"""
    
    def __init__(self):
        """Initialize the LLM service"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model_name)
        
        logger.info(f"LLM Service initialized with model: {settings.gemini_model_name}")
    
    def _build_analysis_prompt(self, query: str) -> str:
        """Build the prompt template for query analysis"""
        prompt = f"""
Analyze the following product search query and extract structured information.

Input: "{query}"

Instructions:
- Detect user intent: identify product types, context tags, and gender preference ('male'|'female'|'unisex').
- List the top 3-5 product types in order of relevance, e.g. ['suit','shirt','shoe','tie','watch'].
- Produce an expanded, context-aware search phrase that includes those types and relevant descriptive terms.
- If gender is not explicitly mentioned, infer from context or default to 'unisex'.
- Product types should be single words (suit, shirt, shoe, etc.) not phrases.

Output format (JSON only, no additional text):
{{
  "gender": "<male|female|unisex>",
  "product_types": ["<type1>", "<type2>", "<type3>"],
  "expanded_query": "<expanded natural-language string>"
}}

Examples:
Query: "I need a black suit for office"
Output: {{"gender": "unisex", "product_types": ["suit", "shirt", "tie"], "expanded_query": "black formal business suit office professional wear"}}

Query: "casual shirt for men"
Output: {{"gender": "male", "product_types": ["shirt", "pants", "shoe"], "expanded_query": "casual men's shirt comfortable everyday wear"}}

Query: "wedding dress for women"
Output: {{"gender": "female", "product_types": ["dress", "shoe", "accessory"], "expanded_query": "wedding dress women formal elegant bridal wear"}}

Now analyze: "{query}"
"""
        return prompt
    
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
            
            prompt = self._build_analysis_prompt(query)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Empty response from LLM")
            
            logger.debug(f"LLM raw response: {response.text}")
            
            # Parse JSON response
            try:
                # Clean the response text - remove any markdown formatting
                clean_text = response.text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                result_dict = json.loads(clean_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Raw response: {response.text}")
                
                # Fallback analysis
                result_dict = self._fallback_analysis(query)
            
            # Validate and create result object
            result = LLMAnalysisResult(**result_dict)
            
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
        gender = "unisex"
        if any(word in query_lower for word in ["men", "man", "male", "him", "his"]):
            gender = "male"
        elif any(word in query_lower for word in ["women", "woman", "female", "her", "hers"]):
            gender = "female"
        
        # Simple product type detection
        product_types = []
        common_types = ["suit", "shirt", "shoe", "dress", "pants", "jacket", "tie", "watch", "belt"]
        for ptype in common_types:
            if ptype in query_lower:
                product_types.append(ptype)
        
        if not product_types:
            product_types = ["clothing"]
        
        # Take only first 3-5 types
        product_types = product_types[:5]
        
        return {
            "gender": gender,
            "product_types": product_types,
            "expanded_query": f"{query} clothing fashion wear"
        }


# Global service instance
llm_service = LLMService()