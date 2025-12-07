"""
Whisper Realtime STT - Google Colab Launcher
Cloudflare Tunnel ile ücretsiz public URL

Kullanım:
1. Bu dosyayı Colab'a yükleyin
2. quick_start_gpu() fonksiyonunu çağırın
3. Public URL ile uygulamaya erişin
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path


def is_colab():
    """Google Colab ortamında mı kontrol et"""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def install_requirements():
    """Gerekli paketleri kur"""
    print("📦 Gerekli paketler kuruluyor...")
    requirements = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "flask-sock>=0.6.0",
        "faster-whisper>=0.10.0",
        "numpy>=1.24.0",
        "torch>=2.0.0",
        "ctranslate2>=3.20.0"
    ]

    for req in requirements:
        print(f"  Installing {req}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", req, "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    print("✅ Tüm paketler kuruldu!")


def install_cloudflared():
    """Cloudflared binary'sini indir ve kur"""
    print("☁️  Cloudflare Tunnel kuruluyor...")

    try:
        # Cloudflared binary'sini indir
        subprocess.check_call([
            "wget",
            "-q",
            "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "-O",
            "/usr/local/bin/cloudflared"
        ])

        # Çalıştırılabilir yap
        subprocess.check_call(["chmod", "+x", "/usr/local/bin/cloudflared"])

        print("✅ Cloudflare Tunnel kuruldu!")
        return True

    except Exception as e:
        print(f"❌ Cloudflare Tunnel kurulumu başarısız: {e}")
        return False


def start_cloudflare_tunnel_pycloudflared(port):
    """
    Cloudflare Tunnel başlat - pycloudflared kullanarak (Önerilen)
    Modern ve güvenilir yöntem
    """
    print(f"🌐 Cloudflare Tunnel başlatılıyor (pycloudflared ile, port {port})...")

    try:
        # pycloudflared'i import et
        try:
            from pycloudflared import try_cloudflare
        except ImportError:
            print("📦 pycloudflared kuruluyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pycloudflared", "-q"])
            from pycloudflared import try_cloudflare

        # Flask'ın hazır olduğunu doğrula
        print("🔍 Flask sunucusu kontrol ediliyor...")
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()

        if result != 0:
            print(f"⚠️  Flask port {port}'da hazır değil, 5 saniye bekleniyor...")
            time.sleep(5)

        # Tunnel'ı başlat ve URL'yi al
        print("🔍 Public URL oluşturuluyor...")
        tunnel = try_cloudflare(port=port)
        public_url = tunnel.tunnel

        if public_url:
            print("\n" + "="*70)
            print("✅ UYGULAMANIZ HAZIR!")
            print("="*70)
            print(f"\n🌐 PUBLIC URL: {public_url}")
            print("\n📝 Bu linke tıklayarak uygulamaya erişebilirsiniz!")
            print("   (Link kalıcıdır, Colab session açık kaldığı sürece çalışır)")
            print("\n💡 İpucu: URL'yi CTRL+Click ile açabilirsiniz")
            print("\n⏱️  İlk açılış 10-15 saniye sürebilir (model yükleme)")
            print("   Eğer 502 hatası alırsanız, 10 saniye bekleyip yenileyin")
            print("="*70 + "\n")

            return tunnel
        else:
            print("❌ URL alınamadı")
            return None

    except Exception as e:
        print(f"⚠️  pycloudflared başarısız: {e}")
        print("   Fallback yöntemine geçiliyor...\n")
        return None


