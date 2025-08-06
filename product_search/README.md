# Product Search - AI Destekli Ürün Arama Servisi

Modern e-ticaret uygulamaları için geliştirilmiş, yapay zeka destekli semantik ürün arama servisi. Google Gemini AI ve Qdrant vektör veritabanı kullanarak kullanıcıların doğal dilde ürün arama yapmalarını sağlar.

![](https://github.com/user-attachments/assets/1674a8b6-08dd-4de3-ad49-0ca525996708)

## Nasıl Çalışır?

### Ürün İndeksleme Süreci
1. **Ürün Verisi**: API üzerinden ürün bilgileri (başlık, açıklama, kategori, cinsiyet, etiketler, fiyat) alınır
2. **Embedding Üretimi**: Gemini embedding modeli ile 1536 boyutlu vektör üretilir
3. **Vektör Saklama**: Qdrant veritabanında metadata ile birlikte saklanır

### Arama Süreci
1. **Sorgu Analizi**: Kullanıcının doğal dil sorgusu Gemini AI ile analiz edilir
   - Cinsiyet tespiti (erkek/kadın)
   - Ürün türleri belirleme
   - Sorgu genişletme ve bağlamsal kelime ekleme
2. **Vektör Arama**: Qdrant'ta cosine benzerlik ile filtrelenmiş arama
3. **Sonuç Sıralama**: Benzerlik skoruna göre sıralı sonuçlar

## Özellikler

- **AI Destekli Arama**: Gemini 2.5 Flash Lite ile doğal dil sorguları anlama
- **Akıllı Filtreleme**: Cinsiyet, kategori, ürün türü otomatik tespiti  
- **Semantik Arama**: Qdrant vektör veritabanı ile anlam tabanlı arama
- **Batch İşleme**: Toplu ürün indeksleme desteği (100 ürüne kadar)
- **Fallback Sistemi**: AI başarısız olursa kural tabanlı analiz
- **Health Monitoring**: Sistem durumu izleme ve diagnostik
- **Yüksek Performans**: FastAPI ile async API
- **RESTful API**: Swagger UI ile dokümantasyon

## Teknoloji Stack

- **Backend**: FastAPI + Python 3.11
- **AI**: Google Gemini 2.5 Flash Lite
- **Vector DB**: Qdrant 
- **Embedding**: Gemini Embedding (1536 boyut)
- **Deployment**: Docker + Docker Compose

## Kurulum

### Docker ile (Önerilen)

```bash
# Projeyi indirin
git clone <repository-url>
cd product_search

# API anahtarını ayarlayın (.env dosyası oluşturun)
echo "GEMINI_API_KEY=your_actual_gemini_api_key_here" > .env
echo "LOG_LEVEL=INFO" >> .env

# Servisleri başlatın
docker-compose up -d

# API sağlığını test edin
curl http://localhost:8000/health
```

### Manuel Kurulum

```bash
# Python ortamı
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Bağımlılıklar
pip install -r requirements.txt

# Qdrant başlatın
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# API anahtarı
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Servisi başlatın
uvicorn app.main:app --reload
```

### API Anahtarı

[Google AI Studio](https://makersuite.google.com/app/apikey)'dan API anahtarı alın ve `.env` dosyasına ekleyin.

## Ana Endpoint'ler

### Ürün İndeksleme - POST /products/index
Tek ürün ekleme ve güncelleme:

```bash
curl -X POST "http://localhost:8000/products/index" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "suit_001",
    "title": "Siyah Takım Elbise",
    "description": "Klasik kesim erkek takım elbise, ofis ve resmi toplantılar için ideal",
    "category": "takım",
    "gender": "male",
    "tags": ["klasik", "ofis", "resmi"],
    "price": 1299.99,
    "image_url": "https://example.com/suit.jpg"
  }'
```

### Doğal Dil Arama - POST /search
AI destekli semantik arama:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "iş görüşmesi için şık takım elbise"}'
```

**Yanıt:**
```json
{
  "query": "iş görüşmesi için şık takım elbise",
  "gender": "male",
  "product_types": ["takım", "gömlek"],
  "expanded_query": "resmi ofis takım elbise profesyonel iş giyim klasik",
  "results": [
    {
      "product_id": "suit_001",
      "title": "Siyah Takım Elbise",
      "price": 1299.99,
      "image_url": "https://example.com/suit.jpg",
      "score": 0.92
    }
  ]
}
```

### Toplu Ürün İndeksleme - POST /products/batch_index
100'e kadar ürünü aynı anda işleme:

```bash
curl -X POST "http://localhost:8000/products/batch_index" \
  -H "Content-Type: application/json" \
  -d '{"products": [...]}'
```

### Sorgu Analizi - POST /search/analyze
Sadece AI analizi (arama yapmadan test için):

```bash
curl -X POST "http://localhost:8000/search/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "düğün için kırmızı elbise"}'
```

**Yanıt:**
```json
{
  "gender": "female",
  "product_types": ["elbise", "ayakkabı", "çanta"],
  "expanded_query": "düğün kırmızı elbise şık gece abiye"
}
```

## API Dokümantasyonu

Servis çalıştıktan sonra detaylı dokümantasyon için:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Yapılandırma

### config.yaml
```yaml
qdrant:
  url: "http://qdrant:6333"      # Docker container adı
  collection_name: "products"
  vector_size: 1536
  distance: "Cosine"

gemini:
  model_name: "models/gemini-2.5-flash-lite"
  embedding_model: "gemini-embedding-001"
  api_key_env: "GEMINI_API_KEY"
  
search:
  max_results: 20
  score_threshold: 0.3
```

### Environment Variables
```bash
# .env dosyası
GEMINI_API_KEY=your_actual_api_key_here
QDRANT_URL=http://localhost:6333  # isteğe bağlı
LOG_LEVEL=INFO                    # isteğe bağlı
```

## Proje Yapısı

```
product_search/
├── app/
│   ├── main.py              # FastAPI uygulaması
│   ├── schemas.py           # Pydantic modelleri
│   ├── settings.py          # Konfigürasyon
│   ├── routers/             # API endpoint'leri
│   │   ├── products.py      # Ürün işlemleri
│   │   └── search.py        # Arama işlemleri
│   └── services/            # İş mantığı
│       ├── llm_service.py   # Gemini AI entegrasyonu
│       └── vector_service.py # Qdrant işlemleri
├── config.yaml             # Ana konfigürasyon
├── requirements.txt         # Python bağımlılıkları
├── docker-compose.yml       # Docker yapılandırması
└── Dockerfile              # Container tanımı
```

## Sistem Mimarisi

### Servis Bileşenleri
- **product-search-app**: Ana FastAPI servisi (Port: 8000)
- **product-search-qdrant**: Qdrant vektör veritabanı (Port: 6333, 6334)

### Veri Akışı
1. **Ürün İndeksleme**: API → Embedding → Qdrant
2. **Arama**: Query → AI Analizi → Embedding → Vektör Arama → Sonuçlar

## Sorun Giderme

### Yaygın Sorunlar

| Problem | Çözüm |
|---------|-------|
| Qdrant bağlantı hatası | `docker-compose up qdrant` ile başlatın |
| Gemini API hatası | `.env` dosyasında `GEMINI_API_KEY` kontrol edin |
| Boş arama sonuçları | Önce ürün ekleyin, `/products/collection/info` ile kontrol edin |
| AI analizi başarısız | Fallback sistemi devreye girer, logları kontrol edin |

### Test

```bash
# Sistem sağlığı
curl http://localhost:8000/health

# Test arama
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test ürün"}'
```

## Lisans

MIT Lisansı altında açık kaynak olarak sunulmaktadır.