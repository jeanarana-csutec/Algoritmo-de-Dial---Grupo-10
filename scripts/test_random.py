"""Contrasta C++ Dial contra Dijkstra, casos con 0 y no alcanzables."""
import heapq,random,subprocess,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
random.seed(20261121)
with tempfile.TemporaryDirectory() as tmp:
    work=Path(tmp)
    exe=work/'dial'
    subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra',str(ROOT/'cpp/dial.cpp'),'-o',str(exe)],check=True)
    for case in range(75):
        n=random.randint(2,25); C=random.randint(0,8); ori=random.randrange(n)
        edges=[]; adj=[[] for _ in range(n)]
        for a in range(n):
            for b in range(n):
                if a!=b and random.random()<.15:
                    w=random.randint(0,C)
                    edges.append((a,b,w));adj[a].append((b,w))
        graph=work/'graph.txt'; trace=work/'trace.jsonl'
        graph.write_text(f'{n} {len(edges)} {ori} {C}\n'+'\n'.join(f'{a} {b} {w}' for a,b,w in edges))
        subprocess.run([str(exe),str(graph),str(trace)],check=True,stdout=subprocess.DEVNULL)
        got=json.loads(trace.read_text().splitlines()[-1])['dist']
        dist=[float('inf')]*n;dist[ori]=0;h=[(0,ori)]
        while h:
            d,u=heapq.heappop(h)
            if d!=dist[u]:continue
            for v,w in adj[u]:
                if d+w<dist[v]:
                    dist[v]=d+w;heapq.heappush(h,(dist[v],v))
        expected=[-1 if d==float('inf') else d for d in dist]
        assert got==expected,(case,n,C,got,expected)
print('OK: 75 grafos aleatorios, resultados C++ Dial idénticos a Dijkstra.')
