import pytest

from slotting.forecast import backtest_forecast, ewma_forecast


def test_ewma_of_constant_series_is_the_constant():
    assert ewma_forecast([7, 7, 7, 7], alpha=0.5) == pytest.approx(7.0)


def test_ewma_rejects_bad_inputs():
    with pytest.raises(ValueError):
        ewma_forecast([])
    with pytest.raises(ValueError):
        ewma_forecast([1, 2], alpha=0)


def test_backtest_is_zero_error_on_constant_history():
    scores = backtest_forecast({"A": [5] * 12}, holdout=4)
    assert scores == {"naive_mae": 0.0, "ewma_mae": 0.0, "holt_mae": 0.0}


def test_backtest_reports_all_methods():
    scores = backtest_forecast({"A": list(range(1, 14))}, holdout=4)
    assert set(scores) == {"naive_mae", "ewma_mae", "holt_mae"}


def test_backtest_needs_enough_history():
    with pytest.raises(ValueError):
        backtest_forecast({"A": [1, 2, 3]}, holdout=4)


def test_holt_tracks_a_clean_linear_trend_better_than_naive():
    series = {"A": [10 + 2 * t for t in range(20)]}
    scores = backtest_forecast(series, holdout=6)
    assert scores["holt_mae"] < scores["naive_mae"]
