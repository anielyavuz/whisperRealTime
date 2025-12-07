"""
Faster-Whisper Realtime STT - Ücretsiz Alternatif
Google Colab'da GPU ile çalıştırılabilir

Latency: ~1-2 saniye (GPU ile)
Türkçe Kalitesi: Mükemmel (Whisper large-v3)
Maliyet: ÜCRETSİZ

Model Boyutları ve Performans:
- tiny: ~75MB, en hızlı, düşük doğruluk
- base: ~150MB, hızlı, orta doğruluk
- small: ~500MB, dengeli, iyi doğruluk (Önerilen)
- medium: ~1.5GB, yavaş, yüksek doğruluk
- large-v3: ~3GB, en yavaş, en yüksek doğruluk
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

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system environment variables

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Global models (lazy loading)
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
                    print(f"⚠️  VAD model yüklenemedi: {e}")
                    print("   VAD olmadan devam edilecek")
                    return None
    return vad_model

def get_model():
    """Lazy load Whisper model"""
    global whisper_model
    if whisper_model is None:
        with model_lock:
            if whisper_model is None:
                try:
                    from faster_whisper import WhisperModel
                except ImportError:
                    print("❌ faster-whisper yüklü değil!")
                    print("   Yüklemek için: pip install faster-whisper")
                    raise

                # Colab'dan gelen DEVICE_TYPE'ı veya yerel için USE_GPU'yu kullan
                # Varsayılan olarak 'cuda' denenir, bulunamazsa 'cpu'ya düşer
                device = os.environ.get("DEVICE_TYPE", "cuda")

                # GPU kontrolü
                try:
                    import torch
                    if device == "cuda" and not torch.cuda.is_available():
                        print("⚠️  CUDA seçildi ancak kullanılamıyor, CPU'ya geçiliyor...")
                        device = "cpu"
                    elif device == "cuda":
                         print(f"✅ GPU bulundu: {torch.cuda.get_device_name(0)}")
                except ImportError:
                    print("⚠️  PyTorch yüklü değil, CPU kullanılacak.")
                    device = "cpu"

                compute_type = "float16" if device == "cuda" else "int8"

                model_size = os.environ.get("WHISPER_MODEL", "small")
                print(f"🔄 Loading Whisper model: {model_size} on {device} ({compute_type})...")

                try:
                    whisper_model = WhisperModel(
                        model_size,
                        device=device,
                        compute_type=compute_type
                    )
                    print(f"✅ Model loaded: {model_size}")
                except Exception as e:
                    print(f"❌ Model yükleme hatası: {e}")
                    print("   Daha küçük bir model deneyin (tiny, base, small)")
                    raise

    return whisper_model

@app.route('/')
def index():
    """Ana sayfa - Web arayüzü"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
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
        'gpu': os.environ.get("USE_GPU", "1") == "1",
        'gpu_available': gpu_available,
        'gpu_name': gpu_name,
        'model_loaded': whisper_model is not None
    })

@app.route('/config')
def config():
    """Model konfigürasyon bilgisi"""
    return jsonify({
        'models': [
            {'value': 'tiny', 'name': 'Tiny (~75MB)', 'speed': 'fastest', 'quality': 'low'},
            {'value': 'base', 'name': 'Base (~150MB)', 'speed': 'fast', 'quality': 'medium'},
            {'value': 'small', 'name': 'Small (~500MB)', 'speed': 'balanced', 'quality': 'good', 'recommended': True},
            {'value': 'medium', 'name': 'Medium (~1.5GB)', 'speed': 'slow', 'quality': 'high'},
            {'value': 'large-v3', 'name': 'Large-v3 (~3GB)', 'speed': 'slowest', 'quality': 'highest'}
        ],
        'languages': [
            {'code': 'auto', 'name': 'Auto-detect'},
            {'code': 'tr', 'name': 'Türkçe'},
            {'code': 'en', 'name': 'English'},
            {'code': 'de', 'name': 'Deutsch'},
            {'code': 'fr', 'name': 'Français'},
            {'code': 'es', 'name': 'Español'},
            {'code': 'pt', 'name': 'Português'},
            {'code': 'it', 'name': 'Italiano'},
            {'code': 'ar', 'name': 'العربية'},
            {'code': 'zh', 'name': '中文'},
            {'code': 'ja', 'name': '日本語'}
        ],
        'default_config': {
            'chunk_length_s': 3,
            'vad_filter': True,
            'sample_rate': 16000
        }
    })

