# expences

Personal finance analyzer for CGD (Caixa Geral de Depósitos) bank statement PDFs.

Parses transaction data, categorizes spending, and provides an interactive TUI to browse summaries and drill down into transactions.

## Features

- Interactive TUI built with [Textual](https://textual.textualize.io/)
- Auto-discovers all statement PDFs in the directory
- Categorizes transactions into 30+ categories (Groceries, Restaurant, Uber, Rent, etc.)
- Smart subscription detection — recurring charges are identified by matching amounts across months; one-off purchases at subscription vendors (e.g. Apple Store) are classified as Shopping
- Amount-based heuristics for ambiguous transactions (Uber vs Uber Eats, generic transfers as Rent)
- Monthly breakdowns with spending/income/net
- Overall summary with super-category grouping and spending percentages
- Configurable time period (last month, 3/6/12 months, all time)
- Financial recommendations based on spending patterns
- Flags uncategorized transactions for easy pattern addition

## TUI screens

- **Dashboard** — key metrics (income, spending, net, savings rate, balance trend) with menu
- **Months** — monthly breakdown table, select a month to see its categories
- **Month detail** — categories for a single month, select to see transactions
- **Categories** — aggregated categories with period selector (default: last 3 months)
- **Transactions** — individual transactions filtered by month/category
- **Uncategorized** — transactions that need categorization
- **Recommendations** — financial advice with period selector

### Navigation

| Key | Action |
|-----|--------|
| `m` | Months (from dashboard) |
| `c` | Categories (from dashboard) |
| `u` | Uncategorized (from dashboard) |
| `r` | Recommendations (from dashboard) |
| `b` | Back one screen |
| `h` | Home (back to dashboard) |
| `q` | Quit |

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```bash
uv sync
```

## Usage

Place your CGD statement PDFs (`comprovativo_YYYYMM.pdf` or `YYYYMM.pdf`) in the project directory, then:

```bash
make          # TUI with all months
make N=3      # TUI with last 3 months
```

For the legacy CLI output:

```bash
make cli          # all months
make cli N=3      # last 3 months
```

Or directly:

```bash
uv run python tui.py              # TUI
uv run python tui.py -n 6         # TUI, last 6 months
uv run python expences.py -n 3    # CLI output
```

## Adding new categories

When new merchants appear, they show up as uncategorized in the TUI (press `u` from dashboard). Add a new entry to the `CATEGORIES` dict in `expences.py`:

```python
"COMPRAS C.DEB MERCHANT": "Category",
```

Order matters — specific patterns must come before generic catch-alls.
