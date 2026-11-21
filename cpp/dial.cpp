// Proyecto Final 2 - Algoritmo de Dial | CS2023 UTEC (2026-2)
// Implementacion propia, sin bibliotecas de caminos minimos.
// Compilar: g++ -std=c++17 -O2 -Wall -Wextra cpp/dial.cpp -o dial
// Ejecutar: ./dial data/grafo_principal.txt data/traza.jsonl
#include <algorithm>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

struct Arista { int destino, peso; };
struct Entrada { int vertice; long long distancia; };

struct Grafo {
    int n = 0, m = 0, origen = 0, C = 0;
    vector<vector<Arista>> adj;
};

Grafo leer_grafo(const string& ruta) {
    ifstream f(ruta);
    if (!f) throw runtime_error("No se pudo abrir el grafo: " + ruta);
    Grafo g;
    if (!(f >> g.n >> g.m >> g.origen >> g.C))
        throw runtime_error("Cabecera invalida. Formato: n m origen C");
    if (g.n < 1 || g.m < 0 || g.C < 0 || g.origen < 0 || g.origen >= g.n)
        throw runtime_error("Parametros de cabecera invalidos");
    g.adj.resize(g.n);
    for (int i = 0; i < g.m; ++i) {
        int u, v, w;
        if (!(f >> u >> v >> w)) throw runtime_error("Arista incompleta");
        if (u < 0 || u >= g.n || v < 0 || v >= g.n || w < 0 || w > g.C)
            throw runtime_error("Arista invalida: indices fuera de rango o peso fuera de [0,C]");
        g.adj[u].push_back({v, w});
    }
    return g;
}

// Un registro es una fotografia del ESTADO REAL del algoritmo.
// -1 representa infinito/no definido. Las listas de buckets son creadas por Dial.
void emitir(ostream& os, const string& tipo, const Grafo& g,
           const vector<long long>& dist, const vector<int>& padre,
           const vector<bool>& extraido, const vector<vector<Entrada>>& buckets,
           long long actual, int u = -1, int v = -1, int w = -1,
           long long antes = -1, long long candidato = -1) {
    os << "{\"type\":\"" << tipo << "\",\"n\":" << g.n << ",\"m\":" << g.m
       << ",\"C\":" << g.C << ",\"source\":" << g.origen
       << ",\"current\":" << actual << ",\"u\":" << u
       << ",\"v\":" << v << ",\"w\":" << w
       << ",\"old\":" << antes << ",\"candidate\":" << candidato;
    os << ",\"dist\":[";
    for (int i = 0; i < g.n; ++i) { if (i) os << ','; os << dist[i]; }
    os << "],\"parent\":[";
    for (int i = 0; i < g.n; ++i) { if (i) os << ','; os << padre[i]; }
    os << "],\"settled\":[";
    for (int i = 0; i < g.n; ++i) { if (i) os << ','; os << (extraido[i] ? "true" : "false"); }
    os << "],\"buckets\":[";
    for (size_t i = 0; i < buckets.size(); ++i) {
        if (i) os << ',';
        os << '[';
        for (size_t j = 0; j < buckets[i].size(); ++j) {
            if (j) os << ',';
            os << "[" << buckets[i][j].vertice << ',' << buckets[i][j].distancia << ']';
        }
        os << ']';
    }
    os << "]}\n";
}

vector<long long> dial(const Grafo& g, ostream& traza) {
    constexpr long long INF = numeric_limits<long long>::max() / 4;
    vector<long long> dist(g.n, INF);
    vector<int> padre(g.n, -1);
    vector<bool> extraido(g.n, false);
    // Estructura de buckets implementada por el grupo: indice circular d % (C+1).
    vector<vector<Entrada>> buckets(static_cast<size_t>(g.C) + 1);
    long long pendientes = 1;
    long long actual = 0;
    dist[g.origen] = 0;
    buckets[0].push_back({g.origen, 0});
    auto tomar_snapshot = [&](const string& tipo, int u=-1, int v=-1, int w=-1,
                              long long antes=-1, long long candidato=-1) {
        vector<long long> visibles = dist;
        for (auto& d : visibles) if (d == INF) d = -1;
        emitir(traza, tipo, g, visibles, padre, extraido, buckets,
               actual, u, v, w, antes, candidato);
    };
    tomar_snapshot("init");
    while (pendientes > 0) {
        auto& bucket = buckets[static_cast<size_t>(actual % (g.C + 1LL))];
        if (bucket.empty()) { ++actual; continue; }
        Entrada item = bucket.back();
        bucket.pop_back();
        --pendientes;
        const int u = item.vertice;
        if (item.distancia != actual || item.distancia != dist[u] || extraido[u]) {
            tomar_snapshot("stale", u, -1, -1, item.distancia);
            continue;
        }
        extraido[u] = true;
        tomar_snapshot("pop", u);
        for (const auto& arista : g.adj[u]) {
            int v = arista.destino, w = arista.peso;
            long long candidato = dist[u] + w;
            long long antes = (dist[v] == INF ? -1 : dist[v]);
            if (candidato < dist[v]) {
                dist[v] = candidato;
                padre[v] = u;
                buckets[static_cast<size_t>(candidato % (g.C + 1LL))].push_back({v, candidato});
                ++pendientes;
                tomar_snapshot("relax", u, v, w, antes, candidato);
            } else {
                tomar_snapshot("reject", u, v, w, antes, candidato);
            }
        }
    }
    tomar_snapshot("done");
    for (auto& d : dist) if (d == INF) d = -1;
    return dist;
}

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            cerr << "Uso: dial <grafo.txt> <salida.jsonl>\n";
            return 2;
        }
        Grafo g = leer_grafo(argv[1]);
        ofstream salida(argv[2]);
        if (!salida) throw runtime_error("No se pudo crear el archivo de traza");
        auto dist = dial(g, salida);
        cout << "Distancias desde el vertice " << g.origen << ":\n";
        for (int i = 0; i < g.n; ++i)
            cout << "  " << char('A' + (i % 26)) << " = "
                 << (dist[i] == -1 ? "INF" : to_string(dist[i])) << '\n';
        cout << "Traza real generada: " << argv[2] << '\n';
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}
