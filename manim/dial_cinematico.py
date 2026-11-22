"""
DIAL, UN GRAFO QUE COBRA VIDA  |  Manim Community Edition 0.19–0.22

La animacion no calcula caminos minimos: LEE la traza JSONL que genera
nuestra implementacion real en C++17. Cada relajacion, extraccion, entrada
obsoleta y distancia final viene de C++, no de una coreografia manual.

Comando:  manim -qh --fps 30 manim/dial_cinematico.py DialFilm
           (Ejecutar desde la carpeta raiz del proyecto)
"""
from __future__ import annotations
import json
from pathlib import Path
from manim import *
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TRACE = ROOT / 'data' / 'traza_principal.jsonl'
GRAPH = ROOT / 'data' / 'grafo_principal.txt'

# Paleta inspirada en visualizacion matematica: fondo estable, pocos acentos.
BG = '#0B1020'
GRID = '#25334B'
INK = '#EDF4FA'
SUB = '#AABCD0'
CYAN = '#58C4DD'
TEAL = '#47D7BC'
GOLD = '#FFD76B'
VIOLET = '#B39DFF'
RED = '#FB7485'
EDGE = '#71849C'
FAINT = '#334357'
FONT = 'DejaVu Sans'

config.background_color = BG
config.frame_width = 14.222
config.frame_height = 8


def text(s: str, size: int = 26, color=INK, weight='NORMAL') -> Text:
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def fmt(d: int) -> str:
    return '∞' if d < 0 else str(d)


def load_trace():
    with open(TRACE, 'r', encoding='utf-8') as f:
        events = [json.loads(row) for row in f if row.strip()]
    if not events or events[0]['type'] != 'init' or events[-1]['type'] != 'done':
        raise ValueError('La traza tiene que empezar en init y terminar en done')
    return events


def load_graph():
    items = GRAPH.read_text(encoding='utf-8').split()
    nums = list(map(int, items))
    n,m,origin,C = nums[:4]
    flat = nums[4:]
    if len(flat) != 3*m:
        raise ValueError('Numero de aristas incorrecto')
    return n,m,origin,C,[(flat[k],flat[k+1],flat[k+2]) for k in range(0,len(flat),3)]


class GraphDrawing:
    # Diagrama fijo; las distancias que aparecen despues se sustituyen con Transform.
    POS = {
        0: (-5.15, .3), 1: (-2.55, 1.45), 2: (-2.6, -.55),
        3: (.25, 1.35), 4: (.25, -.6), 5: (3.25, .45), 6: (5.0, 1.55),
    }
    def __init__(self, edges, init_dist):
        self.nodes, self.circles, self.distance_labels = {}, {}, {}
        self.arrows = {}
        self.weights = {}
        self.arrows_group = VGroup()
        self.labels_group = VGroup()
        self.nodes_group = VGroup()
        for u,v,w in edges:
            a = np.array([*self.POS[u], 0.0]); b = np.array([*self.POS[v], 0.0])
            ar = Arrow(a,b,buff=.47,max_tip_length_to_length_ratio=.115,
                       stroke_width=2.8,color=EDGE)
            self.arrows[u,v]=ar
            self.arrows_group.add(ar)
            dv=b-a
            perp=np.array([-dv[1],dv[0],0.0])
            perp=perp/max(np.linalg.norm(perp),1e-8)
            shift = .20 if (u,v) not in [(2,1),(4,3)] else -.23
            wt = text(str(w),size=21,color=GOLD).move_to(ar.get_center()+shift*perp)
            self.weights[u,v]=wt
            self.labels_group.add(wt)
        for v, xy in self.POS.items():
            loc=np.array([xy[0],xy[1],0.0])
            ring=Circle(radius=.35,stroke_width=3,color=CYAN,fill_color=BG,
                        fill_opacity=1).move_to(loc)
            name=text(chr(65+v),size=25,weight='BOLD').move_to(loc).set_z_index(1)
            d=text('d = '+fmt(init_dist[v]),size=17,color=SUB).next_to(ring,DOWN,buff=.09)
            d.set_opacity(0)
            grp=VGroup(ring,name,d)
            self.nodes[v]=grp
            self.circles[v]=ring
            self.distance_labels[v]=d
            self.nodes_group.add(grp)
        self.group=VGroup(self.arrows_group,self.labels_group,self.nodes_group)

    def show_distances(self,scene,seconds=1.15):
        scene.animate_for(*[d.animate.set_opacity(1) for d in self.distance_labels.values()],seconds=seconds)

    def change_distance(self,scene, v, old, new, seconds=.55):
        if old==new:
            return
        old_mob=self.distance_labels[v]
        new_mob=text('d = '+fmt(new), size=17,color=TEAL).move_to(old_mob)
        scene.animate_for(Transform(old_mob,new_mob),seconds=seconds)
        self.distance_labels[v]=old_mob

    def flash_edge(self,scene,u,v,seconds=.68):
        edge=self.arrows[u,v]
        small=Dot(radius=.082,color=GOLD).move_to(edge.get_start())
        glow=edge.copy().set_color(GOLD).set_stroke(width=7,opacity=.8)
        scene.add(small)
        scene.animate_for(ShowPassingFlash(glow, time_width=.75),
                         MoveAlongPath(small,edge,rate_func=linear),seconds=seconds)
        scene.remove(small)

    def pop_node(self,scene,v,seconds=.7):
        circle=self.circles[v]
        scene.animate_for(Indicate(circle,color=TEAL,scale_factor=1.22),seconds=seconds)


