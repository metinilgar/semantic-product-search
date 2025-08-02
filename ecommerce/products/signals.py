"""
Ürün işlemleri için Django signals
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .api_service import send_product_to_api

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def product_created_handler(sender, instance, created, **kwargs):
    """
    Yeni ürün oluşturulduğunda API'ye gönder
    """
    if created:  # Sadece yeni ürün oluşturulduğunda
        try:
            logger.info(f"Yeni ürün oluşturuldu: {instance.name} (ID: {instance.id})")
            
            # API'ye gönder
            success = send_product_to_api(instance)
            
            if success:
                logger.info(f"Ürün başarıyla API'ye gönderildi: {instance.name}")
            else:
                logger.warning(f"Ürün API'ye gönderilemedi: {instance.name}")
                
        except Exception as e:
            logger.error(f"Signal handler hatası: {instance.name} - {str(e)}")