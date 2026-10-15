#!/usr/bin/env bash
# Instala lo necesario para generar los reels (voz offline, render y fuentes ya incluidas).
set -e
cd "$(dirname "$0")"
python3 -m pip install --break-system-packages -q kokoro-onnx soundfile numpy 2>/dev/null || python3 -m pip install -q kokoro-onnx soundfile numpy
python3 -c "import playwright" 2>/dev/null || python3 -m pip install --break-system-packages -q playwright
command -v ffmpeg >/dev/null || { echo "Falta ffmpeg"; exit 1; }
python3 - <<'EOF'
import sys; sys.path.insert(0, "engine")
from build import ensure_model
ensure_model()
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    p.chromium.launch().close()
print("[setup] listo: voz, navegador y ffmpeg disponibles")
EOF
