# 🛍️ Product Search - AI Destekli Ürün Arama Servisi

Modern e-ticaret uygulamaları için geliştirilmiş, yapay zeka destekli semantik ürün arama servisi. Kullanıcıların doğal dilde arama yapmalarını sağlar.

## ✨ Özellikler

- 🤖 **AI Destekli Arama**: Gemini AI ile doğal dil sorguları anlama
- 🎯 **Akıllı Filtreleme**: Cinsiyet, kategori, ürün türü otomatik tespiti  
- 🔍 **Semantik Arama**: Qdrant vektör veritabanı ile anlam tabanlı arama
- ⚡ **FastAPI**: Yüksek performanslı async API
- 🐳 **Docker Ready**: Tek komutla çalıştırma
- 🔗 **Kolay Entegrasyon**: RESTful API ile herhangi bir frontend'e entegre

## 🛠️ Teknoloji Stack

- **Backend**: FastAPI + Python 3.11
- **AI**: Google Gemini 2.5 Flash Lite
- **Vector DB**: Qdrant 
- **Embedding**: Gemini Embedding (1536 boyut)
- **Deployment**: Docker + Docker Compose

## 🚀 Hızlı Başlangıç

### Docker ile (Önerilen)

```bash
# Projeyi indirin
git clone <repository-url>
cd product_search

# API anahtarını ayarlayın (.env dosyası oluşturun)
echo "GEMINI_API_KEY=your_actual_gemini_api_key_here" > .env
echo "LOG_LEVEL=INFO" >> .env

# Servisleri başlatın (Qdrant + API)
docker-compose up -d

# Servis durumunu kontrol edin
docker-compose ps

# API sağlığını test edin
curl http://localhost:8000/health

# Logları takip edin (isteğe bağlı)
docker-compose logs -f product-search
```

#### Docker Servisleri
- **product-search-app**: Ana API servisi (Port: 8000)
- **product-search-qdrant**: Qdrant vektör veritabanı (Port: 6333, 6334)

#### Docker Komutları
```bash
# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Servisleri yeniden başlat
docker-compose restart

# Veri ile birlikte temizle
docker-compose down -v

# Logları görüntüle
docker-compose logs -f [servis-adı]
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

### API Anahtarı Alma

1. [Google AI Studio](https://makersuite.google.com/app/apikey)'ya gidin
2. "Create API Key" butonuna tıklayın
3. API anahtarını `.env` dosyasına ekleyin

## 📚 API Kullanımı

### 🏷️ Ürün Ekleme - POST /products/index

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

### 🔍 Ürün Arama - POST /search

```bash
# Doğal dil ile arama
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "iş görüşmesi için şık takım elbise"}'

# Yanıt
{
  "query": "iş görüşmesi için şık takım elbise",
  "gender": "male",
  "product_types": ["takım", "gömlek"],
  "results": [
    {
      "product_id": "suit_001",
      "title": "Siyah Takım Elbise",
      "price": 1299.99,
      "score": 0.92
    }
  ]
}
```

### 🧠 Sorgu Analizi - POST /search/analyze

```bash
# Sadece AI analizi için
curl -X POST "http://localhost:8000/search/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "düğün için kırmızı elbise"}'
```

## 📖 API Dokümantasyonu

Servis çalıştıktan sonra detaylı dokümantasyon için:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## ⚙️ Yapılandırma

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

## 🏗️ Proje Yapısı

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

## 🐛 Sorun Giderme

### Yaygın Sorunlar

| Problem | Çözüm |
|---------|-------|
| Qdrant bağlantı hatası | `docker run -p 6333:6333 qdrant/qdrant` ile başlatın |
| Gemini API hatası | `.env` dosyasında `GEMINI_API_KEY` kontrol edin |
| Boş arama sonuçları | Önce ürün ekleyin, collection durumunu kontrol edin |

### Test Etme
```bash
# Sistem sağlığı
curl http://localhost:8000/health

# Test ürünü ekleme
curl -X POST http://localhost:8000/products/index \
  -H "Content-Type: application/json" \
  -d '{"product_id":"test","title":"Test Ürün","description":"Test açıklama","category":"test","gender":"male","tags":["test"],"price":100,"image_url":"http://test.com"}'

# Test arama
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test ürün"}'
```

## 📝 Lisans

MIT Lisansı altında açık kaynak olarak sunulmaktadır.