# Daily Expense Tracker (CLI)

A practical, lightweight expense tracker you can use every day from your terminal.

## What it does
- Add expenses in seconds
- Organize by category
- See monthly totals and category breakdowns
- Set a monthly budget
- Export your data to CSV

## Quick start
```bash
python3 expense_tracker.py --help
```

### Add expenses
```bash
python3 expense_tracker.py add 7.5 food "Coffee and bagel"
python3 expense_tracker.py add 42 travel "Fuel" --date 2026-05-04
```

### List expenses
```bash
python3 expense_tracker.py list
python3 expense_tracker.py list --month 2026-05
python3 expense_tracker.py list --category food
```

### Monthly summary
```bash
python3 expense_tracker.py summary
python3 expense_tracker.py summary --month 2026-05
```

### Set a budget
```bash
python3 expense_tracker.py set-budget 1200 --month 2026-05
```

### Export to CSV
```bash
python3 expense_tracker.py export expenses_may.csv --month 2026-05
```

## Data storage
Data is stored locally at:

`~/.expense_tracker/data.json`

No cloud account needed.

## Daily-life usage tips
- Use simple categories: `food`, `transport`, `bills`, `shopping`, `health`, `fun`.
- Enter expenses immediately after purchase.
- Review `summary` once a week.
- Keep one monthly budget and adjust categories as you learn your spending habits.
