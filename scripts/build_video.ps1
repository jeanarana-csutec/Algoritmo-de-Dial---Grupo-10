$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (-not (Get-Command g++ -ErrorAction SilentlyContinue)) { throw "Falta g++. Instala MinGW-w64 o MSYS2." }
if (-not (Get-Command manim -ErrorAction SilentlyContinue)) { throw "Falta Manim Community. Revisa README.md." }
g++ -std=c++17 -O2 -Wall -Wextra cpp/dial.cpp -o dial.exe
if ($LASTEXITCODE -ne 0) { throw "Error al compilar C++." }
./dial.exe data/grafo_principal.txt data/traza_principal.jsonl
if ($LASTEXITCODE -ne 0) { throw "Error al ejecutar Dial." }
python scripts/verificar_traza.py
if ($LASTEXITCODE -ne 0) { throw "Traza inválida." }
manim -qh --fps 30 manim/dial_cinematico.py DialFilm
if ($LASTEXITCODE -ne 0) { throw "Fallo render Manim." }
