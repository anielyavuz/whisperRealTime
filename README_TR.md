# 🎤 Whisper Realtime STT

**Ücretsiz, gerçek zamanlı konuşma tanıma (Speech-to-Text) uygulaması**

Google Colab'da GPU ile çalışan, public URL üzerinden erişilebilen, Türkçe destekli realtime STT çözümü.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anielyavuz/whisperRealTime/blob/main/WhisperRealtime_Colab.ipynb)

---

## ✨ Özellikler

- ✅ **%100 Ücretsiz** - Hiçbir API anahtarı veya ödeme gerektirmez
- ✅ **GPU Destekli** - Google Colab T4 GPU ile 1-2 saniye latency
- ✅ **Public URL** - Cloudflare Tunnel ile her yerden erişim
- ✅ **Türkçe Mükemmel** - OpenAI Whisper modeli kullanır
- ✅ **Gerçek Zamanlı** - WebSocket ile anlık transkripsiyon
- ✅ **VAD (Voice Activity Detection)** - Sessizlik otomatik filtrelenir
- ✅ **Çoklu Dil** - 99 dil desteği

---

## 🚀 Hızlı Başlangıç

### Google Colab'da Kullanım (Önerilir)

1. **Colab Notebook'u Aç:**

   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anielyavuz/whisperRealTime/blob/main/WhisperRealtime_Colab.ipynb)

2. **GPU'yu Etkinleştir:**
   - `Runtime > Change runtime type > GPU` seçin

3. **Hücreleri Çalıştır:**
   - Her hücreyi sırayla çalıştırın (Shift+Enter)

4. **Public URL'ye Tıkla:**
   - URL ekranda gösterilecek
   - Mikrofon izni verin ve konuşmaya başlayın!

**Detaylı Kullanım:** [COLAB_KULLANIM.md](COLAB_KULLANIM.md)

---

### Yerel Kullanım (Local)

```bash
# 1. Repository'yi klonla
git clone https://github.com/anielyavuz/whisperRealTime.git
cd whisperRealTime

# 2. Sanal ortam oluştur (önerilir)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Bağımlılıkları kur
pip install -r requirements.txt

# 4. Uygulamayı başlat
python app.py

# 5. Tarayıcıda aç
# http://localhost:5000
```

---

## 📋 Sistem Gereksinimleri

### Colab (Önerilir)
- Google hesabı (ücretsiz)
- GPU runtime (ücretsiz T4 GPU)
- Modern web tarayıcısı

### Yerel Kurulum
- Python 3.8+
- 4GB+ RAM
- GPU (opsiyonel, CPU'da da çalışır)
- Mikrofon

---

## ⚙️ Konfigürasyon

### Model Seçimi

`app.py` içinde veya ortam değişkeni:

```python
os.environ['WHISPER_MODEL'] = 'small'
```

**Mevcut Modeller:**
- `tiny` - ~75MB, en hızlı, düşük doğruluk
- `base` - ~150MB, hızlı, orta doğruluk
- `small` - ~500MB, dengeli, iyi doğruluk ⭐ (önerilen)
- `medium` - ~1.5GB, yavaş, yüksek doğruluk
- `large-v3` - ~3GB, en yavaş, en yüksek doğruluk

### Dil Ayarı

Web arayüzünde dropdown'dan seçin veya:

```python
config = {'language': 'tr'}  # tr, en, de, fr, es, pt, it, ar, zh, ja...
```

---

## 🏗️ Mimari

```
┌─────────────┐         WebSocket          ┌──────────────┐
│   Browser   │ ◄─────────────────────────► │ Flask Server │
│  (Mikrofon) │    PCM Audio (Base64)      │   (Python)   │
└─────────────┘                             └──────┬───────┘
                                                   │
                                            ┌──────▼────────┐
                                            │ Faster-Whisper│
                                            │  (GPU/CPU)    │
                                            └───────────────┘
                                                   │
                                            ┌──────▼────────┐
                                            │  Silero VAD   │
                                            │  (Opsiyonel)  │
                                            └───────────────┘
```

**Teknolojiler:**
- **Backend:** Flask + Flask-Sock (WebSocket)
- **STT Model:** Faster-Whisper (OpenAI Whisper optimized)
- **VAD:** Silero VAD (PyTorch)
- **Public URL:** Ngrok (pyngrok) - En güvenilir çözüm
- **Frontend:** Vanilla JavaScript (Web Audio API)

---

## 📊 Performans

| Ortam | Model | Device | Latency | Doğruluk |
|-------|-------|--------|---------|----------|
| Colab | small | T4 GPU | 1-2s | Yüksek |
| Colab | tiny | T4 GPU | 0.5-1s | Orta |
| Colab | large-v3 | T4 GPU | 2-4s | Çok Yüksek |
| Local | small | RTX 3060 | 1-2s | Yüksek |
| Local | small | CPU (i7) | 5-10s | Yüksek |

---

## 🛠️ Dosya Yapısı

```
whisperRealTime/
├── app.py                      # Ana Flask uygulaması
├── colab_launcher.py           # Colab otomatik başlatıcı
├── WhisperRealtime_Colab.ipynb # Colab notebook
├── requirements.txt            # Python bağımlılıkları
├── templates/
│   └── index.html             # Web arayüzü
├── static/                    # CSS/JS (opsiyonel)
├── COLAB_KULLANIM.md          # Colab kullanım kılavuzu
├── README.md                  # Bu dosya (EN)
└── README_TR.md               # Bu dosya (TR)
```

---

## 🔧 Sorun Giderme

### Public URL Görünmüyor
```python
# Cloudflare Tunnel loglarını kontrol et
!ps aux | grep cloudflared
```

### GPU Kullanılmıyor
```python
import torch
print(f"GPU: {torch.cuda.is_available()}")
print(f"Name: {torch.cuda.get_device_name(0)}")
```

### Mikrofon Çalışmıyor
- HTTPS bağlantısı gereklidir (Cloudflare otomatik sağlar)
- Tarayıcıda mikrofon izni verin
- Mikrofon ayarlarını kontrol edin

**Detaylı Sorun Giderme:** [COLAB_KULLANIM.md](COLAB_KULLANIM.md)

---

## 🌟 Kullanım Senaryoları

- 📝 **Toplantı Notları** - Realtime transkripsiyon
- 🎙️ **Podcast Yazımı** - Uzun ses kayıtları
- 🎤 **Canlı Altyazı** - Etkinlikler için
- 📚 **Ders Notları** - Dersler ve seminerlerde
- 🗣️ **Çeviri Hazırlığı** - Önce yazıya çevir, sonra çevir

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şunları yapın:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull Request açın

---

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🙏 Teşekkürler

- [OpenAI Whisper](https://github.com/openai/whisper) - STT modeli
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized inference
- [Cloudflare](https://www.cloudflare.com/) - Tunnel servisi
- [Google Colab](https://colab.research.google.com/) - Ücretsiz GPU

---

## 📞 İletişim

Sorular veya öneriler için:
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/anielyavuz/whisperRealTime/issues)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/anielyavuz/whisperRealTime/discussions)

---

## ⭐ Yıldız Vermeyi Unutmayın!

Bu projeyi beğendiyseniz yıldız vererek destek olabilirsiniz 🌟

---

**Made with ❤️ using OpenAI Whisper & Google Colab**
