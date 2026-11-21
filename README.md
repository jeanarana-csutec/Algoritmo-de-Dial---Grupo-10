## Ejecución del proyecto

Para ejecutar el proyecto se necesita tener instalado **C++17 (g++), Python 3, Manim Community y FFmpeg**.

Primero, desde la carpeta principal del repositorio, instalamos las dependencias de Python:

`python -m pip install -r requirements.txt`

Luego, en Windows, abrimos PowerShell y ejecutamos:

`.\scripts\build_video.ps1`

Este script compila nuestra implementación de Dial en C++, ejecuta el algoritmo sobre el grafo de ejemplo y genera un archivo con los estados de ejecución. Después, Manim utiliza esos datos para construir la animación.

El video generado se guarda en la carpeta `media/videos/dial_cinematico/`.

Para comprobar el funcionamiento del algoritmo también podemos ejecutar:

`python scripts/test_random.py`

`python scripts/test_edge_cases.py`

Estas pruebas verifican los caminos mínimos calculados y el comportamiento del algoritmo en distintos casos.
