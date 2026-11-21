# Proyecto Final 2 — Algoritmo de Dial

**CS2023 — Algoritmos y Estructuras de Datos · UTEC · 2026-2**

Integrantes: Santiago Cesar Morales Portella, Jean Piere Milan Arana Chiong y Omar Alonso Guzmán Harvey.

El programa implementa el algoritmo de Dial en **C++17** para encontrar los caminos mínimos desde un origen en un grafo dirigido con pesos enteros entre `0` y `C`. Cada operación se guarda en una traza JSONL. Una escena de **Manim** lee esa traza y representa el algoritmo; Python no calcula los caminos mínimos.

## Qué contiene

- `cpp/dial.cpp`: implementación propia de Dial y escritura de la traza.
- `data/grafo_principal.txt`: grafo de 7 vértices y 9 aristas; incluye peso cero y un vértice inalcanzable.
- `data/traza_principal.jsonl`: 20 estados generados por el programa en C++.
- `manim/dial_cinematico.py`: escena animada (`DialFilm`) que consume los estados.
- `scripts/`: comandos de compilación, generación del video y verificación.
- `docs/01_storyboard.md` y `docs/02_guion_voz.md`: estructura visual y guion propuesto.
- `docs/capturas_video/`: capturas **reales de la previsualización V3**; no representan un render verificado de Manim.
- `informe/`: versión editable y PDF del informe, pendientes de enlaces definitivos.

## Requisitos

- Compilador de C++17 (`g++`).
- Python 3 y Manim Community Edition. Instrucciones de instalación: https://docs.manim.community/en/stable/installation.html
- FFmpeg para exportar el video.

Para instalar dependencias de Python (idealmente en entorno virtual):

```bash
python -m pip install -r requirements.txt
```

## Ejecutar

Desde la raíz del repositorio:

**Linux o macOS**

```bash
bash scripts/build_video.sh
```

**Windows (PowerShell, con g++ y manim configurados)**

```powershell
.\scripts\build_video.ps1
```

**Manualmente**

```bash
g++ -std=c++17 -O2 -Wall -Wextra cpp/dial.cpp -o dial
./dial data/grafo_principal.txt data/traza_principal.jsonl
python scripts/verificar_traza.py
python scripts/test_random.py
manim -qh --fps 30 manim/dial_cinematico.py DialFilm
```

El video se genera bajo `media/videos/dial_cinematico/` (la ruta exacta puede variar según configuración de Manim). La narración se agrega después en un editor de video.

## Ejemplo y validación

El grafo de ejemplo da distancias desde `A`:

| Vértice | A | B | C | D | E | F | G |
|---|---:|---:|---:|---:|---:|---:|---:|
| Distancia | 0 | 2 | 1 | 3 | 1 | 5 | ∞ |

`test_random.py` compara Dial con Dijkstra en **75 casos aleatorios**; `test_edge_cases.py` comprueba casos límite y entradas inválidas. `verificar_traza.py` comprueba los estados del ejemplo. Ambas pruebas pasaron durante la preparación de este repositorio.

## Validación del algoritmo y uso de librerías

La implementación de Dial está escrita desde cero en `cpp/dial.cpp`. Usa `vector`, `fstream`, `string` y otras herramientas de C++ para almacenar datos y generar la traza; **no usa Dijkstra, heap, una cola de prioridad ni una implementación de Dial de terceros**.

`scripts/test_random.py` **sí usa `heapq` exclusivamente para construir una referencia de Dijkstra en las pruebas**. No participa en la implementación ni en las animaciones. Por eso, no se está delegando el algoritmo asignado a una librería.

Para comprobar el código sin instalar Manim:

```bash
python scripts/test_random.py
python scripts/test_edge_cases.py
python scripts/verificar_traza.py
python -m py_compile manim/dial_cinematico.py
```

El resultado de la revisión técnica realizada se resume en `VERIFICACION.md`.

## Estado de la animación

La escena de Manim y el guion están preparados. **El render final de Manim no se ha verificado en este entorno.** Las capturas incluidas provienen de la previsualización V3, creada con otra herramienta para comprobar el orden visual. No debe presentarse esa previsualización como el MP4 final exigido por el profesor. Antes de la entrega deben renderizar la escena con Manim, revisar el video, incorporar el audio y reemplazar las capturas del informe por las definitivas.

## Referencias

- Dial, R. B. (1969). *Algorithm 360: Shortest-path forest with topological ordering*. Communications of the ACM, 12(11), 632–633.
- Manim Community: https://docs.manim.community/en/stable/
- 3Blue1Brown: https://www.3blue1brown.com/ (referencia de estilo).
