import pytest

from slotting.layout import Layout, Slot
from slotting.routing import route_distance

LAYOUT = Layout(n_aisles=4, slots_per_aisle=20, aisle_gap_m=3.0, slot_len_m=1.2)


def test_single_pick_return_policy_is_round_trip_to_slot():
    # Aisle 0 at x=0, depth 1 at y=1.2: round trip 2 * 1.2
    assert route_distance([Slot(0, 1)], LAYOUT, "return") == pytest.approx(2.4)


def test_return_policy_two_aisles_matches_hand_calculation():
    # Front trip to aisle 2 (x=6): 2*6 = 12.
    # Aisle 0 to depth 3 (3.6 m): 2*3.6 = 7.2. Aisle 2 to depth 5 (6.0 m): 12.0.
    slots = [Slot(0, 3), Slot(2, 5), Slot(2, 2)]
    assert route_distance(slots, LAYOUT, "return") == pytest.approx(31.2)


def test_s_shape_single_aisle_is_there_and_back():
    # Traverse the full 24 m aisle, then return to the depot: 2 * 24.
    assert route_distance([Slot(0, 1)], LAYOUT, "s_shape") == pytest.approx(48.0)


def test_s_shape_two_adjacent_aisles():
    # Aisle 0: 24 m in. Cross to aisle 1 (3 m) at the back, 24 m out.
    # Return 3 m along the front. Total 54 m.
    assert route_distance([Slot(0, 1), Slot(1, 1)], LAYOUT, "s_shape") == pytest.approx(54.0)


def test_empty_order_costs_nothing():
    assert route_distance([], LAYOUT) == 0.0


def test_unknown_policy_is_rejected():
    with pytest.raises(ValueError):
        route_distance([Slot(0, 1)], LAYOUT, "nearest-neighbour")


def test_return_policy_never_exceeds_s_shape_for_one_deep_pick():
    # One shallow pick: walking only to depth 1 beats walking the whole aisle.
    slots = [Slot(0, 1)]
    assert route_distance(slots, LAYOUT, "return") < route_distance(slots, LAYOUT, "s_shape")
