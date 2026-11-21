"""Independent ENIGMA test of AUREN's order-dependent ticker normalization.

Inspected: Ayush441-python/AUREN/api.py at 1ec8dba56cb82981fe334da8ed4311c7c4b3632d.
Copies only the vulnerable helper's normalization statements. This does NOT call
a live API, verify bounty funding, or submit/claim payment.
"""
import math
import pandas as pd

def current_normalize(weights):
    clean_weights = {k.strip().upper(): v for k, v in weights.items()}
    w = pd.Series(clean_weights, dtype=float)
    if (w <= 0).any() or w.sum() <= 0:
        raise ValueError("invalid weights")
    return w / w.sum()

def reject_collisions(weights):
    clean_weights = {}
    for raw_key, value in weights.items():
        ticker = raw_key.strip().upper()
        if ticker in clean_weights:
            raise ValueError(f"Duplicate ticker after normalization: {ticker}")
        clean_weights[ticker] = value
    w = pd.Series(clean_weights, dtype=float)
    return w / w.sum()

def test_order_changes_result_without_changing_input_holdings():
    a = {"NVDA": 99, " nvda ": 1, "MSFT": 100}
    b = {" nvda ": 1, "NVDA": 99, "MSFT": 100}
    aw, bw = current_normalize(a), current_normalize(b)
    assert sum(a.values()) == sum(b.values()) == 200
    assert math.isclose(aw["NVDA"], 1/101, abs_tol=1e-15)
    assert math.isclose(bw["NVDA"], 99/199, abs_tol=1e-15)
    assert abs(aw["NVDA"] - bw["NVDA"]) > .48

def test_collision_rejected_in_both_orders():
    for p in (
        {"NVDA": 99, " nvda ": 1, "MSFT": 100},
        {" nvda ": 1, "NVDA": 99, "MSFT": 100},
    ):
        try:
            reject_collisions(p)
        except ValueError as e:
            assert str(e) == "Duplicate ticker after normalization: NVDA"
        else:
            raise AssertionError("ticker collision silently accepted")

def test_normal_portfolio_works_with_fixed_normalizer():
    assert reject_collisions({" nvda ":40, "msft":60}).to_dict() == {
        "NVDA": 0.4, "MSFT": 0.6}

if __name__ == "__main__":
    test_order_changes_result_without_changing_input_holdings()
    test_collision_rejected_in_both_orders()
    test_normal_portfolio_works_with_fixed_normalizer()
    print("PASS: 3 tests; order-dependent bug reproduced; fix rejects collision")
