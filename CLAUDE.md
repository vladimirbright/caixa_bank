# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal finance analyzer that parses CGD (Caixa Geral de Depósitos) bank statement PDFs, categorizes transactions, and provides an interactive TUI to browse summaries and drill down into transactions.

## Commands

- `make` — launch TUI (all months)
- `make N=3` — launch TUI for last N months only
- `make cli` — legacy CLI output (all months)
- `make cli N=3` — legacy CLI output for last N months
- `uv run python tui.py -n 5` — direct TUI invocation with args
- `uv run python expences.py -n 5` — direct CLI invocation with args

Uses **uv** for dependency management (not poetry).

## Architecture

Two main files:

- **`expences.py`** — pure data logic (no presentation)
- **`tui.py`** — Textual TUI app with screens

### expences.py data flow

1. **PDF discovery** — `discover_pdfs()` finds all `*.pdf` files in the directory
2. **Extraction** — `extract_transactions()` uses PyMuPDF to parse transaction lines from CGD statement PDFs via regex
3. **Recurring detection** — `compute_recurring_amounts()` scans all transactions to find subscription amounts that appear 2+ times; one-off purchases at subscription vendors get reclassified as Shopping
4. **Categorization** — `categorize_transaction()` matches descriptions against `CATEGORIES` dict (order matters — first match wins)
5. **Aggregation** — `load_transactions()` returns monthly groups + recurring amounts; `compute_monthly_stats()` and `compute_overall_stats()` produce structured data dicts
6. **CLI** — `main()` provides legacy CLI output using tabulate

### tui.py screens

7 screens with push/pop navigation:
- **DashboardScreen** — key metrics + clickable menu (m/c/u/r/q keybindings)
- **MonthsScreen** — DataTable of months (descending), select row to drill down
- **MonthDetailScreen** — categories for one month, sorted by abs amount descending
- **CategoriesScreen** — aggregated categories with period selector (default: last 3 months)
- **TransactionsScreen** — individual transactions filtered by month/category/period
- **UncategorizedScreen** — uncategorized transactions
- **RecommendationsScreen** — financial advice with period selector (default: last 3 months)

Navigation: `b` = back, `h` = home (dashboard), `q` = quit.

### Key design details

- `CATEGORIES` is an ordered dict mapping description substrings to category names. Matching is case-insensitive
- Amount-based heuristics: Uber > €15 = Uber Eats; transfers €1,400–€1,500 = Rent
- Subscription validation: amounts must appear 2+ times across all history; one-offs become Shopping
- `recurring_amounts` is computed once from all transactions (before month slicing) and threaded through categorize/stats functions
- `SUPER_CATEGORIES` groups categories into higher-level groups (Transportation, Essentials, Dining out, etc.)
- Amounts use `Decimal` throughout (parsed from Portuguese format: dots as thousands separators, commas as decimal)
- PDF filenames can be either `comprovativo_YYYYMM.pdf` or `YYYYMM.pdf`
- CategoriesScreen and RecommendationsScreen have a period selector (1/3/6/12 months or all time), default 3 months
- `_filter_by_period()` in tui.py recomputes stats for the selected period on the fly

## Style

- Max line length: 120 (`.flake8`)
