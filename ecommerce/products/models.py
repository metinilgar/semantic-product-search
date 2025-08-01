from django.db import models
import uuid

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategori")
    material_type = models.CharField(max_length=100, verbose_name="Malzeme Türü")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Cinsiyet")
    stock_quantity = models.PositiveIntegerField(verbose_name="Stok Miktarı")
    size_info = models.CharField(max_length=50, verbose_name="Beden Bilgisi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Resim")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
    
    def __str__(self):
        return self.name
