# Real-Time Speech-to-Sign for VR Avatars

A Python 3.10 project that captures live speech, converts it to text, maps words to sign tokens, and optionally streams the token sequence to a VR system (Unity/OpenXR bridge).

> **Target hardware:** Raspberry Pi 4  
> **Python version:** **3.10** (kept fixed as requested)

## 🚀 Features

- Real-time microphone speech capture
- **Online STT:** Google Speech Recognition
- **Offline STT:** Vosk local model support (no internet required)
- Text tokenization using NLTK with lightweight regex fallback
- Word-to-sign dictionary mapping
- Optional VR output over:
  - HTTP POST API
  - TCP socket stream
- Queue-based continuous streaming with separate capture/process loops
- Logging + error recovery (mic reconnect, network retries)

## 🧱 Architecture

1. **Speech Input** via microphone (`pyaudio` + `speech_recognition`)
2. **STT Engine** via Google (online) or Vosk (offline)
3. **Text Processing** via tokenizer
4. **Sign Mapping** via JSON dictionary
5. **VR Dispatch** via HTTP or sockets (optional)

## 📁 Project Structure

```text
.
├── app.py
├── requirements.txt
├── signs.json
├── tests/
├── unity_samples/
├── datasets/
└── speech_to_sign/
    ├── __init__.py
    ├── config.py
    ├── pipeline.py
    ├── sign_mapper.py
    ├── stt.py
    └── vr_client.py
```

## 🛠️ Installation (Raspberry Pi 4)

### 1) System packages

```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv portaudio19-dev
```

### 2) Virtual environment

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) (Optional) NLTK tokenizer data

```bash
python -m nltk.downloader punkt
```

> If `punkt` is unavailable, the app automatically falls back to regex tokenization.

### 4) Offline STT model (optional)

Download a Vosk model and keep it in a local directory, for example:

```text
models/vosk/vosk-model-small-en-us-0.15
```

## ▶️ Run

### A) Online STT (Google)

```bash
python app.py --mapping-file signs.json --stt-backend google
```

### B) Offline STT (Vosk)

```bash
python app.py \
  --mapping-file signs.json \
  --stt-backend vosk \
  --vosk-model-path models/vosk/vosk-model-small-en-us-0.15
```

### C) Send sign tokens to VR HTTP bridge

```bash
python app.py \
  --mapping-file signs.json \
  --send-to-vr \
  --vr-endpoint http://127.0.0.1:5000/sign-sequence
```

### D) Send sign tokens over TCP socket

```bash
python app.py \
  --mapping-file signs.json \
  --send-to-vr \
  --vr-socket-enabled \
  --vr-socket-host 127.0.0.1 \
  --vr-socket-port 8765
```

## 🔌 VR Payload Format

Both HTTP and socket integrations send the same JSON shape:

```json
{
  "transcript": "hello how are you",
  "signs": ["SIGN_HELLO", "SIGN_HOW", "SIGN_ARE", "SIGN_YOU"]
}
```

## 🎮 Unity sample receiver

A sample Unity C# script is provided:

- `unity_samples/SignPayloadReceiver.cs`

It can receive sign payloads from either HTTP (`/sign-sequence/`) or TCP socket and prints parsed tokens for mapping to avatar animations.

## 🧪 Tests

Run unit tests:

```bash
python3.10 -m unittest discover -s tests -p "test_*.py" -v
```

Covers:
- tokenizer/mapping behavior
- VR client HTTP retry behavior
- STT backend selection logic

## 🧩 Extend the Dictionary

Edit `signs.json` and add lower-case word keys:

```json
{
  "welcome": "SIGN_WELCOME"
}
```

Unknown words are mapped to `"UNK"`.

## 📚 Dataset support for training

See:

- `datasets/README.md`

It includes a recommended folder structure for:
- **static sign datasets** (image-based)
- **dynamic sign datasets** (GIF/video-based)
- train/val/test splits
- metadata format suggestions

## 🎯 Accessibility Use Case

This system helps bridge communication between spoken-language users and sign-language users in immersive VR environments.
