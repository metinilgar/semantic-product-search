# Semantic Product Search 🛍️

Kullanıcıların doğal dil sorguları aracılığıyla ilgili ürünleri bulmasını sağlayan LLM destekli bir semantik ürün arama sistemi. Bu proje, modern yapay zeka teknolojilerini kullanarak e-ticaret deneyimini geliştiren tam kapsamlı bir çözüm sunar.

[Demo Videosu (YouTube)](https://youtu.be/_ad3iPhRNgg)
![](https://github.com/user-attachments/assets/1674a8b6-08dd-4de3-ad49-0ca525996708)

## Proje Genel Bakış

Bu repository, iki ana bileşenden oluşan entegre bir semantik ürün arama sistemi içerir:

### AI Destekli Arama Motoru
- **Google Gemini AI** ile doğal dil işleme
- **Qdrant vektör veritabanı** ile semantik arama
- FastAPI tabanlı yüksek performanslı API servisi
- Toplu ürün indeksleme ve akıllı filtreleme

### Django E-ticaret Frontend
- Kullanıcı dostu arama arayüzü
- Admin panel ile ürün yönetimi
- Otomatik API entegrasyonu
- Modern ve responsive tasarım

## Nasıl Çalışır?

1. **Ürün Ekleme**: Admin panelden ürünler eklenir, otomatik olarak AI sistemine gönderilir
2. **Vektör İndeksleme**: Ürün bilgileri embedding'e dönüştürülür ve vektör veritabanına kaydedilir
3. **Doğal Arama**: Kullanıcılar "siyah dar pantolon istiyorum" gibi doğal ifadelerle arama yapar
4. **AI Analizi**: Gemini AI sorguyu analiz eder, cinsiyet ve ürün türlerini tespit eder
5. **Semantik Eşleşme**: Vektör veritabanında anlam tabanlı arama yapılır
6. **Akıllı Sonuçlar**: Benzerlik skoruna göre sıralanmış sonuçlar döndürülür

## Proje Yapısı

```
semantic-product-search/
├──  product_search/            # AI Destekli Arama Servisi
│   ├── app/                    # FastAPI uygulaması
│   ├── config.yaml             # Sistem konfigürasyonu
│   ├── docker-compose.yml      # Docker servisleri
│   └── README.md               # 👉 Detaylı kurulum ve kullanım
│
├──  ecommerce/                # Django E-ticaret Frontend
│   ├── products/              # Ürün yönetimi
│   ├── templates/             # Web arayüzü
│   ├── run_server.py          # Otomatik başlatma
│   └── README.md              # 👉 Frontend kurulum ve özellikler
│
└── README.md                  # Bu dosya (genel bakış)
```

## Hızlı Başlangıç

### 1. AI Arama Servisini Başlatın

```bash
cd product_search
echo "GEMINI_API_KEY=your_api_key_here" > .env
docker-compose up -d
```

### 2. Örnek Ürün Verilerini Yükleyin (İsteğe Bağlı)

Proje, hazır Qdrant snapshot dosyası ile birlikte gelir. Bu snapshot, SQLite veritabanındaki örnek ürünlerle senkronize edilmiş 50+ ürün içerir:

**Qdrant Dashboard ile yükleme:**
1. **Dashboard'a erişin**: http://localhost:6333/dashboard
2. **Collections** sekmesine gidin
3. **Eski collection'ı silin** (varsa): Mevcut collection'ın yanındaki **Delete** butonuna tıklayın
4. **Upload Snapshot** butonuna tıklayın
5. `products-8252181329589640-2025-08-06-11-21-58.snapshot` dosyasını seçin
6. **Collection Name** alanına `products` yazın
7. Yükleme tamamlandıktan sonra **products** collection'ını görebilirsiniz

**Not**: `ecommerce/db.sqlite3` dosyasındaki ürünler ile Qdrant snapshot'ında bulunan ürünler tamamen senkronizedir.

### 3. Django Frontend'i Başlatın

```bash
cd ecommerce
pip install -r requirements.txt
python run_server.py
```

### 4. Uygulamayı Kullanın

- **Frontend**: http://127.0.0.1:8001
- **Admin Panel**: http://127.0.0.1:8001/admin (admin/admin123)
- **API Dokümantasyonu**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard 

## Detaylı Dokümantasyon

Her bileşen için ayrıntılı kurulum ve kullanım kılavuzları:

### [AI Arama Servisi - README](./product_search/README.md)
- **Teknoloji**: FastAPI + Google Gemini AI + Qdrant
- **Port**: 8000
- **Snapshot**: `products-8252181329589640-2025-08-06-11-21-58.snapshot` (50+ örnek ürün)
- **Özellikler**:
  - Doğal dil sorgu analizi
  - Semantik vektör arama
  - Toplu ürün indeksleme
  - RESTful API
  - Health monitoring

### [Django E-ticaret Frontend - README](./ecommerce/README.md)
- **Teknoloji**: Django + Bootstrap + AJAX
- **Port**: 8001
- **Veritabanı**: `db.sqlite3` (Qdrant snapshot ile senkronize)
- **Özellikler**:
  - Kullanıcı dostu arama arayüzü
  - Admin panel ürün yönetimi
  - Otomatik API entegrasyonu
  - UUID tabanlı model yapısı
  - Otomatik tag oluşturma

## Ana Özellikler

### Akıllı Arama
- **Doğal Dil**: "iş görüşmesi için şık takım elbise"
- **Cinsiyet Tespiti**: Otomatik erkek/kadın/unisex belirleme
- **Ürün Türü Analizi**: Kategori ve ürün tiplerini anlama
- **Sorgu Genişletme**: Bağlamsal kelimeler ekleme

### Yüksek Doğruluk
- **Semantik Eşleşme**: Anlam tabanlı arama
- **Skor Hesaplama**: Benzerlik skorları ile sıralama
- **Fallback Sistemi**: AI başarısızlığında kural tabanlı analiz

### Performans
- **Async API**: FastAPI ile yüksek performans
- **Vektör Optimizasyonu**: Qdrant ile hızlı arama
- **Batch İşleme**: 100'e kadar ürün toplu indeksleme

---

**🚀 Hemen başlamak için uygun README'yi seçin ve talimatları izleyin!**