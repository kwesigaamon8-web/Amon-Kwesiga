"""ALL W/S/G/H descendant workers share one executable, with a tier-specific task.

This file is intentionally a tiny shared-role entrypoint: no copied owner
orders, no role-specific duplicated code, no individual per-worker script.
An actual process must pass its own role index and produce its own evidence.
"""
from hierarchy_command_core import main_for_tiers

if __name__ == "__main__":
    main_for_tiers(["W","S","G","H"])
