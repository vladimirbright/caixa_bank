# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal finance analyzer that parses CGD (Caixa Geral de Depósitos) bank statement PDFs, categorizes transactions, and generates monthly/overall summaries with financial recommendations.

## Commands

- `make` — run the script (all months)
- `make N=3` — run for last N months only
- `uv run expences.py -n 5` — direct invocation with args

Uses **uv** for dependency management (not poetry).

## Architecture

Single-file script (`expences.py`) with this flow:

1. **PDF discovery** — `discover_pdfs()` finds all `*.pdf` files in the directory
2. **Extraction** — `extract_transactions()` uses PyMuPDF to parse transaction lines from CGD statement PDFs via regex
3. **Categorization** — `categorize_transaction()` matches transaction descriptions against the `CATEGORIES` dict (order matters — first match wins, so specific patterns must come before generic catch-alls like `"COMPRAS C.DEB": "Unknown"` and `"TFI": "Transfers"`)
4. **Reporting** — `categorize()` prints per-month breakdowns; `print_overall_summary()` aggregates across months with super-category grouping and `print_recommendations()` generates financial advice

### Key design details

- `CATEGORIES` is an ordered dict mapping description substrings to category names. Matching is case-insensitive. The Uber/Uber Eats split uses amount threshold (> €15 = Uber Eats)
- `SUPER_CATEGORIES` groups categories into higher-level groups (Transportation, Essentials, Dining out, etc.) for the overall summary
- Amounts use `Decimal` throughout (parsed from Portuguese format: dots as thousands separators, commas as decimal)
- Uncategorized transactions are printed with details so new patterns can be identified and added
- PDF filenames can be either `comprovativo_YYYYMM.pdf` or `YYYYMM.pdf`

## Style

- Max line length: 120 (`.flake8`)
