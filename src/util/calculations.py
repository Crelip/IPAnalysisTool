from collections.abc import Iterable
from math import floor

def lenOfIterable(items: Iterable) -> int:
    result : int = 0
    for item in items:
        result += 1
    return result

def getHIndex(g, values, **kwargs) -> int:
    n = kwargs.get('count', 0)
    freq = [0] * (n + 1)
    for item in g.edges():
        v = floor(values[item])
        if v >= n: freq[n] += 1
        else: freq[v] += 1
    cumulative = 0
    for h in range(n, -1, -1):
        cumulative += freq[h]
        if cumulative >= h: return h
    return 0