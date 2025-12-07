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


def start_cloudflare_tunnel(port, debug=False):
    """Cloudflare Tunnel başlat ve public URL al"""
    print(f"🌐 Cloudflare Tunnel başlatılıyor (port {port})...")

    try:
        # Tunnel'ı başlat
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # URL'yi yakala
        import re
        import threading

        public_url = None
        url_found = threading.Event()

        def read_output(stream, stream_name):
            """stdout ve stderr'ı ayrı thread'lerde oku"""
            nonlocal public_url

            for line in stream:
                line = line.strip()

                # Debug modu
                if debug and line:
                    print(f"[{stream_name}] {line}")

                # URL'yi ara
                if "trycloudflare.com" in line and not public_url:
                    # Regex ile URL'yi yakala
                    url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)

                    if url_match:
                        public_url = url_match.group(0)
                        url_found.set()
                        break
                    else:
                        # Fallback parsing
                        parts = line.split()
                        for part in parts:
                            if "trycloudflare.com" in part:
                                # Temizle (pipe, quotes, noktalama vb.)
                                cleaned = re.sub(r'[^\w\-\.:/]', '', part)
                                if cleaned.startswith("http"):
                                    public_url = cleaned
                                elif "trycloudflare.com" in cleaned:
                                    public_url = "https://" + cleaned

                                if public_url:
                                    url_found.set()
                                    break
                        if public_url:
                            break

        # Her iki stream'i ayrı thread'lerde oku
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "STDOUT"))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "STDERR"))

        stdout_thread.daemon = True
        stderr_thread.daemon = True

        stdout_thread.start()
        stderr_thread.start()

        # URL'yi bekle (max 30 saniye)
        print("🔍 Public URL bekleniyor...")
        url_found.wait(timeout=30)

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
            print("   Lütfen aşağıdaki komutu çalıştırarak manuel kontrol edin:\n")
            print("   !ps aux | grep cloudflared")
            print("   !cloudflared tunnel info\n")

        # Process'i çalışır durumda tut
        return process

    except Exception as e:
        print(f"❌ Cloudflare Tunnel başlatılamadı: {e}")
        import traceback
        if debug:
            traceback.print_exc()
        return None


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
    """Flask sunucusunu başlat"""
    print(f"🚀 Flask sunucusu başlatılıyor (port {port})...")

    # Ortam değişkenlerini ayarla
    os.environ['DEVICE_TYPE'] = 'cuda'
    os.environ['WHISPER_MODEL'] = 'small'

    # Flask'ı başlat
    subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Sunucunun başlaması için bekle
    time.sleep(5)
    print("✅ Flask sunucusu çalışıyor!")


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

    # 3. Cloudflared kur
    if not install_cloudflared():
        print("❌ Cloudflare Tunnel kurulamadı, devam edilemiyor.")
        return

    # 4. Flask sunucusunu başlat
    port = 5000
    start_flask_server(port)

    # 5. Cloudflare Tunnel başlat
    tunnel_process = start_cloudflare_tunnel(port)

    if tunnel_process:
        print("\n✅ Kurulum tamamlandı!")
        print("   Uygulamanız çalışıyor. Yukarıdaki linke tıklayın.")
        print("   Durdurmak için: Runtime -> Interrupt execution\n")

        # Alternatif URL alma yöntemi göster
        time.sleep(2)
        get_public_url_alternative(port)

        # Process'i çalışır durumda tut
        try:
            tunnel_process.wait()
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
