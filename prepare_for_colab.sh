#!/bin/bash

# Faster-Whisper Realtime STT - Colab İçin Dosya Hazırlama
# Bu script, projeyi Colab'a upload etmek için zip'ler

echo "=========================================="
echo "  Colab İçin Dosyalar Hazırlanıyor..."
echo "=========================================="
echo ""

# Dizini kontrol et
if [ ! -f "app.py" ]; then
    echo "❌ Hata: app.py bulunamadı!"
    echo "   Bu script'i whisperRealTime/ dizininde çalıştırın."
    exit 1
fi

# Önceki zip'i sil
if [ -f "../whisperRealTime.zip" ]; then
    echo "🗑️  Eski zip dosyası siliniyor..."
    rm "../whisperRealTime.zip"
fi

echo "📦 Dosyalar zipleniyor..."

# Gerekli dosyaları zipla
cd ..
zip -r whisperRealTime.zip whisperRealTime/ \
    -x "whisperRealTime/__pycache__/*" \
    -x "whisperRealTime/.env" \
    -x "whisperRealTime/*.pyc" \
    -x "whisperRealTime/.git/*" \
    -x "whisperRealTime/.gitignore" \
    -x "whisperRealTime/app2.py" \
    -x "whisperRealTime/prepare_for_colab.sh" \
    -x "whisperRealTime/*.log" \
    -q

if [ $? -eq 0 ]; then
    echo "✅ Hazır: whisperRealTime.zip"
    echo ""
    echo "📊 Dosya boyutu:"
    ls -lh whisperRealTime.zip | awk '{print "   " $9 ": " $5}'
    echo ""
    echo "📁 İçerik:"
    unzip -l whisperRealTime.zip | grep -E "(app.py|colab_setup.py|requirements.txt|templates/index.html)" | awk '{print "   " $4}'
    echo ""
    echo "🚀 Sonraki Adımlar:"
    echo "   1. Google Colab'da yeni notebook aç"
    echo "   2. Runtime → Change runtime type → GPU (veya CPU)"
    echo "   3. Bu kodu çalıştır:"
    echo ""
    echo "      # 1. Zip dosyasını yükle ve çıkar"
    echo "      from google.colab import files"
    echo "      uploaded = files.upload()  # whisperRealTime.zip'i seç"
    echo "      !unzip -q whisperRealTime.zip"
    echo "      %cd whisperRealTime"
    echo ""
    echo "      # 2. Uygulamayı başlat (GPU ile)"
    echo "      from colab_setup import quick_start_gpu"
    echo "      quick_start_gpu()"
    echo ""
    echo "   💡 Notlar:"
    echo "      - Port çakışması otomatik olarak çözülür."
    echo "      - Public URL için Localtunnel kullanılır (ngrok/cloudflared gerekmez)."
    echo "      - CPU kullanmak isterseniz: from colab_setup import quick_start_cpu; quick_start_cpu()"
    echo "      - Bir sorun olursa: Runtime → Restart runtime menüsünü kullanıp adımları tekrarlayın."
    echo ""
else
    echo "❌ Zip oluşturulamadı!"
    exit 1
fi
