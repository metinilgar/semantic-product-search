"""
Arama API servisi
"""
import requests
import logging
from typing import Dict, Any, List, Optional
from .models import Product

logger = logging.getLogger(__name__)

# Arama API Endpoint
SEARCH_API_ENDPOINT = "http://127.0.0.1:8000/search"


def search_products(query: str) -> Dict[str, Any]:
    """
    Arama sorgusunu API'ye gönder ve sonuçları al
    """
    try:
        # API'ye POST isteği gönder
        payload = {"query": query}
        
        response = requests.post(
            SEARCH_API_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        # Yanıtı kontrol et
        if response.status_code == 200:
            api_result = response.json()
            logger.info(f"Arama başarılı: '{query}' - {len(api_result.get('results', []))} sonuç")
            return api_result
        else:
            logger.error(f"Arama API hatası: {response.status_code} - {response.text}")
            return {
                'error': True,
                'message': f'Arama servisi hatası: {response.status_code}',
                'query': query,
                'results': []
            }
            
    except requests.exceptions.Timeout:
        logger.error(f"Arama API timeout: '{query}'")
        return {
            'error': True,
            'message': 'Arama servisi zaman aşımına uğradı',
            'query': query,
            'results': []
        }
    except requests.exceptions.ConnectionError:
        logger.error(f"Arama API bağlantı hatası: '{query}'")
        return {
            'error': True,
            'message': 'Arama servisine bağlanılamıyor',
            'query': query,
            'results': []
        }
    except Exception as e:
        logger.error(f"Beklenmeyen arama hatası: '{query}' - {str(e)}")
        return {
            'error': True,
            'message': 'Beklenmeyen bir hata oluştu',
            'query': query,
            'results': []
        }


def get_products_by_ids(product_ids: List[str]) -> List[Product]:
    """
    Product ID'lerini kullanarak veritabanından ürünleri getir
    """
    try:
        # UUID string'lerini kullanarak ürünleri getir
        products = Product.objects.filter(id__in=product_ids)
        
        # API sonuç sırasını korumak için manuel sıralama
        product_dict = {str(p.id): p for p in products}
        ordered_products = []
        
        for product_id in product_ids:
            if product_id in product_dict:
                ordered_products.append(product_dict[product_id])
            else:
                logger.warning(f"Ürün bulunamadı: {product_id}")
        
        logger.info(f"Veritabanından {len(ordered_products)} ürün getirildi")
        return ordered_products
        
    except Exception as e:
        logger.error(f"Ürün getirme hatası: {str(e)}")
        return []


def process_search_results(api_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    API sonuçlarını işle ve veritabanından ürün detaylarını getir
    """
    if api_result.get('error'):
        return api_result
    
    try:
        # API'den gelen ürün ID'lerini çıkar
        api_results = api_result.get('results', [])
        product_ids = [result['product_id'] for result in api_results]
        
        if not product_ids:
            logger.info("API'den ürün ID'si dönmedi")
            return {
                **api_result,
                'products': [],
                'message': 'Arama kriterlerinize uygun ürün bulunamadı'
            }
        
        # Veritabanından ürünleri getir
        products = get_products_by_ids(product_ids)
        
        # API skorları ile ürünleri birleştir
        api_scores = {result['product_id']: result.get('score', 0) for result in api_results}
        
        # Ürünlere skor ekle
        for product in products:
            product.search_score = api_scores.get(str(product.id), 0)
        
        return {
            **api_result,
            'products': products,
            'total_found': len(products),
            'message': f"{len(products)} ürün bulundu"
        }
        
    except Exception as e:
        logger.error(f"Sonuç işleme hatası: {str(e)}")
        return {
            **api_result,
            'error': True,
            'message': 'Sonuçlar işlenirken hata oluştu',
            'products': []
        }


def search_and_get_products(query: str) -> Dict[str, Any]:
    """
    Tam arama işlemi: API çağrısı + veritabanından ürün getirme
    """
    logger.info(f"Arama başlatıldı: '{query}'")
    
    # 1. API'ye arama sorgusu gönder
    api_result = search_products(query)
    
    # 2. Sonuçları işle ve ürünleri getir
    final_result = process_search_results(api_result)
    
    logger.info(f"Arama tamamlandı: '{query}' - {final_result.get('total_found', 0)} ürün")
    
    return final_result