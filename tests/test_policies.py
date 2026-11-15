import pytest

from slotting.layout import Layout, Slot
from slotting.policies import assign_slots
from slotting.simulate import average_travel, generate_orders, zipf_weights

LAYOUT = Layout(n_aisles=6, slots_per_aisle=15)


def test_popularity_puts_top_sku_on_cheapest_slot():
    demand = {"HOT": 100.0, "WARM": 10.0, "COLD": 1.0}
    assignment = assign_slots(demand, LAYOUT, "popularity")
    assert assignment["HOT"] == Slot(0, 1)
    assert LAYOUT.single_pick_cost(assignment["HOT"]) <= LAYOUT.single_pick_cost(assignment["COLD"])


def test_every_sku_gets_a_unique_slot():
    demand = zipf_weights(50)
    for policy in ("random", "popularity"):
        assignment = assign_slots(demand, LAYOUT, policy, seed=3)
        assert len(assignment) == 50
        assert len(set(assignment.values())) == 50


def test_random_policy_is_reproducible_with_seed():
    demand = zipf_weights(30)
    assert assign_slots(demand, LAYOUT, "random", seed=9) == assign_slots(demand, LAYOUT, "random", seed=9)


def test_too_many_skus_is_rejected():
    with pytest.raises(ValueError, match="do not fit"):
        assign_slots(zipf_weights(LAYOUT.n_aisles * LAYOUT.slots_per_aisle + 1), LAYOUT)


def test_popularity_beats_random_on_skewed_demand():
    weights = zipf_weights(60, exponent=1.0)
    orders = generate_orders(weights, n_orders=800, mean_lines=4, seed=11)
    random_map = assign_slots(weights, LAYOUT, "random", seed=11)
    popular_map = assign_slots(weights, LAYOUT, "popularity")
    assert average_travel(popular_map, orders, LAYOUT) < average_travel(random_map, orders, LAYOUT)


def test_order_generation_is_deterministic_and_well_formed():
    weights = zipf_weights(20)
    a = generate_orders(weights, 100, seed=5)
    b = generate_orders(weights, 100, seed=5)
    assert a == b
    for order in a:
        assert order, "every order has at least one line"
        assert len(order) == len(set(order)), "no SKU repeated within an order"
        assert order == sorted(order)