def start_cloudflare_tunnel_raw(port, debug=False):
    """
    Cloudflare Tunnel başlat - Raw subprocess (Fallback)
    Geliştirilmiş stderr parsing
    """
    print(f"🌐 Cloudflare Tunnel başlatılıyor (raw subprocess, port {port})...")

    try:
        import re
        import select

        # Tunnel'ı başlat - stderr'ı yakalamak çok önemli!
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        print("🔍 Public URL bekleniyor (stderr'dan okuma)...")

        public_url = None
        attempts = 0
        max_attempts = 50  # Daha fazla deneme

        # stderr'dan oku (cloudflared URL'yi stderr'a yazar!)
        while attempts < max_attempts and not public_url:
            # stderr'dan satır oku
            line = process.stderr.readline()

            if line:
                line = line.strip()

                # Debug modu
                if debug:
                    print(f"[STDERR] {line}")

                # URL'yi ara - cloudflared formatı: "| https://xxx.trycloudflare.com |"
                if "trycloudflare.com" in line:
                    # Method 1: Regex ile URL yakala
                    url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)

                    if url_match:
                        public_url = url_match.group(0)
                        break

                    # Method 2: Pipe karakterleri arası parse
                    if '|' in line:
                        parts = line.split('|')
                        for part in parts:
                            part = part.strip()
                            if part.startswith('https://') and 'trycloudflare.com' in part:
                                public_url = part
                                break

                    # Method 3: Kelime bazlı parse
                    if not public_url:
                        words = line.split()
                        for word in words:
                            if 'trycloudflare.com' in word:
                                # Temizle
                                cleaned = re.sub(r'[^a-zA-Z0-9\-\.:/]', '', word)
                                if 'https://' in cleaned:
                                    public_url = cleaned
                                    break

            attempts += 1
            time.sleep(0.1)

        if public_url:
            print("\n" + "="*70)
            print("✅ UYGULAMANIZ HAZIR!")
            print("="*70)
            print(f"\n🌐 PUBLIC URL: {public_url}")
            print("\n📝 Bu linke tıklayarak uygulamaya erişebilirsiniz!")
            print("   (Link kalıcıdır, Colab session açık kaldığı sürece çalışır)")
            print("\n💡 İpucu: URL'yi CTRL+Click ile açabilirsiniz")
            print("="*70 + "\n")
        else:
            print("\n⚠️  Public URL otomatik olarak alınamadı.")
            print("   stderr'dan okuma başarısız oldu.")
            print("   Manuel kontrol için:")
            print("   1. Yeni bir hücrede: !ps aux | grep cloudflared")
            print("   2. Tunnel çalışıyorsa logları kontrol edin\n")

        return process

    except Exception as e:
        print(f"❌ Cloudflare Tunnel başlatılamadı: {e}")
        import traceback
        if debug:
            traceback.print_exc()
        return None


