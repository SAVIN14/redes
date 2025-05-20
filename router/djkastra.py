def dijkstra(origem: str, lsdb):
   
    grafo = {}
    for idRouter, lsa in lsdb.items():
        vizinhanca = {}
        for v in lsa["vizin"].values():
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
 