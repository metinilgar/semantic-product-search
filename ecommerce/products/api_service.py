"""
Ürün verileri için API servisi
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# API Endpoint
API_ENDPOINT = "http://127.0.0.1:8000/products/index"


def send_product_to_api(product):
    """
    Ürün verisini belirtilen API endpoint'ine gönderir
    """
    try:
        # Gender formatını API formatına çevir
        gender_mapping = {
            'E': 'male',
            'K': 'female', 
            'U': 'unisex'
        }
        
        # Image URL oluştur
        image_url = ""
        if product.image and hasattr(product.image, 'url'):
            image_url = f"http://127.0.0.1:8001{product.image.url}"
        
        # API payload oluştur
        payload = {
            "product_id": str(product.id),
            "title": product.name,
            "description": product.description or "",
            "category": product.category.name,
            "gender": gender_mapping.get(product.gender, 'unisex'),
            "tags": product.tags if isinstance(product.tags, list) else [],
            "price": float(product.price),
            "image_url": image_url
        }
        
        # API'ye POST isteği gönder
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # Yanıtı kontrol et
        if response.status_code in [200, 201]:
            logger.info(f"Ürün başarıyla API'ye gönderildi: {product.name} (ID: {product.id})")
            return True
        else:
            logger.error(f"API hatası: {response.status_code} - {response.text} | Ürün: {product.name}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API bağlantı hatası: {str(e)} | Ürün: {product.name}")
        return False
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)} | Ürün: {product.name}")
        return False