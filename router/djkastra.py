# ----------------------------------------------------------------------------------------------------------- #

'''
Bibliotecas necessárias
'''

from typing import Dict, Tuple, Any

# ----------------------------------------------------------------------------------------------------------- #

'''
Funções principais
'''

def dijkstra(origem: str, lsdb: Dict[str, Any]) -> Dict[str, str]:
    """
    Implementa o algoritmo de Dijkstra para encontrar o caminho mais curto em um grafo.
    O grafo é representado por um dicionário onde as chaves são os IDs dos roteadores e os valores são dicionários

    Args:
        origem (str): ID do roteador de origem.
        lsdb (Dict[str, Any]): Dicionário que representa a LSDB (Link State Database). 
        Cada chave é o ID do roteador e o valor é um dicionário com informações sobre o roteador, incluindo a vizinhança.

    Returns:
        Dict[str, str]: Dicionário onde as chaves são os IDs dos roteadores de destino e os valores são os próximos saltos.
    """
    grafo = {}
    for idRouter, lsa in lsdb.items():
        vizinhanca = {}
        for v in lsa["vizinhanca"].values():
            ip, custo = v
            if ip in lsdb:
                vizinhanca[ip] = custo
        grafo[idRouter] = vizinhanca
        
    distancias = {i: float('inf') for i in grafo}
    anterior = {i: None for i in grafo}
    distancias[origem] = 0
    visitados = set()
    
    while len(visitados) < len(grafo):
        x = min((i for i in grafo if i not in visitados), key=lambda i: distancias[i])
        visitados.add(x)
        for v, c in grafo[x].items():
            if distancias[x] + custo < distancias[v]:
                distancias[v] = distancias[x] + c
                anterior[v] = x
                
    tabela = {}
    for destino in grafo:
        if destino == origem or anterior[destino] is None:
            continue
        salto = destino
        while anterior[salto] != origem:
            salto = anterior[salto]
        tabela[destino] = salto
        
    return tabela
        
# ----------------------------------------------------------------------------------------------------------- #

'''
Execução do dijkstra
'''

if __name__ == "__main__":
    lsdb = {
        "172.20.1.3": {
            "id": "172.20.1.3",
            "vizinhanca": {
                "ROUTER_6": [
                    "172.20.6.3",
                    1
                ],
                "ROUTER_2": [
                    "172.20.2.3",
                    1
                ]
            },
            "seq": 3
        },
        "172.20.3.3": {
            "id": "172.20.3.3",
            "vizinhanca": {
                "ROUTER_2": [
                    "172.20.2.3",
                    1
                ],
                "ROUTER_4": [
                    "172.20.4.3",
                    1
                ]
            },
            "seq": 3
        },
        "172.20.4.3": {
            "id": "172.20.4.3",
            "vizinhanca": {
                "ROUTER_3": [
                    "172.20.3.3",
                    1
                ],
                "ROUTER_5": [
                    "172.20.5.3",
                    1
                ]
            },
            "seq": 3
        },
        "172.20.5.3": {
            "id": "172.20.5.3",
            "vizinhanca": {
                "ROUTER_4": [
                    "172.20.4.3",
                    1
                ],
                "ROUTER_6": [
                    "172.20.6.3",
                    1
                ]
            },
            "seq": 3
        },
        "172.20.6.3": {
            "id": "172.20.6.3",
            "vizinhanca": {
                "ROUTER_5": [
                    "172.20.5.3",
                    1
                ],
                "ROUTER_1": [
                    "172.20.1.3",
                    1
                ]
            },
            "seq": 3
        },
        "172.20.2.3": {
            "id": "172.20.2.3",
            "vizinhanca": {
                "ROUTER_1": [
                    "172.20.1.3",
                    1
                ],
                "ROUTER_3": [
                    "172.20.3.3",
                    1
                ]
            },
            "seq": 3
        }
    }
    print(dijkstra("172.20.2.3", lsdb))