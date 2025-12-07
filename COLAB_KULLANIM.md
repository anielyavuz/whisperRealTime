# 🎤 Whisper Realtime STT - Google Colab Kullanım Kılavuzu

## 🌟 Özellikler

- ✅ **%100 Ücretsiz** - Hiçbir ücret yok
- ✅ **GPU Destekli** - 1-2 saniye latency
- ✅ **Public URL** - Her yerden erişim (Cloudflare Tunnel)
- ✅ **Türkçe Desteği** - Mükemmel doğruluk
- ✅ **Kolay Kurulum** - 5 dakikada hazır

---

## 🚀 Hızlı Başlangıç

### Yöntem 1: Colab Notebook (En Kolay)

1. **Notebook'u Aç:**
   - `WhisperRealtime_Colab.ipynb` dosyasını Google Colab'da aç
   - Veya bu linke tıkla: [Colab'da Aç](https://colab.research.google.com/github/KULLANICI_ADI/whisperRealTime/blob/main/WhisperRealtime_Colab.ipynb)

2. **GPU'yu Etkinleştir:**
   - `Runtime > Change runtime type > GPU` seçin
   - `Save` butonuna tıklayın

3. **Hücreleri Çalıştır:**
   - Her hücreyi sırayla çalıştırın (Shift+Enter)
   - Son hücre çalıştığında Public URL göreceksiniz

4. **Kullanmaya Başla:**
   - Public URL'ye tıklayın
   - Mikrofon izni verin
   - "Başlat" butonuna basın ve konuşun!

---

### Yöntem 2: Manuel Kurulum

Google Colab'da yeni bir notebook oluşturun ve aşağıdaki adımları takip edin:

#### Adım 1: Proje Dosyalarını Yükle

```python
# GitHub'dan klonla
!git clone https://github.com/KULLANICI_ADI/whisperRealTime.git
%cd whisperRealTime
```

veya dosyaları manuel yükleyin:
- Sol panelden "Files" > "Upload"
- Şu dosyaları yükleyin:
  - `colab_launcher.py`
  - `app.py`
  - `requirements.txt`
  - `templates/index.html`

#### Adım 2: Gerekli Paketleri Kur

```python
!pip install flask flask-cors flask-sock faster-whisper numpy torch ctranslate2 -q
```

#### Adım 3: Cloudflare Tunnel Kur

```python
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared
!chmod +x /usr/local/bin/cloudflared
```

#### Adım 4: Uygulamayı Başlat

```python
import colab_launcher
colab_launcher.quick_start_gpu()
```

Public URL ekranda görünecektir! 🎉

---

## 📋 Sistem Gereksinimleri

- **Google Colab** - Ücretsiz hesap yeterli
- **GPU Runtime** - T4 GPU (ücretsiz)
- **Tarayıcı** - Chrome, Firefox, Safari (mikrofon izni gerekli)

---

## ⚙️ Konfigürasyon

### Model Seçimi

`app.py` içinde veya ortam değişkeni ile:

```python
os.environ['WHISPER_MODEL'] = 'small'  # tiny, base, small, medium, large-v3
```

**Model Karşılaştırması:**

| Model | Boyut | Hız | Doğruluk | Önerilen |
|-------|-------|-----|----------|----------|
| tiny | ~75MB | En hızlı | Düşük | Hız öncelikli |
| base | ~150MB | Hızlı | Orta | - |
| small | ~500MB | Dengeli | İyi | ✅ Genel kullanım |
| medium | ~1.5GB | Yavaş | Yüksek | Kalite öncelikli |
| large-v3 | ~3GB | En yavaş | En yüksek | Maksimum kalite |

### Dil Değiştirme

Web arayüzünde dropdown'dan seçin veya `app.py` içinde:

```python
config = {
    'language': 'tr',  # tr, en, de, fr, es, pt, it, ar, zh, ja
    'vad_filter': True
}
```

### GPU vs CPU

```python
# GPU ile başlat (önerilir)
colab_launcher.quick_start_gpu()

# CPU ile başlat
colab_launcher.quick_start_cpu()
```

---

## 🔧 Sorun Giderme

### Public URL Görünmüyor veya "..." ile Gösteriliyor

**Sorun:** Cloudflare Tunnel URL'si tam gösterilmiyor veya "https://trycloudflare.com..." şeklinde kesik görünüyor.

**✅ ÇÖZÜLDÜ! Güncel versiyon `pycloudflared` kullanıyor:**

Artık güvenilir bir Python kütüphanesi kullanıyoruz. Güncel kodu çekin:

```python
!git pull origin main
import colab_launcher
colab_launcher.quick_start_gpu()
```

**Yeni Özellikler:**
- ✅ **pycloudflared** - Modern, güvenilir URL yakalama
- ✅ **Otomatik fallback** - Başarısız olursa raw subprocess
- ✅ **stderr parsing** - Cloudflared'in gerçek çıktı kanalı
- ✅ **Üç katmanlı parse** - Regex, pipe split, kelime bazlı

**Hala Sorun Varsa:**

**Çözüm 1 - Debug Modu:**
```python
# Raw subprocess ile debug modu
from colab_launcher import start_cloudflare_tunnel_raw
start_cloudflare_tunnel_raw(5000, debug=True)
# stderr çıktısını gösterir
```

**Çözüm 2 - Manuel pycloudflared:**
```python
# Direkt pycloudflared kullan
!pip install pycloudflared -q
from pycloudflared import try_cloudflare

tunnel = try_cloudflare(port=5000)
print(f"🌐 URL: {tunnel.tunnel}")
```

**Çözüm 3 - Notebook'taki Troubleshooting Hücresi:**
- Notebook'ta "🔍 URL Göremiyorsanız" başlıklı hücreyi çalıştırın
- Otomatik olarak URL'yi bulur ve gösterir

**NOT:**
- ✅ Token/auth gerektirmez
- ✅ %100 ücretsiz
- ✅ HTTPS otomatik
- ✅ Her session yeni URL (normal)

### Mikrofon Çalışmıyor

**Sorun:** Ses algılanmıyor.

**Çözüm:**
1. Tarayıcıda mikrofon izni verin
2. HTTPS bağlantısı kullanıldığından emin olun (Cloudflare otomatik sağlar)
3. Mikrofon ayarlarını kontrol edin
4. Başka bir tarayıcı deneyin

### GPU Kullanılmıyor

**Sorun:** CPU kullanılıyor, GPU değil.

**Çözüm:**
1. `Runtime > Change runtime type > GPU` seçin
2. Runtime'ı yeniden başlatın
3. GPU kontrolü:
   ```python
   import torch
   print(f"GPU Available: {torch.cuda.is_available()}")
   print(f"GPU Name: {torch.cuda.get_device_name(0)}")
   ```

### Bağlantı Kesilmesi

**Sorun:** WebSocket bağlantısı düşüyor.

**Çözüm:**
1. Sayfayı yenileyin (F5)
2. "Durdur" > "Başlat" yapın
3. Colab session'ı kontrol edin (90 dakika idle timeout var)
4. Runtime'ı yeniden başlatın

### Yavaş Transcription

**Sorun:** Latency çok yüksek (>5 saniye).

**Çözüm:**
1. GPU'nun kullanıldığını doğrulayın
2. Daha küçük model deneyin (small yerine tiny)
3. VAD filtrelerini kontrol edin
4. Network bağlantınızı kontrol edin

---

## 💡 İpuçları ve En İyi Pratikler

### Performans Optimizasyonu

1. **GPU Kullanın:**
   - T4 GPU ile ~1-2 saniye latency
   - CPU ile ~5-10 saniye latency

2. **Doğru Model Seçin:**
   - Genel kullanım: `small`
   - Hız öncelikli: `tiny` veya `base`
   - Kalite öncelikli: `medium` veya `large-v3`

3. **VAD Kullanın:**
   - Sessizlikleri otomatik filtreler
   - Gereksiz processing'i önler
   - Daha iyi kullanıcı deneyimi

### Kullanım Senaryoları

**1. Toplantı Notları:**
```python
os.environ['WHISPER_MODEL'] = 'small'
os.environ['LANGUAGE'] = 'tr'
```

**2. Podcast Transkripti:**
```python
os.environ['WHISPER_MODEL'] = 'large-v3'  # Maksimum kalite
```

**3. Hızlı Demo:**
```python
os.environ['WHISPER_MODEL'] = 'tiny'  # Minimum latency
```

### Colab Session Yönetimi

- **Session Süresi:** Colab session'ları 90 dakika idle timeout'a sahip
- **Aktif Tutma:** Periyodik olarak sayfayı kontrol edin
- **Yeniden Bağlanma:** Session düşerse notebook'u yeniden çalıştırın

### Public URL Paylaşımı

- URL'yi paylaşabilirsiniz (session açıkken herkes kullanabilir)
- URL kalıcı DEĞİLDİR - her session'da değişir
- Güvenlik: URL'yi sadece güvendiğiniz kişilerle paylaşın

---

## 🔒 Güvenlik Notları

### Mikrofon İzinleri

- Tarayıcı mikrofon erişimi ister
- HTTPS üzerinden çalıştığı için güvenlidir
- İzinleri istediğiniz zaman iptal edebilirsiniz

### Public URL

- Cloudflare Tunnel ücretsiz ve güvenlidir
- TLS/SSL otomatik olarak sağlanır
- URL'yi sadece güvendiğiniz kişilerle paylaşın

### Veri Gizliliği

- Ses verisi doğrudan Colab'da işlenir
- Harici servislere gönderilmez
- Session kapandığında tüm veriler silinir

---

## 📊 Performans Metrikleri

### Beklenen Latency

| Senaryo | Model | Device | Latency |
|---------|-------|--------|---------|
| Optimum | small | T4 GPU | 1-2s |
| Hızlı | tiny | T4 GPU | 0.5-1s |
| Kaliteli | large-v3 | T4 GPU | 2-4s |
| CPU Fallback | small | CPU | 5-10s |

### Bellek Kullanımı

| Model | VRAM | RAM |
|-------|------|-----|
| tiny | ~500MB | ~1GB |
| small | ~2GB | ~2GB |
| large-v3 | ~5GB | ~4GB |

Colab ücretsiz T4 GPU: 15GB VRAM (yeterli)

---

## 🆘 Destek ve Yardım

### Hata Logları

Hata durumunda logları kontrol edin:

```python
# Flask logs
!tail -f app.log

# Cloudflare logs
!ps aux | grep cloudflared
```

### Debug Modu

```python
# app.py içinde
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Health Check

```python
import requests
response = requests.get('http://localhost:5000/health')
print(response.json())
```

---

## 🔄 Güncellemeler

Projeyi güncellemek için:

```bash
cd whisperRealTime
git pull origin main
```

Paketleri güncellemek için:

```bash
pip install --upgrade faster-whisper torch
```

---

## 📝 Sık Sorulan Sorular

**S: Colab ücretsiz mi?**
C: Evet, GPU dahil tamamen ücretsiz. Session limitleri var ama normal kullanım için yeterli.

**S: Public URL ne kadar süre geçerli?**
C: Colab session açık olduğu sürece. Session kapanınca URL de geçersiz olur.

**S: Hangi diller destekleniyor?**
C: Whisper 99 dili destekler. Türkçe, İngilizce, Almanca, Fransızca vb.

**S: Ücretli alternatiflerden farkı ne?**
C: Tamamen ücretsiz ama session limitleri var. Kalite ve performans benzer.

**S: Offline çalışır mı?**
C: Hayır, Colab internet bağlantısı gerektirir.

---

## 🎓 Gelişmiş Kullanım

### Özel Model Yükleme

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
    download_root="/content/models"  # Özel dizin
)
```

### Transcript Kaydetme

```javascript
// index.html içinde
function addCommittedTranscript(text, langCode, latencyMs) {
    // Transcript'i kaydet
    let transcripts = JSON.parse(localStorage.getItem('transcripts') || '[]');
    transcripts.push({
        text: text,
        language: langCode,
        timestamp: new Date().toISOString(),
        latency: latencyMs
    });
    localStorage.setItem('transcripts', JSON.stringify(transcripts));
}
```

### Webhook Entegrasyonu

```python
# app.py içinde
import requests

def send_webhook(text):
    requests.post('https://your-webhook-url.com', json={'text': text})

# WebSocket handler'da
if full_text.strip():
    send_webhook(full_text.strip())
```

---

## 📚 Kaynaklar

- [Faster-Whisper GitHub](https://github.com/guillaumekln/faster-whisper)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Google Colab Guide](https://colab.research.google.com/)

---

## 📄 Lisans

MIT License - Ücretsiz kullanım için.

---

**🎉 Keyifli Kullanımlar!**

Sorularınız için: [GitHub Issues](https://github.com/KULLANICI_ADI/whisperRealTime/issues)
