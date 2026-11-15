"""Walk-distance heuristics for one pick order.

Two standard policies, both on the Layout model:

- "return": enter each aisle that holds a pick, walk to the deepest needed
  pick face and walk back out. Aisles are visited in order along the front.
- "s_shape": traverse every visited aisle end to end, alternating direction,
  then return to the depot.

Both return metres. Movement is Manhattan along aisles and cross-aisles.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .layout import Layout, Slot

POLICIES = ("return", "s_shape")


def route_distance(slots: Iterable[Slot], layout: Layout, policy: str = "return") -> float:
    slots = list(slots)
    if not slots:
        return 0.0
    if policy == "return":
        return _return_policy(slots, layout)
    if policy == "s_shape":
        return _s_shape(slots, layout)
    raise ValueError(f"unknown routing policy {policy!r}; choose from {POLICIES}")


def _return_policy(slots: list[Slot], layout: Layout) -> float:
    deepest: dict[int, int] = defaultdict(int)
    for s in slots:
        deepest[s.aisle] = max(deepest[s.aisle], s.depth)
    farthest_x = max(a for a in deepest) * layout.aisle_gap_m
    front_trip = 2 * farthest_x  # out along the front cross-aisle and back
    aisle_trips = sum(2 * d * layout.slot_len_m for d in deepest.values())
    return front_trip + aisle_trips


def _s_shape(slots: list[Slot], layout: Layout) -> float:
    visited = sorted({s.aisle for s in slots})
    length = layout.aisle_length_m
    x, y, total = 0.0, 0.0, 0.0
    at_front = True  # picker is on the front edge (y = 0)
    for aisle in visited:
        target_x = aisle * layout.aisle_gap_m
        total += abs(target_x - x)  # walk along whichever cross-aisle we are on
        x = target_x
        total += length             # traverse the full aisle
        at_front = not at_front
        y = 0.0 if at_front else length
    total += abs(x) + abs(y)        # back to the depot at (0, 0)
    return total
