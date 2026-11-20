"""Directors D01–D10 in every root share this one executable.

This file is intentionally a tiny shared-role entrypoint: no copied owner
orders, no role-specific duplicated code, no individual per-worker script.
An actual process must pass its own role index and produce its own evidence.
"""
from hierarchy_command_core import main_for_tiers

if __name__ == "__main__":
    main_for_tiers(["D"])
