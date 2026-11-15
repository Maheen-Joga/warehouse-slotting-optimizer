"""Synthetic order generation and evaluation. Standard library only.

Demand is Zipf-shaped: a few SKUs are picked very often, most rarely. That is
the realistic case, and it is where popularity-based slotting pays off.
"""

from __future__ import annotations

import math
import random
from typing import Mapping

from .layout import Layout, Slot
from .routing import route_distance


def zipf_weights(n_skus: int, exponent: float = 1.0) -> dict[str, float]:
    return {f"SKU{i + 1:04d}": 1.0 / (i + 1) ** exponent for i in range(n_skus)}


def _poisson(rng: random.Random, lam: float) -> int:
    # Knuth's method; fine for the small lambdas used for order lines.
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def generate_orders(
    weights: Mapping[str, float],
    n_orders: int,
    mean_lines: float = 4.0,
    seed: int = 0,
) -> list[list[str]]:
    """Each order is the list of distinct SKUs it picks."""
    rng = random.Random(seed)
    skus = list(weights)
    w = [weights[s] for s in skus]
    orders = []
    for _ in range(n_orders):
        n_lines = max(1, _poisson(rng, mean_lines))
        picked = set(rng.choices(skus, weights=w, k=n_lines))
        orders.append(sorted(picked))
    return orders


def average_travel(
    assignment: Mapping[str, Slot],
    orders: list[list[str]],
    layout: Layout,
    routing: str = "return",
) -> float:
    """Mean walk distance (metres) per order under an assignment and routing policy."""
    if not orders:
        raise ValueError("no orders to evaluate")
    total = 0.0
    for order in orders:
        slots = [assignment[sku] for sku in order if sku in assignment]
        total += route_distance(slots, layout, routing)
    return total / len(orders)
