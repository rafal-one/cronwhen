# cronwhen

Zero-dependency Python CLI: explain a 5-field cron expression and print its next run times.

    python3 cronwhen.py '*/15 9-17 * * mon-fri' 5

Supports lists, ranges, steps, month/day names, `@daily`-style aliases, and standard
day-of-month/day-of-week OR semantics. Tests: `python3 tests/test_cronwhen.py`.

## Support
If it saved you time: PayPal 4433@vp.pl. MIT licensed.
