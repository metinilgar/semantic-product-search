from django.db import models
import uuid
import re

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    GENDER_CHOICES = [
        ('E', 'Erkek'),
        ('K', 'Kadın'),
        ('U', 'Unisex'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Ürün Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategori")
    material_type = models.CharField(max_length=100, verbose_name="Malzeme Türü")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Cinsiyet")
    tags = models.JSONField(default=list, blank=True, verbose_name="Etiketler", help_text="Liste formatında: ['etiket1', 'etiket2']")
    stock_quantity = models.PositiveIntegerField(verbose_name="Stok Miktarı")
    size_info = models.CharField(max_length=50, verbose_name="Beden Bilgisi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Resim")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
    
    def generate_tags_from_description(self):
        """Description'dan otomatik tags oluştur"""
        if not self.description:
            return []
        
        # Türkçe karakter dönüşümü
        text = self.description.lower()
        
        # Noktalama işaretlerini temizle
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Kelimeleri ayır
        words = text.split()
        
        # Kısa kelimeleri ve yaygın kelimeleri filtrele
        stop_words = {'ve', 'ile', 'bir', 'bu', 'şu', 'o', 'çok', 'en', 'da', 'de', 'ta', 'te', 
                     'için', 'olan', 'her', 'tüm', 'bütün', 'gibi', 'kadar', 'daha', 'hem',
                     'ya', 'veya', 'ama', 'fakat', 'ancak', 'lakin', 'ise', 'eğer', 'ki'}
        
        # Anlamlı kelimeleri seç (3+ karakter, stop word değil)
        tags = []
        for word in words:
            if len(word) >= 3 and word not in stop_words and word not in tags:
                tags.append(word)
        
        # Maksimum 10 tag
        return tags[:10]
    
    def save(self, *args, **kwargs):
        """Kaydetmeden önce tags'ı otomatik oluştur"""
        self.tags = self.generate_tags_from_description()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
