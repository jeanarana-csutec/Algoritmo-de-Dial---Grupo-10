import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

cases = [
    ('un_vertece', '1 0 0 0\n', [0]),
    ('cero_y_aislado', '2 1 0 0\n0 0 0\n', [0, -1]),
    ('ciclo_de_ceros', '3 3 0 0\n0 1 0\n1 2 0\n2 0 0\n', [0, 0, 0]),
    ('mejora_con_peso_maximo', '3 3 0 5\n0 1 2\n1 2 2\n0 2 5\n', [0, 2, 4]),
    ('aristas_duplicadas', '3 3 0 4\n0 1 4\n0 1 1\n1 2 4\n', [0, 1, 5]),
]
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    exe = tmp / 'dial'
    subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra',str(ROOT/'cpp/dial.cpp'),'-o',str(exe)], check=True)
    for name, graph_text, expected in cases:
        inp, out = tmp / 'input.txt', tmp / 'trace.jsonl'
        inp.write_text(graph_text, encoding='utf-8')
        subprocess.run([str(exe),str(inp),str(out)],check=True,stdout=subprocess.DEVNULL)
        actual=json.loads(out.read_text(encoding='utf-8').splitlines()[-1])['dist']
        assert actual == expected, (name,actual,expected)
    for graph_text in ['2 1 0 1\n0 1 -1\n', '2 1 0 1\n0 1 2\n','2 1 0 1\n0 2 1\n']:
        inp = tmp / 'invalid.txt'
        inp.write_text(graph_text,encoding='utf-8')
        assert subprocess.run([str(exe),str(inp),str(tmp/'bad.jsonl')],capture_output=True).returncode != 0
print('OK: 5 casos borde correctos y 3 entradas invalidas rechazadas.')
