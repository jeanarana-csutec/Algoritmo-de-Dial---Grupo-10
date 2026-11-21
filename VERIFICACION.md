# Verificación del código — Proyecto Final 2 (Dial)

Revisión: 21 de noviembre de 2026.

## Comprobado

- Compilación: `g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Wconversion cpp/dial.cpp` sin advertencias.
- La implementación calcula las distancias con buckets circulares de `C + 1` posiciones, usando las operaciones del código C++ y no funciones de caminos mínimos prehechas.
- Pruebas automatizadas: 75 grafos aleatorios, todas las distancias coinciden con el algoritmo de referencia de Dijkstra.
- Casos borde adicionales: fuente única, peso cero, ciclo de pesos cero, rutas mejoradas, aristas duplicadas y entradas inválidas.
- Caso ilustrativo: resultados `A=0, B=2, C=1, D=3, E=1, F=5, G=∞`.
- Reproducibilidad: la traza JSONL regenerada coincide byte por byte con `data/traza_principal.jsonl` (20 eventos).
- Conexión: la escena Python lee `data/traza_principal.jsonl`; no resuelve rutas en Python.
- Archivo Manim: sintaxis validada con `python -m py_compile`.
- Dependencias: ninguna implementación externa de Dial utilizada. `heapq` se usa solo en pruebas para la referencia de Dijkstra.

## Pendiente de comprobar para la entrega definitiva

- El render de **Manim Community** no pudo ejecutarse en el entorno de verificación (paquete no instalado y dependencias del sistema ausentes). La sintaxis comprobada **no garantiza** que el render se ejecute sin problemas visuales o de API.
- El video MP4 final, la calidad visual, las voces y las capturas obtenidas del render definitivo requieren verificación después de instalar Manim.
- Los enlaces verdaderos de GitHub y del video deben agregarse al informe PDF antes de la entrega.
- Comprobar que los nombres y contribuciones descritas en el informe correspondan a lo realizado por el grupo.

## Cómo verificar el render (con Manim instalado)

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
bash scripts/build_video.sh                # Linux/macOS
# o .\scripts\build_video.ps1            # Windows PowerShell
```

Comprobar que el MP4 renderizado no exceda los cinco minutos y muestre correctamente todas las escenas (problema, concepto, buckets, simulación, caso borde, complejidad y créditos).
