# 🚀 Google Colab Kurulum Rehberi

## Hızlı Başlangıç (3 Adım)

### 1️⃣ GPU'yu Aktifleştir
```
Colab Menü → Runtime → Change runtime type → GPU → Save
```

### 2️⃣ Yeni Notebook Aç
https://colab.research.google.com

### 3️⃣ Bu Kodları Çalıştır

#### SEÇENEK A: GitHub'dan (Önerilen)
```python
# Hücre 1: Projeyi indir
!git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
%cd YOUR-REPO/whisperRealTime

# Hücre 2: Başlat
from colab_setup import quick_start_gpu
quick_start_gpu()
```

#### SEÇENEK B: Manuel Upload
```python
# Hücre 1: Dosyaları yükle
from google.colab import files
uploaded = files.upload()  # whisperRealTime.zip'i seç
!unzip -q whisperRealTime.zip
%cd whisperRealTime

# Hücre 2: Başlat
from colab_setup import quick_start_gpu
quick_start_gpu()
```

## 📁 Dosya Hazırlama (Local'de)

```bash
# Terminal'de:
cd /Users/anilyavuz/PiyasaAnaliz
zip -r whisperRealTime.zip whisperRealTime/ \
  -x "whisperRealTime/__pycache__/*" \
  -x "whisperRealTime/.env" \
  -x "whisperRealTime/*.pyc"
```

## 🎯 Model Seçenekleri

### Small Model (Önerilen - Dengeli)
```python
from colab_setup import quick_start_gpu
quick_start_gpu()
```

### Large-v3 Model (En Kaliteli Türkçe)
```python
from colab_setup import quick_start_large
quick_start_large()
```

### Tiny Model (CPU için)
```python
from colab_setup import quick_start_cpu
quick_start_cpu()
```

### Özel Model
```python
import os
os.environ['WHISPER_MODEL'] = 'medium'  # tiny, base, small, medium, large-v3
from colab_setup import main
main()
```

## 🔧 Yapılandırma

### GPU Kontrolü
```python
import torch
print("GPU Mevcut:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:", torch.cuda.get_device_properties(0).total_memory / 1024**3, "GB")
```

### ngrok Auth Token (Gerekirse)
```python
from pyngrok import ngrok
ngrok.set_auth_token("YOUR-NGROK-TOKEN")

# Sonra setup'ı çalıştır
from colab_setup import main
main()
```

Token al: https://dashboard.ngrok.com/get-started/your-authtoken

> Ngrok token'ınız olmazsa script otomatik olarak Cloudflared ile trycloudflare.com domeninde public URL üretmeye çalışır.

### Cloudflared (Token gerekmez)
Script, ngrok başarısız olduğunda Cloudflared binary'sini indirip tüneli otomatik açar.
Elle denemek isterseniz:

```python
!pip install -q cloudflared
!cloudflared tunnel --url http://localhost:5123 --no-autoupdate
```

## 📊 Beklenen Çıktı

```
============================================================
  Faster-Whisper Realtime STT - Colab Setup
  100% ÜCRETSIZ - GPU Destekli
============================================================
🔧 Ortam hazırlanıyor...
   Python 3.10.12

📦 Bağımlılıklar yükleniyor (bu işlem 2-3 dakika sürebilir)...
   Installing flask>=2.3.0...
   ...
   ✅ Tüm paketler yüklendi

🔍 GPU Kontrolü...
   ✅ GPU bulundu: Tesla T4
   📊 CUDA version: 12.2

🤖 Model Yapılandırması
   ✅ Model: small
   Device: GPU

📥 Model indiriliyor...
   İndiriliyor: small
   ✅ Model hazır: small

🌐 ngrok başlatılıyor (port 5123)...
   ✅ Public URL: https://abc123.ngrok-free.app

   📱 Bu URL'i tarayıcınızda açın:
   🔗 https://abc123.ngrok-free.app

============================================================
  💡 KULLANIM TALİMATLARI
============================================================

1. Yukarıdaki Public URL'i tarayıcınızda açın
2. Mikrofon iznini verin
3. 'Başlat' butonuna tıklayın
4. Konuşmaya başlayın!

============================================================
  Sunucu çalışıyor! Konuşmaya başlayabilirsiniz.
============================================================

🚀 Flask sunucusu başlatılıyor...
   Host: 0.0.0.0
   Port: 5123
```

