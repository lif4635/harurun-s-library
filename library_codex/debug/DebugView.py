"""フロー・グラフ・配列の現在値をHaru Deskの右側へ送る。"""

import hashlib
import json
import math
import os
import tempfile
import time


def _debug_number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError("edge values must be numbers")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("edge values must be finite")
    text = str(value)
    if len(text) > 1000:
        raise ValueError("edge numbers must be at most 1000 characters")
    return text


def _debug_vertices(n, labels, positions):
    if not isinstance(n, int) or not 0 <= n <= 500:
        raise ValueError("viewer supports 0 to 500 vertices")
    if labels is not None and len(labels) != n:
        raise ValueError("labels must contain one label per vertex")
    if positions is not None and len(positions) != n:
        raise ValueError("positions must contain one [x, y] per vertex")
    nodes = []
    for i in range(n):
        node = {"id": i, "label": str(i if labels is None else labels[i])}
        if len(node["label"]) > 20000:
            raise ValueError("labels must be at most 20000 characters")
        if positions is not None:
            x, y = positions[i]
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("positions must be finite")
            node["position"] = [float(x), float(y)]
        nodes.append(node)
    return nodes


def _debug_endpoint(v, n):
    if not isinstance(v, int) or not 0 <= v < n:
        raise ValueError("edge endpoint outside graph")


def _debug_write(payload, name, directory):
    name = str(name)
    if len(name) > 200:
        raise ValueError("name must be at most 200 characters")
    payload.update(schemaVersion=1, name=name, pid=os.getpid(), capturedAt=time.time_ns())
    text = json.dumps(payload, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    if len(text) > 2 * 1024 * 1024:
        raise ValueError("snapshot exceeds 2 MiB; select a smaller graph or array")
    directory = os.path.abspath(directory or os.environ.get("HARU_DUMP_DIR") or ".haru-dump")
    os.makedirs(directory, exist_ok=True)
    key = hashlib.sha256(name.encode()).hexdigest()[:16]
    destination = os.path.join(directory, str(os.getpid()) + "-" + key + ".json")
    fd, temporary = tempfile.mkstemp(prefix=".snapshot-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return destination


def dump_flow(graph, source=None, sink=None, *, name="flow", labels=None, positions=None, directory=None):
    """現在の辺の容量・流量・残余容量をJSONへ保存する。グラフは変更しない。"""
    n = graph.n
    nodes = _debug_vertices(n, labels, positions)
    for vertex in (source, sink):
        if vertex is not None:
            _debug_endpoint(vertex, n)
    if source is not None and source == sink:
        raise ValueError("source and sink must differ")
    edges = []
    adjacency = [[] for _ in range(n)]
    balance = [0] * n
    ordinary = True
    for i, row in enumerate(graph.edges()):
        if i >= 3000:
            raise ValueError("viewer supports at most 3000 edges")
        cost = None
        lower = 0
        if len(row) == 4:
            u, v, capacity, flow = row
        elif len(row) == 5:
            u, v, capacity, flow, cost = row
            ordinary = False
        elif len(row) == 6:
            u, v, lower, capacity, cost, flow = row
            ordinary = False
        else:
            raise TypeError("unsupported flow edge format")
        _debug_endpoint(u, n)
        _debug_endpoint(v, n)
        edge = {"id": i, "from": u, "to": v, "capacity": _debug_number(capacity),
                "flow": _debug_number(flow), "lower": _debug_number(lower),
                "forward": _debug_number(capacity - flow), "reverse": _debug_number(flow - lower)}
        if not lower <= flow <= capacity:
            raise ValueError("flow outside bounds; b-flow must have a feasible solution")
        if cost is not None:
            edge["cost"] = _debug_number(cost)
        edges.append(edge)
        if capacity > flow:
            adjacency[u].append(v)
        if flow > lower:
            adjacency[v].append(u)
        balance[u] += flow
        balance[v] -= flow
    reachable = [False] * n
    if source is not None:
        reachable[source] = True
        queue = [source]
        for u in queue:
            for v in adjacency[u]:
                if not reachable[v]:
                    reachable[v] = True
                    queue.append(v)
    feasible = source is not None and sink is not None and all(
        balance[i] == 0 for i in range(n) if i != source and i != sink
    ) and balance[source] >= 0 and balance[source] == -balance[sink]
    minimum = bool(ordinary and feasible and not reachable[sink])
    return _debug_write({"kind": "flow", "nodes": nodes, "edges": edges, "directed": True,
                   "source": source, "sink": sink, "reachable": reachable,
                   "minimumCut": minimum}, name, directory)


def dump_graph(n, edges, *, directed=False, name="graph", labels=None, positions=None, directory=None):
    """辺listのグラフや木をJSONへ保存する。辺は(u, v)または(u, v, weight)。"""
    nodes = _debug_vertices(n, labels, positions)
    result = []
    for i, row in enumerate(edges):
        if i >= 3000:
            raise ValueError("viewer supports at most 3000 edges")
        if len(row) not in (2, 3):
            raise ValueError("edges must be (u, v) or (u, v, weight)")
        u, v = row[:2]
        _debug_endpoint(u, n)
        _debug_endpoint(v, n)
        edge = {"id": i, "from": u, "to": v}
        if len(row) == 3:
            edge["weight"] = _debug_number(row[2])
        result.append(edge)
    return _debug_write({"kind": "graph", "nodes": nodes, "edges": result,
                   "directed": bool(directed)}, name, directory)


def dump_array(values, *, name="array", directory=None):
    """列またはtolist()を持つ構造の論理値を、添字付き表示用JSONへ保存する。"""
    if hasattr(values, "tolist"):
        values = values.tolist()
    result = []
    for value in values:
        if len(result) >= 10000:
            raise ValueError("viewer supports at most 10000 array elements")
        text = str(value)
        if len(text) > 20000:
            raise ValueError("array values must be at most 20000 characters")
        result.append(text)
    return _debug_write({"kind": "array", "values": result}, name, directory)
