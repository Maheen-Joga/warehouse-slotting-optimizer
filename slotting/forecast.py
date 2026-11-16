"""One-step demand forecasting, backtested on a holdout window.

Three methods on the same rolling evaluation:

- "naive":  next period equals this period (the floor any model must beat).
- "ewma":   exponentially weighted moving average, a level-only smoother.
- "holt":   Holt's linear trend method (level + trend), for trending demand.

Each method is refit on the training part, then rolled forward through the
holdout with the actual values fed back in, so every error is a genuine
one-step-ahead forecast.
"""

from __future__ import annotations

from typing import Mapping, Sequence

METHODS = ("naive", "ewma", "holt")


def ewma_forecast(series: Sequence[float], alpha: float = 0.3) -> float:
    """Next-period EWMA forecast after consuming the whole series."""
    if not series:
        raise ValueError("series must not be empty")
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0, 1]")
    level = float(series[0])
    for value in series[1:]:
        level = alpha * float(value) + (1 - alpha) * level
    return level


def _holt_init(series: Sequence[float], alpha: float, beta: float) -> tuple[float, float]:
    level, trend = float(series[0]), float(series[1]) - float(series[0])
    for value in series[1:]:
        prev_level = level
        level = alpha * float(value) + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
    return level, trend


def backtest_forecast(
    history: Mapping[str, Sequence[float]],
    holdout: int = 4,
    alpha: float = 0.3,
    beta: float = 0.1,
) -> dict[str, float]:
    """Mean absolute one-step error per method over the holdout, averaged across SKUs."""
    errors: dict[str, list[float]] = {m: [] for m in METHODS}
    for series in history.values():
        if len(series) < holdout + 2:
            raise ValueError("each series needs at least holdout + 2 points")
        train, test = series[:-holdout], series[-holdout:]

        ewma_level = float(train[0])
        for value in train[1:]:
            ewma_level = alpha * float(value) + (1 - alpha) * ewma_level
        holt_level, holt_trend = _holt_init(train, alpha, beta)
        last = float(train[-1])

        for actual in test:
            actual = float(actual)
            errors["naive"].append(abs(last - actual))
            errors["ewma"].append(abs(ewma_level - actual))
            errors["holt"].append(abs(holt_level + holt_trend - actual))

            ewma_level = alpha * actual + (1 - alpha) * ewma_level
            prev_level = holt_level
            holt_level = alpha * actual + (1 - alpha) * (holt_level + holt_trend)
            holt_trend = beta * (holt_level - prev_level) + (1 - beta) * holt_trend
            last = actual

    return {f"{m}_mae": sum(v) / len(v) for m, v in errors.items()}
