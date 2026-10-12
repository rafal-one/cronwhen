#!/usr/bin/env python3
"""cronwhen: explain a 5-field cron expression and list its next run times."""
import sys
from datetime import datetime, timedelta

RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()
DAYS = "sun mon tue wed thu fri sat".split()
ALIASES = {"@hourly": "0 * * * *", "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
           "@weekly": "0 0 * * 0", "@monthly": "0 0 1 * *", "@yearly": "0 0 1 1 *",
           "@annually": "0 0 1 1 *"}


def _num(tok, idx):
    t = tok.lower()
    if idx == 3 and t in MONTHS:
        return MONTHS.index(t) + 1
    if idx == 4 and t in DAYS:
        return DAYS.index(t)
    if not t.isdigit():
        raise ValueError(f"bad value {tok!r} in {NAMES[idx]}")
    return int(t)


def parse_field(text, idx):
    lo, hi = RANGES[idx]
    out = set()
    for part in text.split(","):
        step = 1
        if "/" in part:
            part, s = part.split("/", 1)
            if not s.isdigit() or int(s) == 0:
                raise ValueError(f"bad step {s!r} in {NAMES[idx]}")
            step = int(s)
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            x, y = part.split("-", 1)
            a, b = _num(x, idx), _num(y, idx)
        else:
            a = _num(part, idx)
            b = hi if step > 1 else a
        if a < lo or b > (7 if idx == 4 else hi) or a > b:
            raise ValueError(f"{NAMES[idx]} out of range {lo}-{hi}: {text!r}")
        vals = range(a, b + 1, step)
        out.update({v % 7 for v in vals} if idx == 4 else vals)
    return out


def parse(expr):
    expr = ALIASES.get(expr.strip().lower(), expr)
    parts = expr.split()
    if len(parts) != 5:
        raise ValueError("expected 5 fields: minute hour day-of-month month day-of-week")
    sets = [parse_field(p, i) for i, p in enumerate(parts)]
    return sets, parts[2] != "*", parts[4] != "*"


def matches(spec, dt):
    sets, dom_r, dow_r = spec
    if dt.minute not in sets[0] or dt.hour not in sets[1] or dt.month not in sets[3]:
        return False
    dom_ok = dt.day in sets[2]
    dow_ok = (dt.isoweekday() % 7) in sets[4]
    if dom_r and dow_r:  # standard cron: OR when both restricted
        return dom_ok or dow_ok
    return dom_ok and dow_ok


def next_runs(expr, start, n=5):
    spec = parse(expr)
    dt = start.replace(second=0, microsecond=0) + timedelta(minutes=1)
    runs, limit = [], 366 * 5 * 24 * 60
    while len(runs) < n and limit > 0:
        if dt.month not in spec[0][3]:
            dt = (dt.replace(day=1, hour=0, minute=0) + timedelta(days=32)).replace(day=1)
            limit -= 1440
            continue
        if matches(spec, dt):
            runs.append(dt)
        dt += timedelta(minutes=1)
        limit -= 1
    return runs


def explain(expr):
    sets, _, _ = parse(expr)
    out = []
    for i, s in enumerate(sets):
        lo, hi = RANGES[i]
        if s == set(range(lo, hi + 1)):
            out.append(f"{NAMES[i]}: every")
        else:
            out.append(f"{NAMES[i]}: {', '.join(map(str, sorted(s)))}")
    return "\n".join(out)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: cronwhen.py '<cron expr>' [count]\n  e.g. cronwhen.py '*/15 9-17 * * mon-fri' 5")
        return 0
    try:
        print(explain(argv[0]))
        print("next runs:")
        for r in next_runs(argv[0], datetime.now(), int(argv[1]) if len(argv) > 1 else 5):
            print("  " + r.strftime("%a %Y-%m-%d %H:%M"))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
