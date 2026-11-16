from slotting.cli import main


def test_cli_prints_comparison_table(capsys):
    assert main(["--aisles", "4", "--depth", "10", "--skus", "30", "--orders", "100"]) == 0
    out = capsys.readouterr().out
    assert "metres/order" in out
    assert "popularity" in out and "random" in out
    assert "backtest" in out
