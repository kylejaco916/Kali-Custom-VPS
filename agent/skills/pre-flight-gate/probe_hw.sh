#!/data/data/com.termux/files/usr/bin/bash
echo "=== [GATE A: DETERMINISTIC HARDWARE & ENV FINGERPRINT] ==="
echo "ARCH: $(uname -m) | KERNEL: $(uname -r)"
echo "PYTHON: $(python3 --version 2>&1) | UV: $(uv --version 2>/dev/null || echo 'not-installed')"
free -h 2>/dev/null || true
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader
fi