@sock.route('/ws')
def websocket(ws):
    """WebSocket endpoint for realtime transcription"""
    print("🔌 New WebSocket connection")

    # Get models
    try:
        model = get_model()
        vad = get_vad_model()
    except Exception as e:
        ws.send(json.dumps({
            'type': 'error',
            'error': f'Model yüklenemedi: {str(e)}'
        }))
        return

    # Audio buffer
    audio_buffer = []
    sample_rate = 16000

    # VAD state tracking
    is_speaking = False
    silence_duration = 0
    speech_duration = 0
    vad_window_size = int(sample_rate * 0.032)  # 32ms window for VAD (512 samples at 16kHz)

    # Config from client
    config = {
        'language': 'tr',  # Default Turkish
        'silence_threshold': 0.5,  # Silence duration in seconds to trigger processing
        'min_speech_duration': 0.5,  # Minimum speech duration to process
        'vad_threshold': 0.5  # VAD confidence threshold (0-1)
    }

    # Send ready message
    ws.send(json.dumps({
        'type': 'session_started',
        'message_type': 'session_started',
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

            msg_type = data.get('type', data.get('message_type', ''))

            # Config update
            if msg_type == 'config':
                config.update(data.get('config', {}))
                print(f"📝 Config updated: {config}")
                ws.send(json.dumps({
                    'type': 'config_updated',
                    'config': config
                }))
                continue

            # Audio chunk
            if msg_type == 'audio' or msg_type == 'input_audio_chunk':
                audio_b64 = data.get('audio_base_64') or data.get('audio')
                if not audio_b64:
                    continue

                # Decode base64 to PCM
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    # Convert bytes to numpy array (16-bit PCM)
                    audio_chunk = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    audio_buffer.extend(audio_chunk)
                except Exception as e:
                    print(f"Audio decode error: {e}")
                    continue

                # VAD-based speech detection
                buffer_duration = len(audio_buffer) / sample_rate
                should_process = False

                if vad is not None and len(audio_buffer) >= vad_window_size:
                    # Run VAD on recent audio
                    recent_audio = np.array(audio_buffer[-vad_window_size:], dtype=np.float32)

                    try:
                        import torch
                        audio_tensor = torch.from_numpy(recent_audio).unsqueeze(0)
                        speech_prob = vad(audio_tensor, sample_rate).item()

                        # Update state based on VAD
                        if speech_prob > config['vad_threshold']:
                            # Speech detected
                            if not is_speaking:
                                is_speaking = True
                                silence_duration = 0
                                ws.send(json.dumps({
                                    'type': 'speech_started',
                                    'message_type': 'speech_started'
                                }))
                            speech_duration += len(recent_audio) / sample_rate
                        else:
                            # Silence detected
                            if is_speaking:
                                silence_duration += len(recent_audio) / sample_rate

                                # Check if silence is long enough to process
                                if silence_duration >= config['silence_threshold']:
                                    if speech_duration >= config['min_speech_duration']:
                                        should_process = True
                                    is_speaking = False
                                    speech_duration = 0
                                    silence_duration = 0

                                    ws.send(json.dumps({
                                        'type': 'speech_ended',
                                        'message_type': 'speech_ended',
                                        'speech_duration': round(speech_duration, 2)
                                    }))

                        # Send VAD status update
                        ws.send(json.dumps({
                            'type': 'vad_status',
                            'message_type': 'vad_status',
                            'is_speaking': is_speaking,
                            'speech_prob': round(speech_prob, 2),
                            'buffer_duration': round(buffer_duration, 2)
                        }))

                    except Exception as e:
                        print(f"VAD error: {e}")
                        # Fallback to time-based processing
                        should_process = buffer_duration >= 3.0
                else:
                    # No VAD - fallback to time-based
                    should_process = buffer_duration >= 3.0 or data.get('commit', False)

                if should_process and len(audio_buffer) > sample_rate * 0.3:  # At least 0.3s
                    # Convert to numpy array
                    audio_np = np.array(audio_buffer, dtype=np.float32)

                    # Transcribe
                    start_time = time.time()

                    try:
                        segments, info = model.transcribe(
                            audio_np,
                            language=config['language'] if config['language'] != 'auto' else None,
                            vad_filter=config['vad_filter'],
                            vad_parameters={
                                "min_silence_duration_ms": 500,
                                "speech_pad_ms": 200
                            }
                        )

                        # Collect all text
                        full_text = ""
                        words = []
                        for segment in segments:
                            full_text += segment.text
                            if hasattr(segment, 'words') and segment.words:
                                for word in segment.words:
                                    words.append({
                                        'text': word.word,
                                        'start': word.start,
                                        'end': word.end,
                                        'probability': word.probability
                                    })

                        latency = (time.time() - start_time) * 1000

                        if full_text.strip():
                            # Send committed transcript
                            ws.send(json.dumps({
                                'type': 'committed_transcript',
                                'message_type': 'committed_transcript',
                                'text': full_text.strip(),
                                'language_code': info.language if hasattr(info, 'language') else config['language'],
                                'latency_ms': round(latency),
                                'words': words if words else None,
                                'buffer_duration': round(buffer_duration, 2)
                            }))
                            print(f"📝 [{round(latency)}ms] {full_text.strip()}")
                        else:
                            # Empty result
                            ws.send(json.dumps({
                                'type': 'partial_transcript',
                                'message_type': 'partial_transcript',
                                'text': ''
                            }))

                    except Exception as e:
                        print(f"Transcription error: {e}")
                        ws.send(json.dumps({
                            'type': 'error',
                            'error': str(e)
                        }))

                    # Clear buffer
                    audio_buffer = []

                # Send partial update (buffer status)
                elif len(audio_buffer) > sample_rate * 0.3 and not is_speaking:
                    ws.send(json.dumps({
                        'type': 'partial_transcript',
                        'message_type': 'partial_transcript',
                        'text': f"[{buffer_duration:.1f}s audio buffered...]",
                        'buffer_duration': buffer_duration
                    }))

            # Manual commit
            elif msg_type == 'commit':
                if len(audio_buffer) > sample_rate * 0.3:
                    # Force process - will be handled on next iteration
                    pass

    except Exception as e:
        print(f"WebSocket error: {e}")

    print("🔌 WebSocket disconnected")
