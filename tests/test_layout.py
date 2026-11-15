import pytest

from slotting.layout import Layout, Slot


def test_coordinates_follow_aisle_and_depth():
    layout = Layout(n_aisles=4, slots_per_aisle=20, aisle_gap_m=3.0, slot_len_m=1.2)
    assert layout.xy(Slot(2, 5)) == pytest.approx((6.0, 6.0))


def test_single_pick_cost_is_round_trip_manhattan():
    layout = Layout(4, 20, 3.0, 1.2)
    assert layout.single_pick_cost(Slot(2, 5)) == pytest.approx(24.0)


def test_all_slots_covers_every_aisle_and_depth_once():
    layout = Layout(4, 20)
    slots = layout.all_slots()
    assert len(slots) == 80 and len(set(slots)) == 80


def test_aisle_length():
    assert Layout(4, 20, 3.0, 1.2).aisle_length_m == pytest.approx(24.0)


@pytest.mark.parametrize("kwargs", [
    dict(n_aisles=0, slots_per_aisle=5),
    dict(n_aisles=2, slots_per_aisle=0),
    dict(n_aisles=2, slots_per_aisle=2, aisle_gap_m=0),
])
def test_invalid_layouts_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Layout(**kwargs)