class BucketDrawing:
    def __init__(self,C, init_event):
        self.C=C
        self.count=C+1
        self.frames=VGroup()
        self.contents=VGroup()
        self.index_text=[]
        self.frame_centers=[]
        step=1.70 if self.count<=7 else 11.5/self.count
        width=step-.15
        for i in range(self.count):
            x=(i-(self.count-1)/2)*step
            frame=RoundedRectangle(corner_radius=.12,width=width,height=.92,
                stroke_color=FAINT,stroke_width=1.6,fill_color='#152138',fill_opacity=.65)
            frame.move_to([x,-2.88,0])
            label=text(str(i),size=17,color=SUB).next_to(frame,UP,buff=.12)
            self.frames.add(frame,label)
            self.index_text.append(label)
            self.frame_centers.append(frame.get_center())
        self.title=text('BUCKETS',size=18,color=CYAN,weight='BOLD').move_to([-5.0,-1.79,0])
        self.subtitle=text(f'índice = distancia mod {self.count}',size=16,color=SUB).next_to(self.title,RIGHT,buff=.4)
        self.pointer=Triangle(color=GOLD,fill_color=GOLD,fill_opacity=1,stroke_width=0)
        self.pointer.scale(.105).rotate(PI).move_to([self.frame_centers[0][0],-2.11,0])
        self.contents=self.build_contents(init_event['buckets'])
        self.group=VGroup(self.frames,self.contents,self.title,self.subtitle,self.pointer)

    def build_contents(self,buckets):
        contents=VGroup()
        for i,items in enumerate(buckets):
            for j,(v,d) in enumerate(items[:3]):
                y=-2.75-(j-(len(items[:3])-1)/2)*.25
                label=text(chr(65+v)+':'+str(d),size=19,color=INK)
                label.move_to([self.frame_centers[i][0],y,0])
                contents.add(label)
        return contents

    def sync(self,scene,evt,seconds=.55):
        target=self.build_contents(evt['buckets'])
        new_index=int(evt['current'] % self.count)
        dest=np.array([self.frame_centers[new_index][0],-2.11,0])
        movements=[]
        if len(target)==0 and len(self.contents)==0:
            pass
        elif len(self.contents)==0:
            movements.append(FadeIn(target,shift=UP*.14))
        elif len(target)==0:
            movements.append(FadeOut(self.contents,shift=DOWN*.1))
        else:
            movements.append(ReplacementTransform(self.contents,target))
        if np.linalg.norm(self.pointer.get_center()-dest)>.01:
            movements.append(self.pointer.animate.move_to(dest))
        if movements:
            scene.animate_for(*movements,seconds=seconds)
        else:
            scene.pause_for(seconds)
        self.group.remove(self.contents)
        self.contents=target
        self.group.add(self.contents)


