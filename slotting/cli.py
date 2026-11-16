"""`python -m slotting` runs the comparison on a synthetic warehouse."""

from __future__ import annotations

import argparse

from .layout import Layout
from .policies import assign_slots
from .simulate import average_travel, generate_orders, zipf_weights


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="slotting", description="Compare slotting and routing policies.")
    p.add_argument("--aisles", type=int, default=12)
    p.add_argument("--depth", type=int, default=20, help="pick faces per aisle")
    p.add_argument("--skus", type=int, default=200)
    p.add_argument("--orders", type=int, default=2000)
    p.add_argument("--mean-lines", type=float, default=4.0)
    p.add_argument("--zipf", type=float, default=1.0, help="demand skew exponent")
    p.add_argument("--seed", type=int, default=7)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    layout = Layout(args.aisles, args.depth)
    weights = zipf_weights(args.skus, args.zipf)
    orders = generate_orders(weights, args.orders, args.mean_lines, seed=args.seed)

    print(f"Layout: {args.aisles} aisles x {args.depth} pick faces = {len(layout.all_slots())} slots")
    print(f"SKUs: {args.skus}   orders: {args.orders}   mean lines/order: {args.mean_lines}\n")
    print(f"{'slotting':<12}{'routing':<10}{'metres/order':>14}{'vs random':>12}")

    baseline = None
    for policy in ("random", "popularity"):
        assignment = assign_slots(weights, layout, policy, seed=args.seed)
        for routing in ("return", "s_shape"):
            m = average_travel(assignment, orders, layout, routing)
            if policy == "random" and routing == "return":
                baseline = m
            change = "" if baseline is None else f"{(m - baseline) / baseline * 100:+.1f}%"
            print(f"{policy:<12}{routing:<10}{m:>14.1f}{change:>12}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
