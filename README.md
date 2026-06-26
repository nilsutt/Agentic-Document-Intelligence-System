# Banking Agentic Platform MVP

Bankacılık sektörü için çok-modlu PDF belgelerinden "Agentic Bilgi Çıkarımı" yapan, Clean Architecture prensiplerine dayalı Python MVP sistemi.

## Özellikler

- **Clean Architecture & Factory Pattern:** Katmanlar arası kesin izolasyon. `LLMFactory` ve `EmbeddingFactory` sayesinde ortam değişkeninden (`.env`) Ollama'dan OpenAI'ye geçiş yapılabilir.
- **Hiyerarşik Chunking:** PyMuPDF ile ToC ve font boyutuna dayalı akıllı metin bölme (Tree-Structure).
- **Agentic Retrieval & Validator Node:** LangGraph ile kurulan ReAct döngüsü, sadece bilgi getirmekle kalmaz; ürettiği cevabı bir **Validator** adımından geçirerek kaynak belirtilmemişse veya halüsinasyon varsa kendi kendini düzeltir (Self-Correction).
- **Dayanıklılık (Resilience):** LLM çağrılarında Tenacity (Exponential Backoff with Jitter) ve PyBreaker (Circuit Breaker) koruması.
- **Değerlendirme (Evaluation):** Otonom `scripts/evaluate.py` ile sistemin başarısını ölçecek test altyapısı.

---

## Kurulum ve Çalıştırma

Sistemi iki farklı yöntemle ayağa kaldırabilirsiniz:

### Yöntem 1: Doğrudan Python ile

Hızlıca test etmek ve debug yapmak için:

1. `venv` oluşturun ve `pip install -r requirements.txt` ile bağımlılıkları yükleyin.
2. Ollama'nın arka planda çalıştığından emin olun (`ollama serve`).
3. Çevre değişkenlerini ayarlayın (`cp .env.example .env`).
4. Uygulamayı başlatın:
  ```bash
   uvicorn src.presentation.api.app:app --reload --port 8000
  ```

### Yöntem 2: Docker ile

Sistemi tüm bağımlılıkları ile izole bir şekilde çalıştırmak için:

1. Docker Desktop'ın çalıştığından emin olun.
2. Komutu çalıştırın:
  ```bash
   docker-compose up --build
  ```

### API Dokümantasyonu (Swagger UI)
Sistem, API entegrasyonları için hazır olan, standartlara uygun (OAS 3.1) RESTful API arayüzüne sahiptir.

![API Dokümantasyonu](./assets/api_docs.png)

## Kullanım

### 1. CLI Üzerinden

**PDF Yükleme:**

```bash
python -m src.presentation.cli.main ingest "path/to/document.pdf"
```

**Sorgu Yapma:**

```bash
python -m src.presentation.cli.main ask "Sözleşmenin faiz oranları nedir?"
```

**İnteraktif Sohbet (REPL):**

```bash
python -m src.presentation.cli.main chat
```

### 2. API Üzerinden

**Örnek cURL İstekleri:**

```bash
# Belge Yükleme
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
     -H "Content-Type: application/json" \
     -d '{"file_path": "path/to/document.pdf"}'

# Soru Sorma
curl -X POST "http://localhost:8000/api/v1/queries/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "Önemli maddeleri özetle", "conversation_id": "12345"}'
```

## Test ve Değerlendirme

### 1. Test ve Kalite Güvencesi
Sistem, `pytest` kullanılarak hem unit hem de entegrasyon testleri ile doğrulanmıştır. Kod tabanımızdaki kritik modüller (Chunking, Agent, API) %100 test kapsama oranına sahiptir.

**Testleri Çalıştırma:**
```bash
# Tüm testleri çalıştırmak için:
pytest

# Test kapsamını (coverage) görüntülemek için:
pytest --cov=src
```

### 2. Otonom Değerlendirme Scripti:
Mülakat Q&A testlerini koşturmak için:
```bash
python scripts/evaluate.py
# Çıktı: Agent başlatılıyor... (3/3 Soru Geçildi, Ortalama Keyword Skoru: 76.7%)
```

---

> **Not:** Detaylı Mimari Tasarım için [DESIGN.md](./DESIGN.md) dosyasına bakınız.

---

## Kısa Teknik Not: Tasarım Kararları

Bu projede, sadece çalışan bir kod yazmak değil; sürdürülebilir, güvenli ve "Enterprise-Ready" bir mimari oluşturmak hedeflenmiştir. Bu hedef doğrultusunda şu yapılar kullanılmıştır:

**Tree-Structure (Hiyerarşik) Chunking:** Sabit boyutlu (flat) chunking yerine, belgenin yapısal hiyerarşisini (Section/Sub-section) koruyan Tree-Structure yöntemi tercih edilmiştir. Bu sayede LLM, metin parçalarını hangi ana başlık altında değerlendirmesi gerektiğini bilir; bu da bankacılık verilerinde "bağlam kaybı" ve "halüsinasyon" riskini minimize eder.

**Clean Architecture & Factory Pattern:** Uygulama katmanı (Domain), altyapıdan (Infrastructure) tamamen izole edilmiştir. Factory Pattern kullanılarak LLM ve Vektör Veritabanı sağlayıcıları (Ollama, OpenAI, FAISS vb.) arayüzleştirilmiştir. Bu sayede sistem, kurum içi regülasyonlar (KVKK) gereği yerel bir modelden bulut modeline geçişi, tek bir satır kod değiştirmeden sadece `.env` güncellemesi ile destekler.
