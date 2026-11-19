# Go-Hybrid Wildcard Track — external submission package (NOT yet submitted)

Target: https://github.com/limitlessprojects/Go-Hybrid/issues/new?template=wildcard.yml

Proposed title: **[wildcard] Make Tier-0 verification incremental: fail-closed Merkle proof DAG instead of mandatory full rechecks**

**Status:** Original proof-of-concept tested; upstream filing attempt returned GitHub 403 `Resource not accessible by integration`; no acceptance, award or payment. Do not represent this file as a contest submission.

## The idea, in a paragraph

**Sacred cow:** after any source edit, all existing safety conclusions must be rederived as an inseparable whole. Replace this with content-addressed proof nodes: a checked function or strongly connected component receives a digest covering its normalized typed source, imported signature/sendability facts, generic instantiations, the checker ruleset/version, and hashes of every proof it depends on. A cached ACCEPT result is reused only if the complete transitive digest matches. Unknown/dynamic edges or stale summaries fall back to full module checking. The reusable proof DAG makes a changed task-boundary obligation invalidate every affected caller, while isolating unrelated modules; full checking remains the reference oracle.

## Distinction from existing work

Related proposals #345, #565 and #3930 explore Go translation verification, Go-as-oracle and emitted witnesses. This proposal is specifically about **sound reuse of prior checker decisions across edited source**; it does not claim that a proof digest validates emitter soundness.

## Reproduction and evidence

Runnable Python-only cache model (not actual Hybrid): [proof_dag.py](./proof_dag.py).

Run `python proof_dag.py`. Local Python standard library results:

- PASS: 200 successive edits across 184 unique nodes in a 1,200-node graph, with every incremental digest identical to a from-scratch reference digest.
- PASS: checker version change invalidated all 1,200 proof digests.
- PASS: dependency edge change propagated to affected digests.
- PASS: introduced cycle was rejected instead of trusting cached digests.

**Limit:** This synthetic model hashes opaque source text and explicitly declared edges; it does **not** extract real Hybrid alias/effect dependencies, check safety, run Hybrid CI, or show real performance improvements.

## Experimental Hybrid spike

1. Instrument Tier-0 checks to enumerate each consulted alias, type, import, capture, generic and sendability summary. Missing edges force full checking. SCCs count as one proof unit.
2. Add an optional `hyb check --incremental-proof` mode with immutable dependency fingerprints; never silently trust cached accept results on unknown/dynamic edges.
3. For at least 200 deterministic changes across task boundaries, foreign calls, managed escape, generics, imports and buildable/emitter cases, require **identical accept/reject, diagnostics and Go-build outcomes** to clean full checker. One mismatch ends the experiment.
4. Benchmark p95 edit-to-check latency, CPU and cache size on a large multi-module corpus, comparing against full checking *including* hash/invalidation overhead. Stop if improvement is less than 2x or cache size exceeds 25% of uncompressed checked source.
5. Change checker build, rule version, Go toolchain, unresolved dependencies and dynamic calls; force rechecks. Re-run full existing corpus.

## Cost and falsifiability

Dependency completeness is the hard problem, not SHA hashing. Overconservative invalidation may erase any benefit. The incremental algorithm may be slower than whole-file rechecking and may introduce new soundness risks; reject rather than weaken guarantees. There are no Hybrid-specific results, safety claims or real speedup numbers yet.

**Disclosure:** AI-assisted proposal and locally tested synthetic script; no upstream issue, PR, sponsor approval, or bounty payout yet. Subject to BOUNTY.md/MOONSHOT.md and sponsor discretion. Submission for review never equals a payment claim.
