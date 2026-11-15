"""A simple picking layout: parallel aisles, one pick face per depth step.

Coordinates: the depot sits at (0, 0) on the front cross-aisle. Aisle `a` runs
at x = a * aisle_gap_m. Depth `d` (1..slots_per_aisle) sits at y = d * slot_len_m.
This is a deliberately small model: one pick face per depth, no bays or levels.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Slot:
    aisle: int   # 0-based aisle index
    depth: int   # 1-based pick face depth along the aisle

    def __str__(self) -> str:
        return f"A{self.aisle:02d}-D{self.depth:02d}"


@dataclass(frozen=True)
class Layout:
    n_aisles: int
    slots_per_aisle: int
    aisle_gap_m: float = 3.0
    slot_len_m: float = 1.2

    def __post_init__(self):
        if self.n_aisles < 1 or self.slots_per_aisle < 1:
            raise ValueError("layout needs at least one aisle and one slot per aisle")
        if self.aisle_gap_m <= 0 or self.slot_len_m <= 0:
            raise ValueError("distances must be positive")

    @property
    def aisle_length_m(self) -> float:
        return self.slots_per_aisle * self.slot_len_m

    def xy(self, slot: Slot) -> tuple[float, float]:
        return slot.aisle * self.aisle_gap_m, slot.depth * self.slot_len_m

    def all_slots(self) -> list[Slot]:
        return [Slot(a, d) for a in range(self.n_aisles) for d in range(1, self.slots_per_aisle + 1)]

    def single_pick_cost(self, slot: Slot) -> float:
        """Round-trip walk from the depot to one slot and back (return policy)."""
        x, y = self.xy(slot)
        return 2 * (x + y)