def start_ngrok_tunnel(port):
    """
    Ngrok Tunnel başlat - En güvenilir yöntem
    """
    print(f"🌐 Ngrok Tunnel başlatılıyor (port {port})...")

    try:
        # pyngrok'u import et
        try:
            from pyngrok import ngrok, conf
        except ImportError:
            print("📦 pyngrok kuruluyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "-q"])
            from pyngrok import ngrok, conf

        # Ngrok auth token ayarla
        NGROK_AUTH_TOKEN = "36VvZGBmkwJsts4fedxEoTihnkr_7eYk3TAmBRQcchvbdCusL"
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        print("✅ Ngrok auth token ayarlandı")

        # Flask'ın hazır olduğunu doğrula
        print("🔍 Flask sunucusu kontrol ediliyor...")
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()

        if result != 0:
            print(f"⚠️  Flask port {port}'da hazır değil, 5 saniye bekleniyor...")
            time.sleep(5)

        # Tunnel'ı başlat
        print("🔍 Public URL oluşturuluyor...")
        public_url = ngrok.connect(port, bind_tls=True)  # HTTPS zorunlu (mikrofon için)

        if public_url:
            url_str = str(public_url)

            print("\n" + "="*70)
            print("✅ UYGULAMANIZ HAZIR!")
            print("="*70)
            print(f"\n🌐 PUBLIC URL: {url_str}")
            print("\n📝 Bu linke tıklayarak uygulamaya erişebilirsiniz!")
            print("   (Link kalıcıdır, Colab session açık kaldığı sürece çalışır)")
            print("\n💡 İpucu: URL'yi CTRL+Click ile açabilirsiniz")
            print("\n⏱️  İlk açılış 10-15 saniye sürebilir (model yükleme)")
            print("   Eğer yüklenmezse, sayfayı yenileyin")
            print("\n🎯 Ngrok Dashboard: https://dashboard.ngrok.com/observability/http-requests")
            print("="*70 + "\n")

            return public_url
        else:
            print("❌ URL alınamadı")
            return None

    except Exception as e:
        print(f"❌ Ngrok başlatılamadı: {e}")
        import traceback
        traceback.print_exc()
        return None


def start_cloudflare_tunnel(port, debug=False):
    """
    Cloudflare Tunnel başlat - Akıllı yöntem seçimi
    Önce pycloudflared, başarısız olursa raw subprocess
    """
    # Önce modern kütüphane ile dene
    result = start_cloudflare_tunnel_pycloudflared(port)

    if result:
        return result

    # Başarısız olursa raw subprocess
    print("🔄 Alternatif yöntem deneniyor...\n")
    return start_cloudflare_tunnel_raw(port, debug=debug)


def create_app_file():
    """app.py dosyasını oluştur (eğer yoksa)"""
    app_path = Path("app.py")

    if app_path.exists():
        print("✅ app.py dosyası mevcut")
        return True

    print("📝 app.py dosyası oluşturuluyor...")

    app_content = '''"""
Faster-Whisper Realtime STT - Flask App
"""

import os
import json
import base64
import numpy as np
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_sock import Sock
import threading
import time

app = Flask(__name__)
CORS(app)
sock = Sock(app)

whisper_model = None
vad_model = None
model_lock = threading.Lock()
vad_lock = threading.Lock()


def get_vad_model():
    """Lazy load Silero VAD model"""
    global vad_model
    if vad_model is None:
        with vad_lock:
            if vad_model is None:
                try:
                    import torch
                    print("🔄 Loading Silero VAD model...")
                    vad_model, utils = torch.hub.load(
                        repo_or_dir='snakers4/silero-vad',
                        model='silero_vad',
                        force_reload=False,
                        onnx=False
                    )
                    print("✅ VAD model loaded")
                except Exception as e:
                    print(f"⚠️  VAD yüklenemedi: {e}")
                    return None
    return vad_model


def get_model():
    """Lazy load Whisper model"""
    global whisper_model
    if whisper_model is None:
        with model_lock:
            if whisper_model is None:
                from faster_whisper import WhisperModel

                device = os.environ.get("DEVICE_TYPE", "cuda")
                model_size = os.environ.get("WHISPER_MODEL", "small")

                try:
                    import torch
                    if device == "cuda" and not torch.cuda.is_available():
                        device = "cpu"
                    elif device == "cuda":
                        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
                except:
                    device = "cpu"

                compute_type = "float16" if device == "cuda" else "int8"

                print(f"🔄 Loading Whisper {model_size} on {device}...")
                whisper_model = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type
                )
                print(f"✅ Model loaded!")

    return whisper_model


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check"""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    except:
        gpu_available = False
        gpu_name = None

    return jsonify({
        'status': 'ok',
        'model': os.environ.get("WHISPER_MODEL", "small"),
        'gpu_available': gpu_available,
        'gpu_name': gpu_name
    })


@sock.route('/ws')
def websocket(ws):
    """WebSocket endpoint"""
    print("🔌 New WebSocket connection")

    try:
        model = get_model()
        vad = get_vad_model()
    except Exception as e:
        ws.send(json.dumps({'type': 'error', 'error': str(e)}))
        return

    audio_buffer = []
    sample_rate = 16000
    config = {'language': 'tr', 'vad_filter': True}

    ws.send(json.dumps({
        'type': 'session_started',
        'config': config,
        'vad_enabled': vad is not None
    }))

    try:
        while True:
            message = ws.receive()
            if message is None:
                break

            try:
                data = json.loads(message)
            except:
                continue

            msg_type = data.get('type', '')

            if msg_type == 'config':
                config.update(data.get('config', {}))
                ws.send(json.dumps({'type': 'config_updated', 'config': config}))

            elif msg_type == 'audio':
                audio_b64 = data.get('audio_base_64') or data.get('audio')
                if not audio_b64:
                    continue

                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    audio_chunk = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    audio_buffer.extend(audio_chunk)
                except Exception as e:
                    continue

                buffer_duration = len(audio_buffer) / sample_rate

                if buffer_duration >= 3.0:
                    audio_np = np.array(audio_buffer, dtype=np.float32)
                    start_time = time.time()

                    try:
                        segments, info = model.transcribe(
                            audio_np,
                            language=config['language'] if config['language'] != 'auto' else None,
                            vad_filter=config.get('vad_filter', True)
                        )

                        full_text = ""
                        for segment in segments:
                            full_text += segment.text

                        latency = (time.time() - start_time) * 1000

                        if full_text.strip():
                            ws.send(json.dumps({
                                'type': 'committed_transcript',
                                'text': full_text.strip(),
                                'language_code': info.language if hasattr(info, 'language') else config['language'],
                                'latency_ms': round(latency)
                            }))
                            print(f"📝 [{round(latency)}ms] {full_text.strip()}")

                    except Exception as e:
                        ws.send(json.dumps({'type': 'error', 'error': str(e)}))

                    audio_buffer = []

    except Exception as e:
        print(f"WebSocket error: {e}")

    print("🔌 Disconnected")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''

    app_path.write_text(app_content)
    print("✅ app.py oluşturuldu!")
    return True


def create_templates():
    """templates/index.html oluştur"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    index_path = templates_dir / "index.html"

    if index_path.exists():
        print("✅ templates/index.html mevcut")
        return True

    print("📝 templates/index.html oluşturuluyor...")

    # Mevcut index.html'i kopyala (basitleştirilmiş versiyon)
    html_content = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whisper Realtime STT</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .controls {
            margin: 20px 0;
            text-align: center;
        }
        button {
            padding: 15px 30px;
            margin: 5px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .start {
            background: #28a745;
            color: white;
        }
        .stop {
            background: #dc3545;
            color: white;
        }
        .transcript {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 5px;
            min-height: 100px;
        }
        .status {
            text-align: center;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .connected {
            background: #d4edda;
            color: #155724;
        }
        .disconnected {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Whisper Realtime STT</h1>

        <div id="status" class="status disconnected">Bağlantı Yok</div>

        <div class="controls">
            <button id="startBtn" class="start" onclick="start()">Başlat</button>
            <button id="stopBtn" class="stop" onclick="stop()" disabled>Durdur</button>
        </div>

        <div class="transcript">
            <h3>Transkript:</h3>
            <div id="output">Konuşmaya başlayın...</div>
        </div>
    </div>

    <script>
        let ws = null;
        let audioContext = null;
        let mediaStream = null;
        let processor = null;

        async function start() {
            try {
                // WebSocket bağlantısı
                const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${location.host}/ws`);

                ws.onopen = () => {
                    document.getElementById('status').textContent = 'Bağlı ✓';
                    document.getElementById('status').className = 'status connected';
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'committed_transcript') {
                        const output = document.getElementById('output');
                        output.innerHTML += '<p><strong>' + data.text + '</strong></p>';
                    }
                };

                // Mikrofon erişimi
                mediaStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        channelCount: 1,
                        sampleRate: 16000
                    }
                });

                audioContext = new AudioContext({sampleRate: 16000});
                const source = audioContext.createMediaStreamSource(mediaStream);
                processor = audioContext.createScriptProcessor(4096, 1, 1);

                processor.onaudioprocess = (e) => {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        const inputData = e.inputBuffer.getChannelData(0);
                        const pcm16 = new Int16Array(inputData.length);
                        for (let i = 0; i < inputData.length; i++) {
                            const s = Math.max(-1, Math.min(1, inputData[i]));
                            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                        }

                        const base64 = btoa(String.fromCharCode(...new Uint8Array(pcm16.buffer)));
                        ws.send(JSON.stringify({
                            type: 'audio',
                            audio_base_64: base64
                        }));
                    }
                };

                source.connect(processor);
                processor.connect(audioContext.destination);

                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;

            } catch (error) {
                alert('Hata: ' + error.message);
            }
        }

        function stop() {
            if (processor) processor.disconnect();
            if (audioContext) audioContext.close();
            if (mediaStream) mediaStream.getTracks().forEach(t => t.stop());
            if (ws) ws.close();

            document.getElementById('status').textContent = 'Bağlantı Yok';
            document.getElementById('status').className = 'status disconnected';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
    </script>
</body>
</html>'''

    index_path.write_text(html_content)
    print("✅ templates/index.html oluşturuldu!")
    return True


def start_flask_server(port=5000):
    """Flask sunucusunu başlat ve hazır olana kadar bekle"""
    print(f"🚀 Flask sunucusu başlatılıyor (port {port})...")

    # Ortam değişkenlerini ayarla
    os.environ['DEVICE_TYPE'] = 'cuda'
    os.environ['WHISPER_MODEL'] = 'small'

    # Flask'ı başlat
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Sunucunun gerçekten hazır olmasını bekle
    import socket
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            # Port'un açık olup olmadığını kontrol et
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                # Port açık, Flask hazır
                print("✅ Flask sunucusu çalışıyor!")
                return flask_process

            time.sleep(1)
        except:
            time.sleep(1)

    print("⚠️  Flask başladı ama health check başarısız (timeout)")
    return flask_process


def get_public_url_alternative(port=5000):
    """
    Alternatif yöntem: Cloudflare URL'sini manuel göster
    Eğer otomatik yakalama başarısız olursa kullanıcıya yardımcı ol
    """
    print("\n" + "="*70)
    print("📋 MANUEL URL KONTROLÜ")
    print("="*70)
    print("\nEğer yukarıda URL görünmediyse:")
    print("1. Aşağıdaki komutu çalıştırın:")
    print("   !curl http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^\"]*trycloudflare.com'")
    print("\n2. Veya cloudflared loglarına bakın:")
    print("   Process loglarında 'trycloudflare.com' arayın")
    print("="*70 + "\n")


def main(debug=False):
    """Ana kurulum fonksiyonu"""

    if not is_colab():
        print("⚠️  Bu script Google Colab için tasarlanmıştır.")
        print("   Yerel kullanım için 'python app.py' komutunu kullanın.")
        return

    print("\n" + "="*70)
    print("  🎤 Whisper Realtime STT - Google Colab Kurulumu")
    print("="*70 + "\n")

    # 1. Paketleri kur
    install_requirements()

    # 2. Dosyaları oluştur
    create_app_file()
    create_templates()

    # 3. Flask sunucusunu başlat
    port = 5000
    start_flask_server(port)

    # 4. Ngrok Tunnel başlat
    tunnel_result = start_ngrok_tunnel(port)

    if tunnel_result:
        print("\n✅ Kurulum tamamlandı!")
        print("   Uygulamanız çalışıyor. Yukarıdaki linke tıklayın.")
        print("   Durdurmak için: Runtime -> Interrupt execution\n")

        # Alternatif URL alma yöntemi göster
        time.sleep(2)
        get_public_url_alternative(port)

        # Tunnel'ı çalışır durumda tut
        try:
            # pycloudflared objesi mi yoksa subprocess mi kontrol et
            if hasattr(tunnel_result, 'wait'):
                # subprocess.Popen objesi
                tunnel_result.wait()
            else:
                # pycloudflared Urls objesi - sonsuz bekle
                print("🔄 Tunnel aktif, session açık tutmak için bekliyor...")
                while True:
                    time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 Uygulama durduruldu.")
    else:
        print("❌ Tunnel başlatılamadı.")


def quick_start_gpu():
    """Hızlı başlatma - GPU modu"""
    print("\n🚀 Hızlı Başlatma - GPU Modu\n")
    main()


def quick_start_cpu():
    """Hızlı başlatma - CPU modu"""
    print("\n🚀 Hızlı Başlatma - CPU Modu\n")
    os.environ['DEVICE_TYPE'] = 'cpu'
    main()


if __name__ == "__main__":
    quick_start_gpu()
