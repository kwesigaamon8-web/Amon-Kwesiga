# Source-level bug reproducer: Interval.add / contains / overlap

This file independently checks **the current source logic** in `bad-antics/lateralus-lang/stdlib/interval.ltl` for mathematical interval semantics. It is not Lateralus execution (upstream #114 already reports a parser blocker). The reproducer is a direct, transparent Python translation, without third-party dependencies.

```python
def source_add(a, b):
    if a[0] > b[1]:
        return b
    if a[1] < b[0]:
        return a
    lower = max(a[0], min(b[0], a[1]))
    upper = min(a[1], max(b[1], a[0]))
    return (lower, upper)

def source_contains(a, b):
    return a[0] <= b[1] and b[0] <= a[1]

def source_overlap(a, b):
    return not source_contains(b, a)

def test_bug():
    assert source_add((1, 2), (3, 4)) == (1, 2)  # expected math (4, 6)
    assert source_add((1, 5), (2, 3)) == (2, 3)  # expected math (3, 8)
    assert source_contains((1, 2), (1.5, 3))     # expected False
    assert not source_overlap((1, 2), (1.5, 3))  # expected True
    assert source_overlap((1, 2), (9, 10))      # expected False

if __name__ == "__main__":
    test_bug()
    print("Five source-level defects independently reproduced")
```

## Evidence / correction
- Source: https://github.com/bad-antics/lateralus-lang/blob/main/stdlib/interval.ltl
- Arithmetic `add([a,b],[c,d])` should compute `[a+c,b+d]` (not conditional intersection/return input).
- Containment `contains(left,right)` should be `left.lower <= right.lower && right.upper <= left.upper`.
- Overlap `overlap(left,right)` should be `left.lower <= right.upper && right.lower <= left.upper` for closed intervals.
- There is also a separate existing parser issue (#114), so this report does NOT claim the Lateralus runtime executed.
- Verify these five input/expected vectors after #114 is fixed; include parser+runtime regression tests before declaring full fix.

## Commercial status
Submitted as original evidence for the project's recurring **$10 high-signal bug report micro-bounty** if eligible. This is a source-level proof and is not an accepted bounty, merge, invoice, or payment. Public B1 native BTC mainnet receiving route if sponsor independently agrees to settle: `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z`. No email or wallet signing.