class DialFilm(Scene):
    """Un solo movimiento visual continuo; no son diapositivas enlazadas."""
    def setup(self):
        self.clock=0.0
        self.trace=load_trace()
        self.n,self.m,self.origin,self.C,self.edges=load_graph()
        if self.n!=7 or self.C!=6:
            raise ValueError('El encuadre de esta escena esta disenado para grafo_principal.txt')

    def animate_for(self,*animations,seconds=1.0,**kwargs):
        self.play(*animations,run_time=seconds,**kwargs)
        self.clock+=seconds

    def pause_for(self,seconds):
        if seconds>0:
            self.wait(seconds)
            self.clock+=seconds

    def until(self,absolute):
        delta=absolute-self.clock
        if delta>=.033:
            self.pause_for(delta)
        elif delta < -.5:
            print(f'AVISO: escena excede hito {absolute:.1f}s por {-delta:.1f}s')

    def headline(self,label,accent=CYAN):
        t=text(label,size=30,weight='BOLD').to_edge(UP,buff=.26)
        bar=Line(LEFT*.75,RIGHT*.75,stroke_width=5,color=accent).next_to(t,DOWN,buff=.12)
        return VGroup(t,bar)

    def status(self,s,color=SUB):
        return text(s,size=21,color=color).move_to([0,-1.20,0])

    def construct(self):
        self.camera.background_color=BG
        first=self.trace[0]
        graph=GraphDrawing(self.edges,first['dist'])
        bgdots=VGroup(*[
            Dot(point=[x,y,0],radius=.014,color=GRID,fill_opacity=.45)
            for x in np.arange(-6.7,6.8,.55) for y in np.arange(-3.6,3.7,.55)
        ])
        self.add(bgdots)

        # 0:00–0:12 / Pregunta antes de la respuesta
        question=self.headline('¿Cuál es el camino de menor costo?',GOLD)
        self.animate_for(FadeIn(question,shift=UP*.3),seconds=1.1)
        self.animate_for(LaggedStart(*[Create(x) for x in graph.arrows_group],lag_ratio=.12),seconds=3.0)
        self.animate_for(LaggedStart(*[FadeIn(x,scale=.75) for x in graph.nodes_group],lag_ratio=.08),seconds=2.0)
        self.animate_for(FadeIn(graph.labels_group),seconds=.7)
        preview=[(0,2),(2,4),(4,3),(3,5)]
        for u,v in preview:
            graph.flash_edge(self,u,v,seconds=.48)
        self.until(12)

        # 0:12–0:29 / Restricciones antes de 'buckets'
        concept=self.headline('Dial · caminos mínimos con pesos pequeños')
        self.animate_for(ReplacementTransform(question,concept),seconds=1.25)
        pill=text('Pesos enteros  0 ≤ w ≤ C',size=25,color=GOLD)
        pill.move_to([0,-2.25,0])
        self.animate_for(FadeIn(pill,shift=UP*.2),seconds=1.0)
        support=text('La siguiente distancia se procesa antes que las mayores.',size=22,color=SUB)
        support.next_to(pill,DOWN,buff=.3)
        self.animate_for(Write(support),seconds=2.25)
        # La pregunta '¿y sin heap?' motiva la idea de los contenedores.
        delta=text('¿Y si ordenamos por distancia?',size=26,color=CYAN)
        delta.move_to([0,-1.2,0])
        self.animate_for(FadeIn(delta,scale=.85),seconds=.9)
        # Mostramos, sobre la MISMA red, que los pesos son pequenos y discretos.
        graph.flash_edge(self,2,4,seconds=1.0)    # peso cero
        graph.flash_edge(self,4,5,seconds=1.0)    # peso seis
        graph.flash_edge(self,0,1,seconds=1.0)    # peso cuatro
        self.until(26)
        self.animate_for(FadeOut(pill,support,delta),seconds=1.0)
        self.until(29)

        # 0:29–0:50 / Los buckets emergen, grafo permanece (no corte)
        self.animate_for(graph.group.animate.scale(.82).shift(UP*.82),seconds=1.6)
        buckets=BucketDrawing(self.C,first)
        self.animate_for(FadeIn(buckets.frames,shift=UP*.2),FadeIn(buckets.title),
                         FadeIn(buckets.subtitle),seconds=1.25)
        self.animate_for(FadeIn(buckets.contents,scale=.92),GrowFromCenter(buckets.pointer),seconds=1.0)
        concept2=self.headline(f'C + 1 = {self.C+1} buckets circulares',TEAL)
        self.animate_for(ReplacementTransform(concept,concept2),seconds=.9)
        guide=text('La ficha A:0 entra al bucket de índice 0.',size=21,color=SUB)
        guide.move_to([0,-1.16,0])
        self.animate_for(FadeIn(guide),seconds=.75)
        # Puntero VIOLETA de explicacion modular (NO es el puntero real de Dial).
        # El puntero AMARILLO conserva fielmente el indice 0 de la traza de C++.
        demo=Dot(radius=.065,color=VIOLET).move_to([buckets.frame_centers[0][0],-2.0,0])
        self.animate_for(FadeIn(demo),seconds=.35)
        for k in [1,2,3,4,5,6,0]:
            point=[buckets.frame_centers[k][0],-2.0,0]
            self.animate_for(demo.animate.move_to(point),seconds=.55)
        self.animate_for(FadeOut(demo),seconds=.45)
        cyclic=text('0 → 1 → 2 → … → 6 → 0',size=21,color=GOLD).move_to(guide)
        self.animate_for(Transform(guide,cyclic),seconds=1.1)
        self.until(49)
        self.animate_for(FadeOut(guide),seconds=.5)
        self.until(50)

        # 0:50–1:08 / Inicializacion legible antes de ejecutar
        concept3=self.headline('Inicio: fuente A, distancia cero',CYAN)
        self.animate_for(ReplacementTransform(concept2,concept3),seconds=.9)
        graph.show_distances(self,seconds=1.25)
        info=self.status('d[A] = 0      ·      d[otros] = ∞',CYAN)
        self.animate_for(FadeIn(info,shift=UP*.15),seconds=.8)
        self.animate_for(Indicate(graph.circles[0],color=GOLD),seconds=1.1)
        # El infinito es una DISTANCIA DESCONOCIDA, no el peso de una arista.
        self.animate_for(LaggedStart(*[Indicate(graph.circles[i],color=SUB,scale_factor=1.08)
                    for i in [1,2,3,4,5,6]],lag_ratio=.35),seconds=4.1)
        self.animate_for(Indicate(buckets.pointer,color=GOLD),seconds=1.25)
        self.until(67)
        self.animate_for(FadeOut(info),seconds=.45)
        self.until(68)

        # 1:08–1:51 / SOLO eventos reales emitidos por C++.
        title_run=self.headline('Dial en acción: extraer, relajar, actualizar',GOLD)
        self.animate_for(ReplacementTransform(concept3,title_run),seconds=.85)
        hud=self.status('Procesando el siguiente bucket...',SUB)
        self.add(hud)
        prev=first
        durations={'pop':1.45,'relax':2.3,'reject':1.8,'stale':1.45}
        for event in self.trace[1:-1]:
            typ=event['type']; u=event['u'];v=event['v']
            if typ=='pop':
                self.animate_for(Transform(hud,self.status(f'Extraemos {chr(65+u)}: d = {fmt(event["dist"][u])}',TEAL)),seconds=.38)
                buckets.sync(self,event,seconds=.47)
                graph.pop_node(self,u,seconds=.59)
                self.pause_for(.25)
            elif typ=='relax':
                old=event['old'];cand=event['candidate']
                wording=f'{chr(65+u)} → {chr(65+v)}     {fmt(prev["dist"][u])} + {event["w"]} = {cand}'
                self.animate_for(Transform(hud,self.status(wording,GOLD)),seconds=.40)
                graph.flash_edge(self,u,v,seconds=.65)
                graph.change_distance(self,v,old,cand,seconds=.45)
                buckets.sync(self,event,seconds=.54)
                self.pause_for(.63)
            elif typ=='reject':
                wording=f'No mejora: {chr(65+v)} ya tiene {fmt(event["dist"][v])} < {event["candidate"]}'
                self.animate_for(Transform(hud,self.status(wording,SUB)),seconds=.40)
                graph.flash_edge(self,u,v,seconds=.55)
                self.pause_for(1.35)
            elif typ=='stale':
                current=event['dist'][u]
                word=f'Entrada antigua {chr(65+u)}:{event["old"]}; ahora d[{chr(65+u)}]={fmt(current)}'
                self.animate_for(Transform(hud,self.status(word,RED)),seconds=.38)
                buckets.sync(self,event,seconds=.52)
                graph.pop_node(self,u,seconds=.40)
                self.pause_for(.60)
            prev=event
        self.animate_for(Transform(hud,self.status('¡Todas las distancias están calculadas!',TEAL)),seconds=.6)
        self.until(110)
        self.animate_for(FadeOut(hud),seconds=.6)
        self.until(111)

        # 1:51–2:11 / Casos borde: demostrados con estados de esta traza.
        caveats=self.headline('Dos casos límite y un detalle importante',VIOLET)
        self.animate_for(ReplacementTransform(title_run,caveats),seconds=.9)
        zero=self.around_edge(graph,2,4)
        self.animate_for(Create(zero),seconds=.8)
        z=text('Peso 0: C y E pueden quedar a la misma distancia.',size=21,color=GOLD)
        z.move_to([0,-1.05,0]); self.animate_for(FadeIn(z),seconds=.9)
        self.until(118)
        self.animate_for(FadeOut(z,zero),seconds=.6)
        self.animate_for(Indicate(graph.circles[6],color=RED),seconds=1.1)
        unreachable=text('G es inalcanzable: d[G] = ∞',size=23,color=RED).move_to([0,-1.05,0])
        self.animate_for(FadeIn(unreachable),seconds=.8)
        self.until(124)
        ghost=text('Antiguos:  B:4    D:6    F:7',size=22,color=VIOLET)
        ghost.move_to([0,-1.05,0])
        self.animate_for(ReplacementTransform(unreachable,ghost),seconds=.65)
        self.until(130)
        self.animate_for(FadeOut(ghost),seconds=.5)
        self.until(131)

        # 2:11–2:30 / Formula como consecuencia de dos movimientos visibles
        compl=self.headline('¿Por qué es eficiente?',TEAL)
        self.animate_for(ReplacementTransform(caveats,compl),seconds=.85)
        # Cada grupo de movimientos evidencia uno de los dos sumandos.
        for uu,vv in [(0,2),(2,4),(4,3)]:
            graph.flash_edge(self,uu,vv,seconds=.82)
        guide_pointer=Dot(radius=.065,color=VIOLET).move_to([buckets.frame_centers[0][0],-2.0,0])
        self.animate_for(FadeIn(guide_pointer),seconds=.25)
        for k in range(7):
            self.animate_for(guide_pointer.animate.move_to([buckets.frame_centers[k][0],-2.0,0]),seconds=.31)
        self.animate_for(FadeOut(guide_pointer),seconds=.25)
        self.animate_for(FadeOut(buckets.group),graph.group.animate.scale(.81).shift(UP*.4),seconds=1.1)
        formula=text('O(|E| + C · |V|)',size=42,color=GOLD,weight='BOLD').move_to([0,-1.1,0])
        left=text('Aristas inspeccionadas',size=23,color=CYAN).move_to([-2.7,-2.12,0])
        right=text('Distancias recorridas',size=23,color=TEAL).move_to([2.7,-2.12,0])
        self.animate_for(Write(formula),seconds=1.1)
        self.animate_for(FadeIn(left,shift=UP*.12),FadeIn(right,shift=UP*.12),seconds=.9)
        foot=text('Ventajoso si C es pequeño.',size=23,color=SUB).move_to([0,-3.05,0])
        self.animate_for(FadeIn(foot),seconds=.8)
        self.until(149)
        self.animate_for(FadeOut(left,right,foot),seconds=.5)
        self.until(150)

        # 2:30–2:40 / Conclusión y créditos. Nombres se agregan en config.json.
        ending=self.headline('Resultado desde A',CYAN)
        self.animate_for(ReplacementTransform(compl,ending),FadeOut(formula),seconds=.75)
        done=self.trace[-1]['dist']
        row=text('  ·  '.join(f'{chr(65+i)}={fmt(v)}' for i,v in enumerate(done)),
                 size=24,color=GOLD).move_to([0,-1.25,0])
        self.animate_for(FadeIn(row,scale=.92),seconds=1.1)
        people=self.team_credit()
        self.animate_for(FadeIn(people,shift=UP*.1),seconds=.85)
        self.until(160)

    def around_edge(self, graph, u, v):
        obj=graph.arrows[u,v]
        return obj.copy().set_color(GOLD).set_stroke(width=8,opacity=.95)

    def team_credit(self):
        # Se rellenan nombres mediante archivo externo; no se inventan integrantes.
        path=ROOT/'config.json'
        try:
            people=json.loads(path.read_text(encoding='utf-8'))['integrantes']
        except Exception:
            people=['Integrante 1','Integrante 2','Integrante 3']
        names='  ·  '.join(str(n) for n in people)
        return VGroup(
            text('CS2023 · Algoritmos y Estructuras de Datos',size=17,color=SUB),
            text(names,size=17,color=SUB)
        ).arrange(DOWN,buff=.15).move_to([0,-2.8,0])
