"""Slotting policies: decide which SKU goes in which pick face.

- "random": shuffle SKUs over slots (the baseline most warehouses start from).
- "popularity": highest-demand SKUs get the slots with the lowest single-pick cost
  (closest to the depot). This is the ABC / velocity-based idea used in practice.
"""

from __future__ import annotations

import random
from typing import Mapping

from .layout import Layout, Slot

POLICIES = ("random", "popularity")


def assign_slots(
    demand: Mapping[str, float],
    layout: Layout,
    policy: str = "popularity",
    seed: int | None = None,
) -> dict[str, Slot]:
    if len(demand) > len(layout.all_slots()):
        raise ValueError(
            f"{len(demand)} SKUs do not fit in {len(layout.all_slots())} slots"
        )
    if policy == "random":
        slots = layout.all_slots()
        random.Random(seed).shuffle(slots)
        skus = list(demand)
        return dict(zip(skus, slots))
    if policy == "popularity":
        ranked_skus = sorted(demand, key=lambda s: (-demand[s], s))
        ranked_slots = sorted(layout.all_slots(), key=layout.single_pick_cost)
        return dict(zip(ranked_skus, ranked_slots))
    raise ValueError(f"unknown slotting policy {policy!r}; choose from {POLICIES}")
