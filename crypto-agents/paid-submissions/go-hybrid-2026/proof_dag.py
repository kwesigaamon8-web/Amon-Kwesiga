"""Synthetic proof-DAG cache prototype, not the Go-Hybrid checker.

Goal: a cached verification result can only be reused if all source,
transitive dependencies and the ruleset fingerprint are unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, random


def H(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()

@dataclass(frozen=True)
class Node:
    source: str
    deps: tuple[str, ...]


def full_check(nodes, rule_version):
    """Deterministic conservative reference recomputation for an acyclic dependency graph."""
    output = {}
    visited = set()
    active = set()
    def visit(k):
        if k in active:
            raise ValueError('Cycle: strongly connected component must be collapsed before checking')
        if k in visited:
            return output[k]
        active.add(k)
        node = nodes[k]
        dep_proofs = [(x, visit(x)) for x in node.deps]
        output[k] = H(rule_version, k, node.source, dep_proofs)
        active.remove(k)
        visited.add(k)
        return output[k]
    for k in sorted(nodes):
        visit(k)
    return output


def incremental_check(nodes, rule_version, cache):
    """Returns all proof fingerprints and number of nodes recomputed.

    NOTE: This is a cache-dependency model only; it does not prove any program safe.
    """
    output = {}
    active = set()
    rebuilt = 0
    def visit(k):
        nonlocal rebuilt
        if k in active:
            raise ValueError("Cycle: collapse strongly connected components")
        if k in output:
            return output[k]
        active.add(k)
        node = nodes[k]
        dep_proofs = [(x, visit(x)) for x in node.deps]
        key = H(rule_version, k, node.source, dep_proofs)
        if cache.get(k) != key:
            rebuilt += 1
        output[k] = key
        active.remove(k)
        return key
    for k in sorted(nodes):
        visit(k)
    return output, rebuilt


def exercise():
    # Modular, layered acyclic graph. All dependency edges are explicit.
    nodes = {f'n{i}': Node(f'v{i}', tuple(f'n{p}' for p in sorted({i // 2, i // 3}) if 1 <= p < i))
             for i in range(1, 1201)}
    original = full_check(nodes, 'ruleset1')
    matched = 0
    unique = set()
    rng = random.Random(20261119)
    for attempt in range(200):
        j = rng.randint(1, 1200)
        n = f'n{j}'
        nodes[n] = Node(f'v{j}-edit-{attempt}', nodes[n].deps)
        new, n_rebuilt = incremental_check(nodes, 'ruleset1', original)
        assert new == full_check(nodes, 'ruleset1'), (attempt, 'unsound reuse')
        assert n_rebuilt >= 1
        assert n_rebuilt <= len(nodes)
        original = new
        matched += 1
        unique.add(n)
    updated, count = incremental_check(nodes, 'ruleset2', original)
    assert updated == full_check(nodes, 'ruleset2')
    assert count == len(nodes), 'rule-version change must invalidate every proof'
    # Changed dependency edge invalidates only relevant affected nodes.
    n = 'n1100'
    nodes[n] = Node(nodes[n].source, nodes[n].deps + ('n1',))
    changed, count = incremental_check(nodes, 'ruleset2', updated)
    assert changed == full_check(nodes, 'ruleset2')
    assert count >= 1
    # A cycle must fail closed: not be accepted on cached proofs.
    nodes['n1'] = Node(nodes['n1'].source, ('n1200',))
    try:
        full_check(nodes, 'ruleset2')
        raise AssertionError('cycle admitted')
    except ValueError:
        pass
    try:
        incremental_check(nodes, "ruleset2", changed)
        raise AssertionError("incremental cache admitted cycle")
    except ValueError:
        pass
    print(f'PASS: 200 edits, {len(unique)} unique nodes, recomputation matches full oracle')
    print('PASS: ruleset change invalidates 1,200 proofs; dependency edge change propagated')
    print('PASS: cycle rejected instead of reusing stale proof')
    print('LIMIT: synthetic dependency graph only, not Hybrid integration/CI, no real benchmark')

if __name__ == '__main__':
    exercise()
