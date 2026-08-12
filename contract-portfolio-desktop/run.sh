#!/usr/bin/env bash
# Uygulamayı kaynak koddan çalıştırır (Linux/macOS geliştirme).
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
else
  . .venv/bin/activate
fi

# pywebview için GUI arka ucu yoksa Flask'a düşmek için:
#   SPP_FORCE_FLASK=1 ./run.sh
python app/main.py
