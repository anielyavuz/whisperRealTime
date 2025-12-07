import socket
import sys
import os
import subprocess
import threading
import time
from importlib import util, import_module

def is_colab():
    """Google Colab ortamında olup olmadığını kontrol eder."""
    return "google.colab" in sys.modules

def find_free_port(start_port=7860):
    """Belirtilen porttan başlayarak boş bir port bulur."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1

def install_dependencies():
    """requirements.txt dosyasındaki bağımlılıkları kurar."""
    print("📦 Gerekli paketler kuruluyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✅ Paketler başarıyla kuruldu.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Paket kurulumu sırasında hata oluştu: {e}")
        sys.exit(1)

def install_localtunnel():
    """localtunnel'i npm ile kurar."""
    print("🚇 Localtunnel kuruluyor...")
    try:
        # npm'in -g flag'i ile global olarak kurulması, path sorunlarını önler.
        subprocess.check_call(["npm", "install", "-g", "localtunnel", "-q"])
        print("✅ Localtunnel kuruldu.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Localtunnel kurulumu sırasında hata oluştu: {e}")
        print("   Colab ortamında olduğunuzdan ve npm'in kurulu olduğundan emin olun.")
        return False

def start_localtunnel_tunnel(port):
    """Localtunnel tünelini başlatır ve genel URL'yi yazdırır."""
    print(f"🚇 Localtunnel tüneli {port} portu için başlatılıyor...")
    localtunnel_process = subprocess.Popen(
        ["lt", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    public_url = None
    for _ in range(15): # 15 saniye içinde URL'yi bulmaya çalış
        line = localtunnel_process.stdout.readline()
        if "your url is:" in line:
            public_url = line.split(":")[-1].strip()
            break
        time.sleep(1)

    if public_url:
        print("\n" + "="*60)
        print("✅ UYGULAMA ERİŞİM LİNKİ (PUBLIC URL)")
        print(f"   {public_url}  <-- Bu linke tıklayın")
        print("="*60 + "\n")
    else:
        print("❌ Localtunnel tünel URL'si alınamadı. Lütfen logları kontrol edin.")

def start_gradio_tunnel(port):
    """Gradio'nun kendi tünel mekanizmasıyla public URL üretir."""
    print(f"🌐 Gradio public URL oluşturuluyor (port {port})...")
    try:
        from gradio import networking
    except Exception as e:
        print(f"⚠️  Gradio tüneli için gerekli modül yüklenemedi: {e}")
        return None

    share_url = None
    try:
        # Yeni API'lerde ilave parametreler olabileceği için olası TypeError'ları da yakalıyoruz
        try:
            share_url = networking.setup_tunnel(
                port,
                share_token=None,
                controller=None,
            )
        except TypeError:
            share_url = networking.setup_tunnel(port)
    except Exception as e:
        print(f"⚠️  Gradio tüneli açılamadı: {e}")
        return None

    if share_url:
        print("\n" + "="*60)
        print("✅ UYGULAMA ERİŞİM LİNKİ (PUBLIC URL - Gradio)")
        print(f"   {share_url}  <-- Bu linke tıklayın")
        print("="*60 + "\n")
    else:
        print("⚠️  Gradio tünel URL'si alınamadı.")
    return share_url

def start_flask_app(host='0.0.0.0', port=5000):
    """Flask uygulamasını belirtilen host ve portta çalıştırır."""
    try:
        # app.py dosyasını dinamik olarak yükle
        spec = util.spec_from_file_location("app", "app.py")
        app_module = util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        app = app_module.app

        print("\n" + "="*60)
        print("🚀 Flask sunucusu başlatılıyor...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print("="*60)
        print("  Sunucu çalışıyor! Konuşmaya başlayabilirsiniz.")
        print("="*60 + "\n")

        # Werkzeug loglarını bastırmak için
        log = import_module('werkzeug.serving')
        log.get_logger = lambda: type('dummy_logger', (), {'info': lambda *args, **kwargs: None, 'error': lambda *args, **kwargs: None})()

        app.run(host=host, port=port, debug=False, use_reloader=False)

    except OSError as e:
        if e.errno == 98: # Address already in use
            print(f"❌ Hata: Port {port} zaten kullanılıyor.")
            print("   Lütfen Colab runtime'ı yeniden başlatın (Runtime -> Restart runtime) ve tekrar deneyin.")
        else:
            print(f"❌ Flask sunucusu başlatılırken hata oluştu: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Beklenmedik bir hata oluştu: {e}")
        sys.exit(1)

def main(device_type="gpu"):
    """Ana kurulum ve başlatma fonksiyonu."""
    if not is_colab():
        print("Bu script sadece Google Colab ortamında çalışmak üzere tasarlanmıştır.")
        return

    print("============================================================")
    print("    Faster-Whisper Realtime STT - Google Colab Kurulumu")
    print("============================================================")

    # 1. Bağımlılıkları kur
    install_dependencies()

    # 2. Boş bir port bul
    port = find_free_port()
    print(f"✅ Boş port bulundu: {port}")

    # 3. Ortam değişkenlerini ayarla
    os.environ['DEVICE_TYPE'] = device_type
    print(f"⚙️  Cihaz tipi ayarlandı: {device_type.upper()}")

    # 4. Flask uygulamasını bir thread'de başlat
    flask_thread = threading.Thread(target=start_flask_app, args=('0.0.0.0', port))
    flask_thread.daemon = True
    flask_thread.start()
    time.sleep(3) # Sunucunun başlaması için bekle

    # 5. Önce Gradio tüneli ile public URL üretmeyi dene, olmazsa Localtunnel'a düş
    share_url = start_gradio_tunnel(port)
    if not share_url:
        print("⚠️  Gradio tüneli başarısız, Localtunnel denenecek...")
        if not install_localtunnel():
            return
        start_localtunnel_tunnel(port)

    print("\n============================================================")
    print("🎉 Kurulum tamamlandı! Yukarıdaki linkten uygulamaya erişebilirsiniz.")
    print("   Uygulamayı durdurmak için Colab'daki 'Stop' butonuna basın.")
    print("============================================================")

    # Ana thread'in sonlanmasını engelle
    flask_thread.join()

def quick_start_gpu():
    """GPU için hızlı başlangıç fonksiyonu."""
    print("\n" + "="*60)
    print("🚀 UYGULAMA BAŞLATILIYOR (GPU MODU)")
    print("="*60 + "\n")
    print("Bilgilendirme:")
    print("  - Cihaz: GPU")
    print("  - Varsayılan dil: Türkçe (arayüzden değiştirebilirsiniz)")
    print("\nİpuçları:")
    print("  - Her 3 saniyede bir transkripsiyon yapılır")
    print("  - VAD aktif (sessizlik otomatik filtrelenir)")
    print("  - Latency: ~1-2 saniye (GPU)")
    print("="*60 + "\n")
    main(device_type="cuda")

def quick_start_cpu():
    """CPU için hızlı başlangıç fonksiyonu."""
    print("\n" + "="*60)
    print("🚀 UYGULAMA BAŞLATILIYOR (CPU MODU)")
    print("="*60 + "\n")
    print("Bilgilendirme:")
    print("  - Cihaz: CPU")
    print("  - Varsayılan dil: Türkçe (arayüzden değiştirebilirsiniz)")
    print("\nİpuçları:")
    print("  - Her 3 saniyede bir transkripsiyon yapılır")
    print("  - VAD aktif (sessizlik otomatik filtrelenir)")
    print("  - Latency: ~3-5 saniye (CPU)")
    print("="*60 + "\n")
    main(device_type="cpu")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cpu":
        quick_start_cpu()
    else:
        quick_start_gpu()
