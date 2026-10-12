import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime
import cronwhen as c

def test_step():
    r = c.next_runs("*/15 * * * *", datetime(2026, 1, 1, 10, 0), 3)
    assert [x.minute for x in r] == [15, 30, 45]

def test_weekday_range():
    r = c.next_runs("0 9 * * mon-fri", datetime(2026, 10, 9, 10, 0), 2)  # Fri
    assert [x.day for x in r] == [12, 13]

def test_monthly_alias():
    r = c.next_runs("@monthly", datetime(2026, 1, 15), 2)
    assert [(x.month, x.day) for x in r] == [(2, 1), (3, 1)]

def test_dom_or_dow():
    r = c.next_runs("0 0 13 * fri", datetime(2026, 10, 1), 3)
    assert r[0].day == 2 and r[1].day == 9 and r[2].day == 13

def test_bad():
    for e in ["* * *", "61 * * * *", "*/0 * * * *", "a * * * *"]:
        try: c.parse(e)
        except ValueError: continue
        raise AssertionError(e)

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("ok", n)


# --- extended pytest suite ---
import pytest


@pytest.mark.parametrize("field,expected", [
    ("7", {0}), ("5-7", {0, 5, 6}), ("0-7", set(range(7))),
    ("sun", {0}), ("mon-fri", {1, 2, 3, 4, 5}), ("*/2", {0, 2, 4, 6}),
])
def test_dow_fields(field, expected):
    assert c.parse_field(field, 4) == expected


@pytest.mark.parametrize("field,idx,expected", [
    ("jan,mar", 3, {1, 3}), ("1-5/2", 2, {1, 3, 5}), ("10/20", 0, {10, 30, 50}),
    ("0,30", 0, {0, 30}), ("*", 1, set(range(24))),
])
def test_other_fields(field, idx, expected):
    assert c.parse_field(field, idx) == expected


@pytest.mark.parametrize("expr", [
    "", "* * *", "* * * * * *", "60 * * * *", "* 24 * * *", "* * 0 * *",
    "* * * 13 * ", "* * * * 8", "5-1 * * * *", "*/0 * * * *", "*/x * * * *", "foo * * * *",
])
def test_bad_expressions(expr):
    with pytest.raises(ValueError):
        c.parse(expr)


def test_sunday_seven_runs_only_sunday():
    r = c.next_runs("0 0 * * 7", datetime(2026, 10, 12), 2)  # Mon
    assert [x.strftime("%a") for x in r] == ["Sun", "Sun"]


def test_aliases():
    assert c.next_runs("@daily", datetime(2026, 1, 1, 5), 1)[0] == datetime(2026, 1, 2)
    assert c.next_runs("@hourly", datetime(2026, 1, 1, 5, 30), 1)[0] == datetime(2026, 1, 1, 6)


def test_leap_day():
    r = c.next_runs("0 0 29 2 *", datetime(2026, 1, 1), 1)
    assert r[0] == datetime(2028, 2, 29)


def test_impossible_date_returns_empty():
    assert c.next_runs("0 0 31 2 *", datetime(2026, 1, 1), 1) == []


def test_explain():
    out = c.explain("*/30 9 * * mon")
    assert "minute: 0, 30" in out and "hour: 9" in out and "month: every" in out


def test_cli_ok(capsys):
    assert c.main(["0 9 * * *", "2"]) == 0
    out = capsys.readouterr().out
    assert "next runs:" in out and out.count("09:00") == 2


def test_cli_bad_expr(capsys):
    assert c.main(["bogus"]) == 2
    assert "error:" in capsys.readouterr().err


def test_cli_bad_count(capsys):
    assert c.main(["* * * * *", "abc"]) == 2


def test_cli_help(capsys):
    assert c.main([]) == 0
    assert "usage" in capsys.readouterr().out