## ❓ Sorun Giderme

### "No module named 'app'" Hatası
```python
# Doğru dizinde misiniz?
!pwd
!ls -la

# app.py görünüyor mu?
%cd whisperRealTime
!ls app.py
```

### "CUDA out of memory" Hatası
```python
# Daha küçük model kullanın
import os
os.environ['WHISPER_MODEL'] = 'tiny'
from colab_setup import main
main()
```

### ngrok Hatası
```python
# Auth token ekleyin
from pyngrok import ngrok
ngrok.set_auth_token("your-token")

# Tekrar deneyin
from colab_setup import main
main()
```

### Public URL Oluşmadı
- Loglarda `ngrok başarısız, Cloudflared deneniyor...` mesajını görmüyorsanız `quick_start_gpu()` komutunu tekrar çalıştırın.
- Cloudflared log'larında URL belirmezse Colab hücresinde şu komutu çalıştırıp tekrar deneyin:
```python
!pkill -f cloudflared || true
from colab_setup import quick_start_gpu
quick_start_gpu()
```
- Hâlâ URL yoksa ngrok token'ınızı ekleyin veya manuel olarak `!cloudflared tunnel --url http://localhost:XXXX` komutunu çalıştırın.

### "Address already in use" / Port 5123 Hatası
1. Colab menüsünden **Runtime → Restart runtime** deyin ve notebook'u tekrar çalıştırın.
2. Alternatif olarak port'u değiştirin:
```python
import os
os.environ["APP_PORT"] = "6000"
from colab_setup import quick_start_gpu
quick_start_gpu()
```
3. Cloudflared çalışıyorsa `!pkill -f cloudflared` ile kapatıp tekrar başlatın.

### Session Timeout
Colab ücretsiz tier'da ~12 saat sonra disconnect olur. Yeniden başlatmak için:

```python
# Dosyalar hala mevcut, sadece setup'ı tekrar çalıştırın
from colab_setup import quick_start_gpu
quick_start_gpu()
```

## 💾 Google Drive'a Kaydet (Opsiyonel)

```python
# Hücre 1: Drive'ı mount et
from google.colab import drive
drive.mount('/content/drive')

# Hücre 2: Dosyaları kopyala
!cp -r whisperRealTime /content/drive/MyDrive/

# Sonraki kullanımlarda:
!cp -r /content/drive/MyDrive/whisperRealTime /content/
%cd /content/whisperRealTime
from colab_setup import quick_start_gpu
quick_start_gpu()
```

## 🎯 Performans Beklentileri

| Model | İlk İndirme | Latency | Kalite | VRAM |
|-------|-------------|---------|--------|------|
| tiny | ~1 dakika | 500ms | Orta | ~1GB |
| small | ~2 dakika | 1-2s | İyi | ~2GB |
| medium | ~5 dakika | 2-3s | Yüksek | ~5GB |
| large-v3 | ~10 dakika | 2-4s | Mükemmel | ~10GB |

**Not:** İlk çalıştırmada model indirilir, sonraki kullanımlarda cache'ten yüklenir (çok hızlı).

## 📝 Notlar

- ✅ Colab ücretsiz GPU: Tesla T4 (16GB VRAM)
- ✅ Tüm modeller çalışır (tiny → large-v3)
- ✅ VAD otomatik aktif (Silero-VAD)
- ✅ Session ~12 saat (ücretsiz tier)
- ⚠️ Internet gerekli (model indirme, ngrok)

## 🔗 Linkler

- Colab: https://colab.research.google.com
- ngrok: https://dashboard.ngrok.com
- Silero VAD: https://github.com/snakers4/silero-vad
- Faster-Whisper: https://github.com/guillaumekln/faster-whisper

---

**Hazırlayan:** Faster-Whisper Realtime STT
**Tarih:** 2025
**Lisans:** Test ve Eğitim Amaçlı
