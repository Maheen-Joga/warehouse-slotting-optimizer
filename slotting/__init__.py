"""warehouse-slotting-optimizer: where to put SKUs so pickers walk less."""

from .layout import Layout, Slot
from .policies import assign_slots
from .routing import route_distance
from .forecast import ewma_forecast, backtest_forecast
from .simulate import generate_orders, average_travel

__all__ = [
    "Layout", "Slot", "assign_slots", "route_distance",
    "ewma_forecast", "backtest_forecast", "generate_orders", "average_travel",
]
__version__ = "0.1.0"
