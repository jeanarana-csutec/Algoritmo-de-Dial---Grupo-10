#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v g++ >/dev/null || { echo 'Falta g++'; exit 1; }
command -v manim >/dev/null || { echo 'Falta Manim. Ver README.md'; exit 1; }
g++ -std=c++17 -O2 -Wall -Wextra cpp/dial.cpp -o dial
./dial data/grafo_principal.txt data/traza_principal.jsonl
python scripts/verificar_traza.py
manim -qh --fps 30 manim/dial_cinematico.py DialFilm
