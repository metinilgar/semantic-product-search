"""
LLM Service for query analysis using Gemini 2.5 Flash Lite
"""
import logging
from typing import Dict, Any, Optional
from google import genai
from app.settings import settings
from app.schemas import LLMAnalysisResult

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
    
    def _build_analysis_prompt(self, query: str) -> str:
        """Build the prompt template for query analysis"""
        prompt = f"""
Aşağıdaki ürün arama sorgusunu analiz et ve yapılandırılmış bilgileri çıkar.

Input: "{query}"

Talimatlar:
- Sen, e-ticaret aramalarını analiz eden uzman bir yapay zekasın.
- Kullanıcı niyetini tespit et: ürün türleri, bağlamsal etiketler ve cinsiyet tercihini ('erkek'|'kadın'|'unisex') belirle.
- En alakalı 3–5 ürün türünü sırayla listele. İlk ürün türü, her zaman sorguda belirtilen ana ürün olmalıdır. Ürün türleri tek kelime olsun (ör. ceket, gömlek, ayakkabı).
- Renk, malzeme (ör: pamuk, deri), stil (ör: V yaka, dar paça) gibi tüm ürün niteliklerini tespit et.
- Genişletilmiş sorguyu (expanded_query) oluştururken, bunun bir ürün başlığı veya zengin bir ürün açıklaması gibi olmasını hedefle. Bu sorgu; tespit edilen cinsiyeti, ana ürün türünü, renk, malzeme gibi nitelikleri ve bağlamsal kelimeleri (ör: ofis, yazlık, spor, rahat) mutlaka içermelidir.
- Eğer kullanıcı "hariç", "dışında", "olmayan" gibi negatif bir kısıtlama belirtirse, bu kısıtlamayı genişletilmiş sorguya dahil ETME, bunun yerine ilgili terimi ürün türlerinden ve genişletilmiş sorgudan çıkar.
- Eğer cinsiyet açıkça belirtilmemişse, bağlamdan çıkar ya da varsayılan olarak 'unisex' ata.

Örnekler:
Query: "Ofis için siyah takım elbise lazım" → gender: "unisex", product_types: ["takım_elbise", "gömlek", "ayakkabı", "kravat"], expanded_query: "unisex siyah resmi ofis takım elbise profesyonel iş giyim klasik kesim gömlek ve ayakkabı"

Query: "erkekler için günlük spor ayakkabı" → gender: "male", product_types: ["ayakkabı", "çorap", "eşofman", "şort"], expanded_query: "erkek günlük spor ayakkabı rahat konforlu yürüyüş ve koşu sneaker erkek spor çorap eşofman altı"

Query: "Deri olmayan siyah erkek ceketi" → gender: "male", product_types: ["ceket", "mont", "trençkot", "gömlek"], expanded_query: "siyah erkek ceket kumaş mevsimlik bomber kolej mont su geçirmez trençkot"

Şimdi aşağıdaki sorguyu analiz et: "{query}"
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