# Semantic Product Search - Frontend

Kullanıcıların doğal dil sorguları aracılığıyla ilgili ürünleri bulmasını sağlayan LLM destekli bir semantik ürün arama sistemi.

## Kurulum ve Çalıştırma

### Gereksinimler

```bash
pip install -r requirements.txt
```

### Sunucuyu Başlatma

Proje **8001 portunda** çalışacak şekilde konfigüre edilmiştir.

#### Yöntem 1: Otomatik Script (Önerilen)

```bash
python run_server.py
```

#### Yöntem 2: Manuel

```bash
python manage.py runserver 127.0.0.1:8001
```

#### Yöntem 3: Virtual Environment ile

```bash
source venv/bin/activate
python manage.py runserver 127.0.0.1:8001
```

Sunucu başlatıldıktan sonra tarayıcınızda `http://127.0.0.1:8001` adresine giderek uygulamaya erişebilirsiniz.

## Admin Panel

### Superuser Bilgileri

- **Kullanıcı Adı:** `admin`
- **E-posta:** `admin@example.com`
- **Admin Panel URL:** `http://127.0.0.1:8001/admin/`

### Yeni Superuser Oluşturma

```bash
python manage.py createsuperuser
```

## Model Yapısı

### UUID Primary Keys

Projede hem `Category` hem de `Product` modelleri UUID primary key kullanır:

- Otomatik olarak benzersiz UUID'ler oluşturulur
- Veritabanı kayıt aşamasında UUID atanır
- Admin panelde UUID'ler readonly field olarak görüntülenir

### Product Alanları

- `name`: Ürün adı
- `description`: Ürün açıklaması (TextField)
- `category`: Kategori (ForeignKey)
- `material_type`: Malzeme türü
- `gender`: Cinsiyet (E/K/U)
- `tags`: Etiketler (JSONField - otomatik oluşturulur)
- `stock_quantity`: Stok miktarı
- `size_info`: Beden bilgisi
- `price`: Fiyat
- `image`: Ürün resmi

### Otomatik Tag Oluşturma

- Tags alanı `description` metninden otomatik oluşturulur
- 3+ karakter uzunluğunda anlamlı kelimeler seçilir
- Yaygın Türkçe kelimeler (ve, ile, bir, etc.) filtrelenir
- Maksimum 10 tag oluşturulur
- Admin panelinde readonly olarak görüntülenir

### API Entegrasyonu

Admin panelden yeni ürün eklendiğinde otomatik olarak şu endpoint'e POST isteği gönderilir:

- **Endpoint:** `http://127.0.0.1:8000/products/index`
- **Format:**

```json
{
  "product_id": "UUID string",
  "title": "Ürün adı",
  "description": "Ürün açıklaması",
  "category": "Kategori adı",
  "gender": "male/female/unisex",
  "tags": ["etiket1", "etiket2"],
  "price": 199.99,
  "image_url": "http://127.0.0.1:8001/media/products/..."
}
```

### Migration Geçmişi

- `0001_initial.py`: İlk model oluşturma (BigAutoField)
- `0002_alter_category_id_alter_product_id.py`: UUID'ye geçiş
- `0003_product_description_product_tags.py`: Description ve tags alanları

## Port Konfigürasyonu

Varsayılan port `eticaret/settings.py` dosyasında `DEVELOPMENT_PORT = 8001` olarak ayarlanmıştır. Bu portu değiştirmek isterseniz bu dosyayı düzenleyebilirsiniz.
