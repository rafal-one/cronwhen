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
