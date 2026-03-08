# expences

Personal finance analyzer for CGD (Caixa Geral de Depósitos) bank statement PDFs.

Parses transaction data, categorizes spending, and generates monthly summaries with financial recommendations.

## Features

- Auto-discovers all statement PDFs in the directory
- Categorizes transactions into 30+ categories (Groceries, Restaurant, Uber, Rent, etc.)
- Monthly breakdowns with spending/income/net
- Overall summary with super-category grouping and spending percentages
- Monthly savings rate trend
- Financial recommendations based on spending patterns
- Flags uncategorized transactions for easy pattern addition

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```bash
uv sync
```

## Usage

Place your CGD statement PDFs (`comprovativo_YYYYMM.pdf` or `YYYYMM.pdf`) in the project directory, then:

```bash
make          # all months
make N=3      # last 3 months
```

Or directly:

```bash
uv run expences.py
uv run expences.py -n 6
uv run expences.py /path/to/statements -n 3
```

## Adding new categories

When new merchants appear, they show up as uncategorized in the output. Add a new entry to the `CATEGORIES` dict in `expences.py`:

```python
"COMPRAS C.DEB MERCHANT": "Category",
```

Order matters — specific patterns must come before generic catch-alls.
