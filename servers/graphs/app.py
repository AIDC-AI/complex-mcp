from fastmcp import FastMCP
import heapq
from collections import defaultdict, deque

mcp = FastMCP("GraphsServer")


@mcp.tool
async def bfs(adj: dict, start) -> list:
    """Perform breadth-first search on `adj` from `start` and return visit order.

    `adj` is expected to be a mapping node -> iterable of neighbors.
    """
    visited = set()
    order = []
    q = deque([start])
    visited.add(start)
    while q:
        v = q.popleft()
        order.append(v)
        for nb in adj.get(v, []):
            if nb not in visited:
                visited.add(nb)
                q.append(nb)
    return order


@mcp.tool
async def dfs(adj: dict, start) -> list:
    """Perform depth-first search on `adj` from `start` and return visit order."""
    visited = set()
    order = []
    stack = [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        order.append(v)
        for nb in adj.get(v, []):
            if nb not in visited:
                stack.append(nb)
    return order


@mcp.tool
async def shortest_path_dijkstra(adj: dict, source) -> dict:
    """Compute shortest-path distances from `source` using Dijkstra's algorithm.

    `adj` should map nodes to an iterable of `(neighbor, weight)` pairs.
    Returns a mapping node -> distance.
    """
    # adj: node -> list of (neighbor, weight)
    dist = {source: 0}
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist.get(u, float('inf')):
            continue
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


@mcp.tool
async def is_bipartite(adj: dict) -> bool:
    """Return True if graph `adj` is bipartite (2-colorable), False otherwise."""
    color = {}
    for start in adj:
        if start in color:
            continue
        queue = deque([start])
        color[start] = 0
        while queue:
            u = queue.popleft()
            for v in adj.get(u, []):
                if v in color:
                    if color[v] == color[u]:
                        return False
                else:
                    color[v] = 1 - color[u]
                    queue.append(v)
    return True


@mcp.tool
async def connected_components(adj: dict) -> list[list]:
    """Return a list of connected components (each a list of nodes) in `adj`."""
    seen = set()
    comps = []
    for n in adj:
        if n in seen:
            continue
        comp = []
        q = deque([n])
        seen.add(n)
        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj.get(u, []):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        comps.append(comp)
    return comps


@mcp.tool
async def topological_sort(adj: dict) -> list:
    """Return a topological ordering of `adj` if it is a DAG; raises on cycles."""
    indeg = defaultdict(int)
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
        if u not in indeg:
            indeg[u] += 0
    q = deque([n for n, d in indeg.items() if d == 0])
    res = []
    while q:
        u = q.popleft()
        res.append(u)
        for v in adj.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(res) != len(indeg):
        raise ValueError("graph has cycles")
    return res


@mcp.tool
async def mst_kruskal(edges: list, nodes: list) -> list:
    """Compute a Minimum Spanning Tree using Kruskal's algorithm.

    `edges` is a list of `(weight, u, v)` triples and `nodes` lists all nodes.
    Returns a list of edges included in the MST.
    """
    # edges: list of (w,u,v)
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        parent[ra] = rb

    res = []
    for w, u, v in sorted(edges):
        if find(u) != find(v):
            union(u, v)
            res.append((w, u, v))
    return res


@mcp.tool
async def shortest_path_unweighted(adj: dict, source) -> dict:
    """Compute shortest path distances in an unweighted graph (BFS distances)."""
    dist = {source: 0}
    q = deque([source])
    while q:
        u = q.popleft()
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


@mcp.tool
async def path_exists(adj: dict, a, b) -> bool:
    """Return True if there exists a path from node `a` to node `b` in `adj`."""
    return b in bfs.__wrapped__(adj, a)


@mcp.tool
async def adjacency_matrix(adj: dict, nodes: list) -> list[list[int]]:
    """Build an adjacency matrix for `nodes` from adjacency mapping `adj`.

    Returns a square matrix of 0/1 ints where entry [i][j] is 1 if there is an edge.
    """
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    mat = [[0] * n for _ in range(n)]
    for u in adj:
        for v in adj[u]:
            if u in idx and v in idx:
                mat[idx[u]][idx[v]] = 1
    return mat


@mcp.tool
async def adjacency_list_to_matrix(adj: dict) -> list:
    """Convert adjacency list mapping to an adjacency matrix using the list of keys as nodes."""
    nodes = list(adj.keys())
    return await adjacency_matrix.__wrapped__(adj, nodes)


@mcp.tool
async def degree_centrality(adj: dict) -> dict:
    """Return the degree (number of neighbors) for each node in `adj`."""
    return {n: len(adj.get(n, [])) for n in adj}


@mcp.tool
async def is_connected(adj: dict) -> bool:
    """Return True if the graph `adj` is connected (single component)."""
    if not adj:
        return True
    start = next(iter(adj))
    comp = bfs.__wrapped__(adj, start)
    return len(comp) == len(adj)


@mcp.tool
async def graph_complement(adj: dict, nodes: list) -> dict:
    """Return the complement graph of `adj` over the provided `nodes`.

    Nodes not present in `adj` are treated as having no neighbors.
    """
    comp = {n: [] for n in nodes}
    s = set(nodes)
    for u in nodes:
        nbrs = set(adj.get(u, []))
        others = s - nbrs - {u}
        comp[u] = list(others)
    return comp


@mcp.tool
async def random_erdos_renyi(n: int, p: float) -> dict:
    """Generate a random undirected Erdos-Renyi graph with `n` nodes and edge probability `p`.

    Returns an adjacency mapping node -> list of neighbors.
    """
    import random

    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                adj[i].append(j)
                adj[j].append(i)
    return adj

