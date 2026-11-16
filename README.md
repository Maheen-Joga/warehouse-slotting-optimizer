# warehouse-slotting-optimizer

Where you put each SKU decides how far pickers walk. This project compares slotting and
routing policies on a simulated warehouse, and backtests a simple demand forecast that
can feed the slotting decision.

Standard library only. Synthetic data only.

```bash
pip install -e ".[dev]"
python -m slotting            # or: slotting --aisles 12 --depth 20 --seed 7
pytest
```

## Results (default run: 12 aisles × 20 pick faces, 200 SKUs, 2,000 orders, seed 7)

| Slotting | Routing | Metres per order | vs random |
|---|---|---:|---:|
| random | return | 138.9 | baseline |
| random | s-shape | 140.6 | +1.2% |
| popularity | return | 65.3 | −53.0% |
| popularity | s-shape | 98.9 | −28.8% |

Popularity slotting puts the highest-demand SKUs on the pick faces closest to the depot.
The gain is largest under the return policy, because the most common picks get the
shortest round trip.

Demand forecast backtest (last 4 weeks, one-step-ahead, mean absolute error in picks per week):

| Method | MAE (seed 7) | MAE, five other seeds |
|---|---:|---|
| naive (last week) | 4.66 | 4.50–4.96 |
| EWMA, α = 0.3 | 3.65 | 3.46–3.86 |
| Holt linear trend | 3.99 | 3.69–4.28 |

On this synthetic history, EWMA beat both naive and Holt on all six seeds. Holt's trend
estimate adds variance when the trend is small, so the simpler smoother won. This is a
finding about this data, not a general claim. Real demand with a stronger trend or
seasonality could change the ranking, so re-run the backtest on your own history.

## Model and assumptions

- **Layout.** Parallel aisles. The depot sits at the front cross-aisle, and each aisle has
  one pick face per depth step. There are no bays, levels or two-sided aisles, which
  keeps the model small enough to read.
- **Routing.** Two standard heuristics. *Return*: enter each aisle with a pick, walk to
  the deepest pick face, walk back. *S-shape*: traverse each visited aisle end to end,
  alternating direction, then return to the depot. Both measure Manhattan distance in
  metres, not time.
- **Slotting.** *Random* is the baseline. *Popularity* ranks SKUs by demand and assigns
  them to slots in order of single-pick cost (closest to the depot first).
- **Demand.** Zipf-shaped popularity (a few SKUs picked often, most rarely). Order lines are
  Poisson, and each order picks distinct SKUs.

## What this does not model

- Travel time, congestion, picker speed, or pick time per line
- Heavy or bulky items, cube, or weight constraints
- Replenishment, slot capacity, or moving stock between slots
- Real warehouse data. The numbers come from the synthetic generator and should not be
  read as a warehouse's expected savings.

## Using it on your own data

```python
from slotting import Layout, assign_slots, average_travel, generate_orders
from slotting.forecast import backtest_forecast

layout = Layout(n_aisles=10, slots_per_aisle=25)
demand = {"SKU-1": 540.0, "SKU-2": 12.0}          # e.g. forecast picks per week
assignment = assign_slots(demand, layout, "popularity")
```

`demand` can be any mapping of SKU to expected picks. A forecast fits directly, and the
backtest helps you choose between naive, smoothing and trend methods on your history.

## Project layout

```
slotting/
  layout.py     aisles, pick faces, coordinates, single-pick cost
  routing.py    return and s-shape walk distance
  policies.py   random and popularity slotting
  forecast.py   naive, EWMA and Holt backtests
  simulate.py   Zipf demand, Poisson orders, average travel
  cli.py        comparison table and forecast backtest
tests/          27 tests: layout, hand-checked route distances, slotting, forecasts, CLI
```

## License

MIT
