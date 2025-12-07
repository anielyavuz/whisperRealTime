# 🎙️ Faster-Whisper Realtime STT - Ücretsiz Alternatif

100% ücretsiz, GPU destekli, gerçek zamanlı speech-to-text uygulaması. OpenAI'ın Whisper modelini kullanır.

## 🎯 Neden Bu Uygulama?

| Özellik | ElevenLabs Scribe | Faster-Whisper (Bu Uygulama) |
|---------|-------------------|------------------------------|
| **Maliyet** | ~$0.10/dakika | **%100 ÜCRETSIZ** |
| **Latency** | ~150ms | ~1-2 saniye (GPU) |
| **Türkçe Kalitesi** | Mükemmel | Mükemmel (large-v3) |
| **GPU Gereksinimi** | Yok | Var (Colab'da ücretsiz) |
| **Dil Desteği** | 8 dil | 99+ dil |
| **Offline Kullanım** | Hayır | Evet |

## ✨ Özellikler

- 🆓 **%100 Ücretsiz**: Google Colab'ın ücretsiz GPU'sunu kullanır
- 🚀 **Gerçek Zamanlı**: ~1-2 saniye latency (GPU ile)
- 🌍 **99+ Dil Desteği**: Türkçe, İngilizce ve daha fazlası
- 🎚️ **Model Seçenekleri**: tiny (75MB) → large-v3 (3GB)
- 🎙️ **Akıllı VAD (Silero)**: Sessizlik algılandığında otomatik işler - sabit döngü yok!
- 📊 **Latency Monitoring**: Gerçek zamanlı performans takibi
- 🎨 **Modern UI**: Responsive ve kullanıcı dostu arayüz (en yeni log en üstte)
- ☁️ **Colab Ready**: Google Colab'da çalışmaya hazır

## 🏗️ Proje Yapısı

```
whisperRealTime/
├── app.py                # Flask backend (WebSocket)
├── colab_setup.py       # Colab başlatma script'i
├── requirements.txt     # Python bağımlılıkları
├── templates/
│   └── index.html      # Ana web arayüzü
└── static/
    └── js/
        └── (embedded in index.html)
```

## 🚀 Hızlı Başlangıç - Google Colab (Önerilen)

### 1️⃣ Colab Notebook Oluştur

Yeni bir Google Colab notebook açın: https://colab.research.google.com

### 2️⃣ GPU'yu Etkinleştir

```
Menü → Runtime → Change runtime type → GPU → Save
```

### 3️⃣ Dosyaları Yükle

**Seçenek A: GitHub'dan (Önerilen)**
```python
!git clone https://github.com/your-username/your-repo.git
%cd your-repo/whisperRealTime
```

**Seçenek B: Manuel Upload**
- Sol panel → Files → Upload
- Tüm dosyaları yükleyin

### 4️⃣ Uygulamayı Başlat

```python
# Basit başlatma
from colab_setup import main
main()
```

**Veya model boyutu seçerek:**

```python
# Tiny model (en hızlı, CPU için)
from colab_setup import quick_start_cpu
quick_start_cpu()

# Small model (dengeli, önerilen)
from colab_setup import quick_start_gpu
quick_start_gpu()

# Large-v3 (en kaliteli, GPU gerekli)
from colab_setup import quick_start_large
quick_start_large()
```

### 5️⃣ Kullan!

- Console'da görünen **ngrok URL**'ini kopyalayın
- Tarayıcınızda açın
- Mikrofon iznini verin
- "Başlat" butonuna tıklayın
- Konuşmaya başlayın! 🎤

## 💻 Yerel Ortamda Kullanım

### Gereksinimler

- Python 3.8+
- (Opsiyonel) NVIDIA GPU + CUDA

### Kurulum

```bash
# 1. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 2. Uygulamayı başlatın
python app.py
```

### Model ve GPU Ayarları

```bash
# Model seçimi (varsayılan: small)
export WHISPER_MODEL=small  # tiny, base, small, medium, large-v3

# GPU kullanımı (varsayılan: 1 - aktif)
export USE_GPU=1  # 1: GPU kullan, 0: CPU kullan

# Başlat
python app.py
```

Tarayıcınızda açın: `http://localhost:5123`

## ⚙️ Model Seçimi

| Model | Boyut | Hız | Kalite | Önerilen |
|-------|-------|-----|--------|----------|
| `tiny` | ~75MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | CPU için |
| `base` | ~150MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | CPU için |
| `small` | ~500MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **Dengeli (GPU)** |
| `medium` | ~1.5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | GPU için |
| `large-v3` | ~3GB | ⚡ | ⭐⭐⭐⭐⭐⭐ | **En Kaliteli (GPU)** |

### Model Seçim Tavsiyeleri

**Google Colab (Ücretsiz GPU):**
- `small`: Hız ve kalite dengesi (önerilen)
- `large-v3`: En iyi Türkçe kalitesi

**Yerel CPU:**
- `tiny`: En hızlı
- `base`: Daha iyi kalite

**Yerel GPU (NVIDIA):**
- `small` veya `medium`: Hızlı ve kaliteli
- `large-v3`: En iyi sonuç

## 🔧 Konfigürasyon

### Dil Ayarları

```javascript
// Frontend'de (index.html)
languageSelect: 'tr'  // tr, en, de, fr, es, pt, it, ar, zh, ja, auto
```

### Audio Ayarları

```javascript
sampleRate: 16000      // 8000, 16000 (önerilen), 22050, 44100, 48000
chunkLength: 3         // Her kaç saniyede bir işlensin (1-10)
vadFilter: true        // Sessizlik filtreleme (true önerilen)
```

### Backend Ayarları (Environment Variables)

```bash
WHISPER_MODEL=small    # Model boyutu
USE_GPU=1             # GPU kullanımı (1: evet, 0: hayır)
```

## 📊 WebSocket Protokolü

### Client → Server

**Config Update:**
```json
{
  "type": "config",
  "config": {
    "language": "tr",
    "chunk_length_s": 3,
    "vad_filter": true
  }
}
```

**Audio Chunk:**
```json
{
  "type": "audio",
  "audio_base_64": "base64_encoded_pcm_data",
  "sample_rate": 16000
}
```

### Server → Client

**Session Started:**
```json
{
  "type": "session_started",
  "config": {...}
}
```

**Partial Update (Buffer Status):**
```json
{
  "type": "partial_transcript",
  "text": "[3.2s audio buffered...]",
  "buffer_duration": 3.2
}
```

**Committed Transcript:**
```json
{
  "type": "committed_transcript",
  "text": "transkripsiyon metni",
  "language_code": "tr",
  "latency_ms": 1234,
  "words": [...],
  "buffer_duration": 3.0
}
```

## 🔌 API Endpoint'leri

### `GET /`
Ana web arayüzü

### `GET /health`
Sistem durumu ve model bilgisi

**Response:**
```json
{
  "status": "ok",
  "model": "small",
  "gpu": true,
  "gpu_available": true,
  "gpu_name": "Tesla T4",
  "model_loaded": true
}
```

### `GET /config`
Model ve dil konfigürasyonu

### `WS /ws`
WebSocket endpoint (realtime transcription)

## 🐛 Troubleshooting

### "faster-whisper yüklü değil" Hatası

```bash
pip install faster-whisper
```

### "CUDA bulunamadı" Uyarısı

- **Colab'da:** Runtime → Change runtime type → GPU → Save
- **Yerel:** CUDA Toolkit kurun veya `USE_GPU=0` ile CPU kullanın

### Mikrofon Çalışmıyor

- Tarayıcı izinlerini kontrol edin
- HTTPS bağlantısı gerekli (ngrok otomatik sağlar)
- Chrome/Edge kullanmanız önerilir

### ngrok Token Gerekiyor

```python
# Colab'da
from pyngrok import ngrok
ngrok.set_auth_token("your-token-here")
```

Token almak için: https://dashboard.ngrok.com/get-started/your-authtoken

### Model İndirme Çok Yavaş

- İlk kullanımda model otomatik indirilir
- `small` model ~500MB (2-3 dakika)
- `large-v3` model ~3GB (5-10 dakika)
- Model bir kez indirilir, sonra cache'ten kullanılır

### Yüksek Latency (>5 saniye)

**Colab'da:**
- GPU'yu etkinleştirin (Runtime → Change runtime type → GPU)
- Daha küçük model deneyin (`small` yerine `tiny`)

**Yerel CPU'da:**
- Normal (CPU'da 3-5 saniye)
- `tiny` veya `base` model kullanın

## 📈 Performans Karşılaştırması

### Latency Testleri

| Ortam | Model | Latency | Kalite |
|-------|-------|---------|--------|
| Colab GPU (T4) | tiny | ~500ms | Orta |
| Colab GPU (T4) | small | ~1-2s | İyi |
| Colab GPU (T4) | large-v3 | ~2-3s | Mükemmel |
| Colab CPU | tiny | ~2-3s | Orta |
| Local CPU (i7) | tiny | ~3-5s | Orta |
| Local GPU (RTX 3060) | small | ~800ms | İyi |

### İpuçları

1. **En Düşük Latency İçin:**
   - GPU kullanın
   - `tiny` veya `small` model
   - `chunk_length_s: 2`

2. **En Yüksek Kalite İçin:**
   - GPU kullanın
   - `large-v3` model
   - VAD filter aktif
   - `chunk_length_s: 3-5`

3. **Dengeli (Önerilen):**
   - Colab GPU
   - `small` model
   - `chunk_length_s: 3`
   - VAD aktif

## 🆚 ElevenLabs ile Karşılaştırma

### Faster-Whisper Avantajları ✅

- ✅ %100 ücretsiz (Colab)
- ✅ Offline çalışabilir
- ✅ 99+ dil desteği
- ✅ Veri gizliliği (kendi sunucunuz)
- ✅ Sınırsız kullanım

### ElevenLabs Avantajları ✅

- ✅ Çok düşük latency (~150ms)
- ✅ Setup gerektirmez
- ✅ GPU gerekmez
- ✅ Bulut tabanlı (her yerden erişim)

### Hangi Durumda Ne Kullanmalı?

**Faster-Whisper (Bu Uygulama) Kullan:**
- Yüksek kullanım hacmi (>100 dakika/gün)
- Bütçe kısıtlı
- Veri gizliliği önemli
- Offline çalışma gerekli
- Test ve development

**ElevenLabs Kullan:**
- Ultra-düşük latency kritik (<200ms)
- Production kullanım (güvenilirlik)
- Düşük kullanım hacmi (<30 dakika/gün)
- Setup yapmak istemiyorsanız

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'feat: add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje test ve eğitim amaçlıdır. OpenAI'ın Whisper modeli MIT lisansı altında sunulmaktadır.

## 🔗 Faydalı Linkler

- [Faster-Whisper GitHub](https://github.com/guillaumekln/faster-whisper)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Google Colab](https://colab.research.google.com)
- [ngrok Documentation](https://ngrok.com/docs)
- [Flask-Sock Documentation](https://flask-sock.readthedocs.io/)

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

**Not:** Bu uygulama OpenAI'ın Whisper modelini kullanır ve Google Colab'ın ücretsiz GPU'sundan yararlanır. Colab kullanım politikalarına uygun şekilde kullanın.

## 🎓 Ek Bilgiler

### Model Detayları

Faster-Whisper, OpenAI Whisper'ın [CTranslate2](https://github.com/OpenNMT/CTranslate2) ile optimize edilmiş versiyonudur:
- 4x daha hızlı
- 2x daha az bellek
- Aynı kalite

### Desteklenen Diller

Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, Portekizce, İtalyanca, Arapça, Çince, Japonca, Korece, Rusça, Hintçe ve 80+ dil daha.

Tam liste: https://github.com/openai/whisper#available-models-and-languages

### GPU Gereksinimleri

| Model | VRAM | GPU Önerisi |
|-------|------|-------------|
| tiny | ~1GB | Herhangi bir GPU |
| base | ~1GB | Herhangi bir GPU |
| small | ~2GB | GTX 1060+, Colab T4 |
| medium | ~5GB | RTX 2060+, Colab T4 |
| large-v3 | ~10GB | RTX 3080+, A100 |

Google Colab ücretsiz T4 GPU: 16GB VRAM (tüm modeller çalışır)

### Colab Sınırlamaları

- **Ücretsiz Tier**: ~12 saat session, sonra restart
- **RAM**: 12GB (yeterli)
- **Disk**: 100GB (yeterli)
- **GPU**: Tesla T4 (16GB VRAM, mükemmel)

Session disconnect olursa setup script'i tekrar çalıştırmanız yeterli.
