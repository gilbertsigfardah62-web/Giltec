#!/usr/bin/env python3
"""Simple daily-life expense tracker CLI.

Features:
- Add expenses with amount, category, note, date
- List expenses with optional month/category filters
- Monthly summary and category breakdown
- Set monthly budgets and check spend vs budget
- Data persisted locally in JSON
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path.home() / ".expense_tracker"
DATA_FILE = DATA_DIR / "data.json"


@dataclass
class Expense:
    id: int
    amount: float
    category: str
    note: str
    spent_on: str  # YYYY-MM-DD
    created_at: str  # ISO datetime


@dataclass
class Budget:
    month: str  # YYYY-MM
    amount: float


def load_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return {"expenses": [], "budgets": []}
    with DATA_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_data(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def parse_date(raw: str | None) -> str:
    if not raw:
        return date.today().isoformat()
    return datetime.strptime(raw, "%Y-%m-%d").date().isoformat()


def parse_month(raw: str | None) -> str:
    if not raw:
        today = date.today()
        return f"{today.year:04d}-{today.month:02d}"
    datetime.strptime(raw, "%Y-%m")
    return raw


def cmd_add(args: argparse.Namespace) -> None:
    data = load_data()
    expenses = data["expenses"]
    next_id = (max((e["id"] for e in expenses), default=0) + 1) if expenses else 1

    expense = Expense(
        id=next_id,
        amount=round(float(args.amount), 2),
        category=args.category.strip().lower(),
        note=args.note.strip(),
        spent_on=parse_date(args.date),
        created_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
    )
    expenses.append(asdict(expense))
    save_data(data)
    print(f"Added expense #{expense.id}: ${expense.amount:.2f} [{expense.category}] on {expense.spent_on}")


def cmd_list(args: argparse.Namespace) -> None:
    data = load_data()
    month = parse_month(args.month) if args.month else None
    category = args.category.strip().lower() if args.category else None

    rows = []
    for e in data["expenses"]:
        if month and not e["spent_on"].startswith(month):
            continue
        if category and e["category"] != category:
            continue
        rows.append(e)

    if not rows:
        print("No expenses found for the selected filters.")
        return

    rows.sort(key=lambda x: (x["spent_on"], x["id"]))
    total = 0.0
    print("ID | Date       | Category      | Amount   | Note")
    print("---+------------+---------------+----------+------------------------------")
    for e in rows:
        total += e["amount"]
        print(f"{e['id']:>2} | {e['spent_on']} | {e['category'][:13]:<13} | ${e['amount']:>7.2f} | {e['note']}")
    print(f"\nTotal: ${total:.2f}")


def cmd_summary(args: argparse.Namespace) -> None:
    data = load_data()
    month = parse_month(args.month)
    monthly = [e for e in data["expenses"] if e["spent_on"].startswith(month)]

    if not monthly:
        print(f"No expenses recorded for {month}.")
        return

    total = sum(e["amount"] for e in monthly)
    by_category: dict[str, float] = defaultdict(float)
    for e in monthly:
        by_category[e["category"]] += e["amount"]

    print(f"Summary for {month}")
    print(f"Total spend: ${total:.2f}")
    print("By category:")
    for category, amount in sorted(by_category.items(), key=lambda kv: kv[1], reverse=True):
        pct = (amount / total * 100) if total else 0
        print(f"- {category}: ${amount:.2f} ({pct:.1f}%)")

    budget = next((b for b in data["budgets"] if b["month"] == month), None)
    if budget:
        remaining = budget["amount"] - total
        print(f"\nBudget: ${budget['amount']:.2f}")
        if remaining >= 0:
            print(f"Remaining: ${remaining:.2f}")
        else:
            print(f"Over budget by: ${abs(remaining):.2f}")


def cmd_set_budget(args: argparse.Namespace) -> None:
    data = load_data()
    month = parse_month(args.month)
    amount = round(float(args.amount), 2)

    budgets = data["budgets"]
    existing = next((b for b in budgets if b["month"] == month), None)
    if existing:
        existing["amount"] = amount
    else:
        budgets.append(asdict(Budget(month=month, amount=amount)))

    save_data(data)
    print(f"Budget for {month} set to ${amount:.2f}")


def cmd_export(args: argparse.Namespace) -> None:
    data = load_data()
    month = parse_month(args.month) if args.month else None
    out_path = Path(args.output)

    rows = [e for e in data["expenses"] if not month or e["spent_on"].startswith(month)]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "spent_on", "category", "amount", "note", "created_at"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} expenses to {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track daily expenses from your terminal")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add an expense")
    p_add.add_argument("amount", type=float, help="Amount spent")
    p_add.add_argument("category", help="Category (food, rent, travel, etc.)")
    p_add.add_argument("note", help="Short note")
    p_add.add_argument("--date", help="Expense date in YYYY-MM-DD (default: today)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List expenses")
    p_list.add_argument("--month", help="Filter by month YYYY-MM")
    p_list.add_argument("--category", help="Filter by category")
    p_list.set_defaults(func=cmd_list)

    p_summary = sub.add_parser("summary", help="Monthly summary")
    p_summary.add_argument("--month", help="Month in YYYY-MM (default: current month)")
    p_summary.set_defaults(func=cmd_summary)

    p_budget = sub.add_parser("set-budget", help="Set a monthly budget")
    p_budget.add_argument("amount", type=float, help="Budget amount")
    p_budget.add_argument("--month", help="Month in YYYY-MM (default: current month)")
    p_budget.set_defaults(func=cmd_set_budget)

    p_export = sub.add_parser("export", help="Export expenses to CSV")
    p_export.add_argument("output", help="Output CSV filepath")
    p_export.add_argument("--month", help="Filter export by month YYYY-MM")
    p_export.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
