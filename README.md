# warehouse-slotting-optimizer

Where you put each SKU decides how far pickers walk. This project compares
slotting and routing policies on a simulated warehouse.

Standard library only. Synthetic data only.

**Status: early development.** Built in small steps; checked items exist and are tested.

- [x] Layout model: aisles, pick faces, coordinates
- [x] Pick routing: return and s-shape walk distance
- [x] Slotting policies (random, popularity) and synthetic order simulation
- [x] Command-line comparison of policies
- [ ] Demand forecast backtest (naive, EWMA, Holt)
- [ ] Results write-up and assumptions

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
