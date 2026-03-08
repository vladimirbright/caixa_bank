import glob
import os
import re
from datetime import date
from decimal import Decimal
from collections import defaultdict, Counter
from itertools import groupby

import fitz  # PyMuPDF


CATEGORIES = {
    # Transportation - Rides
    "COMPRAS C.DEB UBER": "Uber",
    "COMPRAS C.DEB UBR PE": "Uber",
    "COMPRAS C.DEB BOLT.EU": "Bolt",

    # Transportation - Public
    "COMPRA CP CAIS SODRE": "Trains",
    "COMPRA CP SAO PEDRO": "Trains",
    "COMPRA CARREGAMENTO": "Trains",
    "COMPRA VIVA MERCHANT": "Trains",
    "COMPRA ALBUFEIRA": "Trains",

    # Groceries
    "COMPRAS C.DEB FRESCUR": "Groceries",
    "WWW.CONTINENTE": "Groceries",
    "COMPRAS C.DEB CONTINE": "Groceries",
    "COMPRA CONTINENTE": "Groceries",
    "COMPRA VASQUES GARC": "Groceries",  # Talho
    "COMPRAS C.DEB PINGO D": "Groceries",
    "COMPRAS C.DEB NESTLE": "Groceries",
    "COMPRAS C.DEB ATALHO": "Groceries",
    "COMPRAS C.DEB EL CORT": "Groceries",
    "COMPRAS C.DEB GAYO-YA": "Groceries",
    "COMPRAS C.DEB AROIOS": "Groceries",
    "COMPRA LIDL AGRADECE": "Groceries",
    "COMPRAS C.DEB LIDL AG": "Groceries",
    "COMPRA ALDI": "Groceries",
    "COMPRAS C.DEB ALDI CA": "Groceries",
    "COMPRA OVOS DO MELO": "Groceries",
    "COMPRA CAMPO DE OURIQ": "Groceries",
    "COMPRAS C.DEB SUPERME": "Groceries",
    "COMPRAS C.DEB GLEBA O": "Groceries",
    "COMPRAS C.DEB GLEBA N": "Groceries",
    "COMPRAS C.DEB GLEBA": "Groceries",
    "COMPRA GLEBA NOSSA": "Groceries",
    "COMPRA PINGO DOCE": "Groceries",
    "COMPRA SUPERMERC": "Groceries",
    "COMPRA EL CORTE INGLE": "Groceries",
    "COMPRAS C.DEB AUCHAN": "Groceries",
    "COMPRAS C.DEB MY AUCH": "Groceries",
    "COMPRAS C.DEB CELEIRO": "Groceries",
    "COMPRAS C.DEB MERC CA": "Groceries",
    "COMPRAS C.DEB MINIPRE": "Groceries",
    "COMPRAS C.DEB TALHO N": "Groceries",
    "COMPRAS C.DEB TALHO A": "Groceries",
    "COMPRAS C.DEB POLVO M": "Groceries",
    "COMPRAS C.DEB FRUTOS": "Groceries",
    "COMPRAS C.DEB MEUSUPE": "Groceries",
    "COMPRAS C.DEB SUPER M": "Groceries",
    "COMPRAS C.DEB SPAR AL": "Groceries",
    "COMPRAS C.DEB CONTIN": "Groceries",
    "COMPRAS C.DEB FRESCO": "Groceries",
    "COMPRAS C.DEB CONSUMA": "Groceries",
    "COMPRAS C.DEB GRANOS": "Groceries",
    "COMPRAS C.DEB QUALIDA": "Groceries",

    # Home
    "COMPRA IKEA PORTUGAL": "Home goods",
    "COMPRAS C.DEB IKEA AL": "Home goods",
    "COMPRAS C.DEB IKEA PO": "Home goods",
    "COMPRAS C.DEB LEROY M": "Home goods",
    "COMPRAS C.DEB CASA DO": "Home goods",
    "COMPRAS C.DEB NATURA": "Home goods",
    "COMPRAS C.DEB MAISON": "Home goods",

    # Tech & Electronics
    "COMPRA WORTEN-EQUIPAM": "Tech",
    "COMPRAS C.DEB WORTEN": "Tech",
    "COMPRAS C.DEB FNAC AM": "Tech",
    "COMPRAS C.DEB FNAC VA": "Tech",

    # Amazon / Online shopping
    "COMPRAS C.DEB AMZN": "Amazon",
    "COMPRA CTT - CORREIO": "Amazon",
    "COMPRAS C.DEB WWW.AMA": "Amazon",
    "COMPRAS C.DEB AMAZON": "Amazon",

    # Subscriptions
    "COMPRAS C.DEB NETFLIX": "Subscriptions",
    "COMPRAS C.DEB APPLE.C": "Subscriptions",
    "COMPRAS C.DEB VODAFON": "Subscriptions",
    "COMPRAS C.DEB CLOUDFL": "Subscriptions",
    "COMPRAS C.DEB KINDLE": "Subscriptions",
    "COMPRAS C.DEB IYZICO": "Subscriptions",

    # Games
    "COMPRAS C.DEB MICROSO": "Games",

    # Cafe & Bakery
    "COMPRAS C.DEB POPPY": "Cafe",
    "COMPRAS C.DEB CAFE MA": "Cafe",
    "COMPRAS C.DEB FAUNA": "Cafe",
    "COMPRAS C.DEB DEJAVU": "Cafe",
    "COMPRAS C.DEB SANTINI": "Cafe",
    "COMPRAS C.DEB PADARIA": "Cafe",
    "COMPRAS C.DEB AREAS P": "Cafe",
    "COMPRA POPPY PATISSER": "Cafe",
    "COMPRA PASTELARIA MAR": "Cafe",
    "COMPRAS C.DEB BARISTA": "Cafe",
    "COMPRAS C.DEB JERONYM": "Cafe",
    "COMPRAS C.DEB THE COF": "Cafe",
    "COMPRA THE COFFEE": "Cafe",
    "COMPRAS C.DEB STARBUC": "Cafe",
    "COMPRAS C.DEB CAFE DO": "Cafe",
    "COMPRAS C.DEB CAFE PA": "Cafe",
    "COMPRAS C.DEB CAF SUN": "Cafe",
    "COMPRAS C.DEB CONFEIT": "Cafe",
    "COMPRAS C.DEB GELADOS": "Cafe",
    "COMPRAS C.DEB SANTI B": "Cafe",
    "COMPRAS C.DEB LEONIDA": "Cafe",
    "COMPRAS C.DEB TEA SHO": "Cafe",
    "COMPRAS C.DEB FABRICA": "Cafe",
    "COMPRAS C.DEB POPBAR": "Cafe",

    # Restaurant
    "COMPRAS C.DEB CHAPITO": "Restaurant",
    "COMPRAS C.DEB PILS": "Restaurant",
    "COMPRAS C.DEB SUMAYA": "Restaurant",
    "COMPRA EMBAIXADA FED": "Restaurant",
    "COMPRA MCDONALDS": "Restaurant",
    "COMPRA MCDONALD S": "Restaurant",
    "COMPRAS C.DEB MCDONAL": "Restaurant",
    "COMPRAS C.DEB MC DONA": "Restaurant",
    "COMPRAS C.DEB MACDONA": "Restaurant",
    "COMPRAS C.DEB HAMBURG": "Restaurant",
    "COMPRAS C.DEB KITCHEN": "Restaurant",
    "COMPRAS C.DEB REST MC": "Restaurant",
    "COMPRAS C.DEB REST CA": "Restaurant",
    "COMPRAS C.DEB REST MO": "Restaurant",
    "COMPRAS C.DEB REST LU": "Restaurant",
    "COMPRAS C.DEB REST BL": "Restaurant",
    "COMPRAS C.DEB REST PA": "Restaurant",
    "COMPRAS C.DEB REST VI": "Restaurant",
    "COMPRAS C.DEB REST SU": "Restaurant",
    "COMPRAS C.DEB REST SE": "Restaurant",
    "COMPRAS C.DEB REST AC": "Restaurant",
    "COMPRAS C.DEB REST DH": "Restaurant",
    "COMPRAS C.DEB RES VER": "Restaurant",
    "COMPRAS C.DEB RES MER": "Restaurant",
    "COMPRAS C.DEB HUMMUS": "Restaurant",
    "COMPRAS C.DEB CERVEJA": "Restaurant",
    "COMPRAS C.DEB BAR CEN": "Restaurant",
    "COMPRAS C.DEB SEA ME": "Restaurant",
    "COMPRAS C.DEB EMPANAD": "Restaurant",
    "COMPRAS C.DEB O MEXIL": "Restaurant",
    "COMPRAS C.DEB BURGUER": "Restaurant",
    "COMPRAS C.DEB MOULES": "Restaurant",
    "COMPRAS C.DEB TEXAS G": "Restaurant",
    "COMPRAS C.DEB HOT DOG": "Restaurant",
    "COMPRAS C.DEB MUSTARD": "Restaurant",
    "COMPRAS C.DEB VESUVIA": "Restaurant",
    "COMPRAS C.DEB PICCOLO": "Restaurant",
    "COMPRAS C.DEB ROZZA V": "Restaurant",
    "COMPRAS C.DEB DEGRAZI": "Restaurant",
    "COMPRAS C.DEB SPUTNIK": "Restaurant",
    "COMPRAS C.DEB KHOB KH": "Restaurant",
    "COMPRAS C.DEB DIM SUM": "Restaurant",
    "COMPRAS C.DEB VEGAN J": "Restaurant",
    "COMPRAS C.DEB JHOL MO": "Restaurant",
    "COMPRAS C.DEB BON VIV": "Restaurant",
    "COMPRAS C.DEB PETISCA": "Restaurant",
    "COMPRAS C.DEB NOORI M": "Restaurant",
    "COMPRAS C.DEB TEMPERO": "Restaurant",
    "COMPRAS C.DEB ADEGA Q": "Restaurant",
    "COMPRAS C.DEB SINGH E": "Restaurant",
    "COMPRAS C.DEB NECO S": "Restaurant",
    "COMPRAS C.DEB PEPE JE": "Restaurant",
    "COMPRAS C.DEB SALTA": "Restaurant",
    "COMPRAS C.DEB SANTO G": "Restaurant",
    "COMPRAS C.DEB O TACHI": "Restaurant",
    "COMPRAS C.DEB SELVA C": "Restaurant",
    "COMPRAS C.DEB NEXT RO": "Restaurant",
    "COMPRAS C.DEB PEPPERI": "Restaurant",
    "COMPRAS C.DEB FRIGIDE": "Restaurant",
    "COMPRAS C.DEB SIMIT S": "Restaurant",
    "COMPRAS C.DEB TAYA YO": "Restaurant",
    "COMPRAS C.DEB WINE AN": "Restaurant",
    "COMPRAS C.DEB OYSTER": "Restaurant",
    "COMPRAS C.DEB MARIACH": "Restaurant",
    "COMPRAS C.DEB SHAH AL": "Restaurant",
    "COMPRAS C.DEB THE HOT": "Restaurant",
    "COMPRA HELLO SEOUL": "Restaurant",
    "COMPRA TALHO ARGENTIN": "Restaurant",
    "COMPRAS C.DEB JIANZHE": "Restaurant",
    "COMPRA JIANZHEN CHEN": "Restaurant",
    "COMPRA CHEN JIANZHEN": "Restaurant",
    "COMPRA CHEN JINGQIANG": "Restaurant",

    # Clothes
    "COMPRAS C.DEB NIKE": "Clothes",
    "COMPRAS C.DEB ASOS.CO": "Clothes",
    "COMPRAS C.DEB ZARA HO": "Clothes",
    "COMPRAS C.DEB ZARA": "Clothes",
    "COMPRAS C.DEB ZARAHOM": "Clothes",
    "COMPRAS C.DEB SPORT Z": "Clothes",
    "COMPRAS C.DEB ADIDASP": "Clothes",
    "COMPRAS C.DEB UNIQLO": "Clothes",
    "COMPRAS C.DEB UNDERAR": "Clothes",
    "COMPRAS C.DEB QUIKSIL": "Clothes",
    "COMPRAS C.DEB JD SPOR": "Clothes",
    "COMPRAS C.DEB SKECHER": "Clothes",
    "COMPRAS C.DEB SEZANE": "Clothes",
    "COMPRAS C.DEB BLUEJEA": "Clothes",
    "COMPRA LA REDOUTE POR": "Clothes",
    "COMPRAS C.DEB LA REDO": "Clothes",

    # Gym & Fitness
    "TRF MBWAY 913xxx401": "Gym",
    "COMPRAS C.DEB SUNSETF": "Gym",
    "Rounds": "Gym",

    # Leisure & Outings
    "COMPRAS C.DEB MARINHA": "Leisure",
    "COMPRAS C.DEB MUSEU": "Leisure",
    "COMPRAS C.DEB FEVER": "Leisure",
    "COMPRAS C.DEB QUIOSQU": "Leisure",
    "COMPRA FUND CALOUSTE": "Leisure",
    "COMPRAS C.DEB F CALOU": "Leisure",
    "COMPRAS C.DEB BILHETE": "Leisure",
    "COMPRAS C.DEB 39 BILH": "Leisure",
    "COMPRAS C.DEB MUS NAC": "Leisure",
    "COMPRAS C.DEB EPIC SA": "Leisure",
    "COMPRA PARQUES DE SIN": "Leisure",
    "COMPRA COLEGIO MILITA": "Leisure",
    "COMPRAS C.DEB MONSANT": "Leisure",
    "COMPRAS C.DEB QUISOQU": "Leisure",

    # Cleaning
    "COMPRAS C.DEB OSCAR": "Cleaning",

    # Bank Fees
    "MANUT CONTA PACOTE CAIXA": "Bank fees",
    "COMISSAO COMPRAS": "Bank fees",
    "IMPOSTO SELO S": "Bank fees",

    # Bills & Utilities
    "EDP COMERCIAL": "Utilities",
    "MEO": "Utilities",
    "FIDELIDADE": "Insurance",

    # Rent
    "TFI Manuel Teixeira": "Rent",
    "TFI MANUEL TEIXEIRA": "Rent",

    # Services / misc payments
    "ALMOUROLTEC": "Tech",
    "HIPAY": "Subscriptions",
    "COMPRA EUPAGO": "Subscriptions",

    # Taxes
    "I G F S": "Taxes",
    "INST GEST": "Taxes",
    "ANUL PAG 10095 PAG-ES": "Taxes",
    "INSTITUTO DE GESTAO": "Taxes",
    "PAG 10095 PAG-ESTADO": "Taxes",

    # Cash Withdrawal
    "LEVANTAMENTO": "Withdrawal",
    "LEV": "Withdrawal",

    # Health
    "COMPRA FARMACIA": "Health",
    "COMPRAS C.DEB FARMACI": "Health",
    "COMPRA LASERLAB": "Health",
    "COMPRA HOSPITAL DA LU": "Health",
    "COMPRAS C.DEB HOSP LU": "Health",
    "COMPRAS C.DEB SAMS HO": "Health",
    "COMPRA SAMS HOSPITAL": "Health",
    "COMPRAS C.DEB HSP MER": "Health",

    # Car
    "COMPRA BOL": "Car",  # Boleia / fuel
    "COMPRA POSTO GALP": "Car",
    "COMPRAS C.DEB POSTO R": "Car",
    "COMPRAS C.DEB REPSOL": "Car",
    "COMPRAS C.DEB RENTALC": "Car",
    "COMPRAS C.DEB CARS ON": "Car",

    # Shopping (misc)
    "COMPRA SILAU": "Shopping",
    "COMPRA GRUPO CASTILHO": "Shopping",
    "COMPRA MY AUC": "Shopping",
    "COMPRAS C.DEB RECORD": "Shopping",
    "COMPRAS C.DEB LOJA PR": "Shopping",
    "COMPRAS C.DEB SPORTIN": "Shopping",
    "COMPRAS C.DEB WOMEN S": "Shopping",
    "COMPRAS C.DEB CORTESI": "Shopping",
    "COMPRAS C.DEB BOUTIQU": "Shopping",
    "COMPRAS C.DEB LIBERTY": "Shopping",
    "COMPRAS C.DEB WORLDCO": "Shopping",
    "COMPRAS C.DEB SEVENTH": "Shopping",

    # Beauty & Personal care
    "COMPRAS C.DEB NYX AZN": "Health",
    "COMPRAS C.DEB NYX APL": "Health",
    "COMPRAS C.DEB ITS HAI": "Health",
    "COMPRAS C.DEB FITUEYE": "Health",
    "COMPRAS C.DEB CTRO CL": "Health",

    # Pet
    "COMPRAS C.DEB UPAPI R": "Veterinary",

    # Travel (cont.)
    "COMPRAS C.DEB HOTEL A": "Travel",
    "COMPRAS C.DEB AVAIBOO": "Travel",
    "COMPRAS C.DEB ALLWAYS": "Travel",
    "COMPRAS C.DEB ALBUFEI": "Travel",
    "COMPRA LAGOSINTER LDA": "Travel",
    "COMPRA IN E OUT": "Travel",
    "COMPRAS C.DEB SHS IST": "Travel",
    "COMPRAS C.DEB ITA TRA": "Travel",

    # Telecom
    "COMPRAS C.DEB WWW.THE": "Subscriptions",
    "COMPRAS C.DEB MCO": "Subscriptions",

    # Generic POS / misc small purchases (unclassifiable)
    "COMPRAS C.DEB SUMUP": "Unknown",
    "COMPRAS C.DEB PAD POR": "Unknown",
    "COMPRAS C.DEB ASTRO F": "Cafe",

    # More restaurants / bars (one-offs)
    "COMPRAS C.DEB BANANA": "Restaurant",
    "COMPRAS C.DEB ILHA DO": "Restaurant",
    "COMPRAS C.DEB PRACA J": "Restaurant",
    "COMPRAS C.DEB CHEERS": "Restaurant",
    "COMPRAS C.DEB CALL FO": "Restaurant",
    "COMPRAS C.DEB DOCA MA": "Restaurant",
    "COMPRAS C.DEB DEZ PRA": "Restaurant",
    "COMPRAS C.DEB AMOR AO": "Restaurant",
    "COMPRAS C.DEB SABOR F": "Restaurant",
    "COMPRAS C.DEB UMA CAN": "Restaurant",
    "COMPRAS C.DEB 2COOKIN": "Restaurant",
    "COMPRAS C.DEB LOBA MA": "Restaurant",
    "COMPRAS C.DEB GINJINH": "Restaurant",
    "COMPRAS C.DEB AMOREIR": "Restaurant",
    "COMPRAS C.DEB FORCA P": "Restaurant",
    "COMPRAS C.DEB AMELIA": "Restaurant",
    "COMPRAS C.DEB SPRING": "Restaurant",
    "COMPRAS C.DEB CHAVES": "Restaurant",
    "COMPRAS C.DEB VINCENT": "Restaurant",
    "COMPRAS C.DEB LENA SP": "Restaurant",
    "COMPRAS C.DEB TL CAMP": "Restaurant",
    "COMPRAS C.DEB COSMO": "Restaurant",
    "COMPRAS C.DEB HORTO B": "Restaurant",
    "COMPRAS C.DEB DONNA V": "Restaurant",
    "COMPRAS C.DEB CEBATE": "Restaurant",
    "COMPRAS C.DEB POPBAR": "Cafe",
    "COMPRAS C.DEB ROYAL V": "Restaurant",
    "COMPRAS C.DEB MESTRE": "Restaurant",
    "COMPRAS C.DEB ARTISAN": "Restaurant",

    # Veterinary
    "COMPRAS C.DEB VET CAI": "Veterinary",
    "COMPRAS C.DEB HOSPITA": "Veterinary",  # TODO too greedy

    # Travel
    "COMPRAS C.DEB TURKISH": "Travel",
    "COMPRAS C.DEB RYANAIR": "Travel",
    "COMPRAS C.DEB TAP AIR": "Travel",
    "COMPRAS C.DEB BOOKING": "Travel",

    # Catch-all unknowns (keep last)
    "CR VCHER CRT DB": "Unknown",
    "COMPRAS C.DEB SALA DE": "Unknown",
    "COMPRA MA ALVARES CAB": "Unknown",
    "COMPRAS C.DEB CONTO F": "Unknown",
    "COMPRAS C.DEB REST MC": "Unknown",
    "COMPRAS C.DEB": "Unknown",

    # Income
    "TFI Deel": "Salary",

    # Transfers
    "TRF MBWAY": "Transfers",
    "TRF IMEDIATA INT": "Transfers",
    "TRF": "Transfers",
    "TFI ANA MARGARIDA": "Transfers",
    "TFI": "Transfers",
}

# Super-categories for grouping in summaries
SUPER_CATEGORIES = {
    "Uber": "Transportation",
    "Uber Eats": "Food delivery",
    "Bolt": "Transportation",
    "Trains": "Transportation",
    "Groceries": "Essentials",
    "Home goods": "Essentials",
    "Tech": "Shopping",
    "Amazon": "Shopping",
    "Subscriptions": "Recurring",
    "Games": "Recurring",
    "Cafe": "Dining out",
    "Restaurant": "Dining out",
    "Clothes": "Shopping",
    "Gym": "Recurring",
    "Leisure": "Lifestyle",
    "Cleaning": "Recurring",
    "Bank fees": "Recurring",
    "Taxes": "Taxes",
    "Withdrawal": "Cash",
    "Veterinary": "Essentials",
    "Travel": "Travel",
    "Health": "Essentials",
    "Utilities": "Recurring",
    "Insurance": "Recurring",
    "Rent": "Housing",
    "Car": "Transportation",
    "Shopping": "Shopping",
    "Unknown": "Other",
    "Salary": "Income",
    "Transfers": "Transfers",
}


def _currency(v: Decimal) -> str:
    import babel.numbers
    return babel.numbers.format_currency(v, 'EUR', locale='en_CA')


def _to_date(v: str) -> date:
    return date(*map(int, v.split("-")))


def discover_pdfs(directory="."):
    """Find all PDF files that look like bank statements."""
    all_pdfs = glob.glob(os.path.join(directory, "*.pdf"))
    return sorted(all_pdfs)


def extract_transactions(pdf_path):
    doc = fitz.open(pdf_path)
    transactions = []

    transaction_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.+) (\d*)"
    )

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text("text")

        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.match(r"\d\d\d\d-\d\d-\d\d", line):
                if m := transaction_pattern.match(line):
                    transaction = {
                        "transaction_date": _to_date(m.group(1)),
                        "purchase_date": _to_date(m.group(2)),
                        "description": re.sub(r"\s+", " ", m.group(3)).strip(),
                        "amount": Decimal(lines[i+1].replace(".", "").replace(",", ".")),
                        "balance": Decimal(lines[i+2].replace(".", "").replace(",", ".")),
                        "filename": pdf_path,
                    }
                    transactions.append(transaction)

    doc.close()
    return transactions


def compute_recurring_amounts(all_transactions):
    """Find subscription amounts that appear at least twice (recurring charges).

    Returns a set of amounts that recur, used to distinguish real subscriptions
    from one-off purchases at subscription vendors (e.g. Apple Store buys).
    """
    amount_counts = Counter()
    for trx in all_transactions:
        cat = _raw_categorize(trx["description"], trx["amount"])
        if cat == "Subscriptions":
            amount_counts[trx["amount"]] += 1
    return {amt for amt, cnt in amount_counts.items() if cnt >= 2}


def _raw_categorize(description, amount):
    """Return the raw category from CATEGORIES dict (no recurring check)."""
    desc_upper = description.upper()
    for pattern, category in CATEGORIES.items():
        if pattern.upper() in desc_upper:
            if category == "Uber" and amount < Decimal("-15"):
                return "Uber Eats"
            if category == "Transfers" and Decimal("-1500") <= amount <= Decimal("-1400"):
                return "Rent"
            return category
    return None


def categorize_transaction(description, amount, recurring_amounts=None):
    """Return the category for a single transaction.

    If recurring_amounts is provided, transactions that match a Subscriptions
    pattern but whose amount does not recur are reclassified as Shopping.
    """
    cat = _raw_categorize(description, amount)
    if cat == "Subscriptions" and recurring_amounts is not None:
        if amount not in recurring_amounts:
            return "Shopping"
    return cat


def categorize(transactions: list[dict], recurring_amounts=None) -> dict:
    """Categorize transactions and return structured data.

    Returns dict with keys: sums, counts, uncategorized, debit, credit,
    balance_start, balance_end, categorized_transactions.
    """
    sums = Counter()
    counts = defaultdict(int)
    uncategorized = []
    categorized_transactions = []

    for trx in transactions:
        cat = categorize_transaction(trx["description"], trx["amount"], recurring_amounts)
        if cat:
            sums[cat] += trx["amount"]
            counts[cat] += 1
            categorized_transactions.append({**trx, "category": cat})
        else:
            uncategorized.append({**trx, "category": None})

    debit = Decimal()
    credit = Decimal()
    for amount in sums.values():
        if amount < Decimal():
            debit += amount
        else:
            credit += amount

    balance_start = transactions[0]["balance"] if transactions else None
    balance_end = transactions[-1]["balance"] if transactions else None

    return {
        "sums": dict(sums),
        "counts": dict(counts),
        "uncategorized": uncategorized,
        "categorized_transactions": categorized_transactions,
        "debit": debit,
        "credit": credit,
        "balance_start": balance_start,
        "balance_end": balance_end,
    }


def load_transactions(directory=".", last_n_months=0):
    """Load and sort all transactions, optionally limited to last N months.

    Returns (monthly_groups, all_transactions, recurring_amounts) where
    monthly_groups is a list of (month_str, [transactions]) tuples and
    recurring_amounts is the set of subscription amounts that recur.
    """
    pdf_files = discover_pdfs(directory)
    if not pdf_files:
        return [], [], set()

    all_transactions = []
    for pdf in pdf_files:
        all_transactions += extract_transactions(pdf)

    all_transactions.sort(key=lambda x: (x["purchase_date"], x["transaction_date"]))

    # Compute recurring amounts from ALL transactions before slicing
    recurring_amounts = compute_recurring_amounts(all_transactions)

    monthly_groups = []
    for month, trxs in groupby(all_transactions, lambda x: x["purchase_date"].strftime("%Y-%m")):
        monthly_groups.append((month, list(trxs)))

    if last_n_months:
        monthly_groups = monthly_groups[-last_n_months:]
        all_transactions = [trx for _, trxs in monthly_groups for trx in trxs]

    return monthly_groups, all_transactions, recurring_amounts


def compute_monthly_stats(monthly_groups: list[tuple[str, list[dict]]], recurring_amounts=None) -> list[dict]:
    """Compute per-month statistics.

    Returns list of dicts with keys: month, income, spending, net, savings_rate,
    balance_start, balance_end, category_data (from categorize()).
    """
    results = []
    for month, trx_list in monthly_groups:
        cat_data = categorize(trx_list, recurring_amounts)
        income = cat_data["credit"]
        spending = cat_data["debit"]
        net = income + spending
        savings_rate = (net / income * 100) if income > 0 else Decimal(0)

        results.append({
            "month": month,
            "income": income,
            "spending": spending,
            "net": net,
            "savings_rate": savings_rate,
            "balance_start": cat_data["balance_start"],
            "balance_end": cat_data["balance_end"],
            "category_data": cat_data,
        })
    return results


def compute_overall_stats(monthly_stats: list[dict], all_transactions: list[dict],
                          recurring_amounts=None) -> dict:
    """Compute aggregated statistics across all months.

    Returns dict with keys: months_count, total_income, total_spending, total_net,
    savings_rate, balance_start, balance_end, balance_change,
    categories (list of dicts), super_categories (list of dicts),
    monthly_trend (list of dicts), recommendations (list of strings),
    total_transactions, uncategorized (list of transactions).
    """
    months_count = len(monthly_stats)
    if not months_count:
        return {}

    # Aggregate category sums and counts
    total_sums = Counter()
    total_counts = defaultdict(int)
    all_uncategorized = []

    for ms in monthly_stats:
        cd = ms["category_data"]
        for cat, amount in cd["sums"].items():
            total_sums[cat] += amount
            total_counts[cat] += cd["counts"].get(cat, 0)
        all_uncategorized.extend(cd["uncategorized"])

    total_income = Decimal()
    total_spending = Decimal()
    categories = []
    for cat, amount in sorted(total_sums.items(), key=lambda x: (x[1] < Decimal(), -abs(x[1]))):
        avg = amount / months_count
        categories.append({
            "category": cat,
            "total": amount,
            "count": total_counts[cat],
            "monthly_avg": avg,
        })
        if amount < Decimal():
            total_spending += amount
        else:
            total_income += amount

    total_net = total_income + total_spending
    savings_rate = (total_net / total_income * 100) if total_income > 0 else Decimal(0)

    # Super-category breakdown
    super_sums = defaultdict(Decimal)
    for cat, amount in total_sums.items():
        sc = SUPER_CATEGORIES.get(cat, "Other")
        super_sums[sc] += amount

    spending_super = {k: v for k, v in super_sums.items() if v < Decimal() and k not in ("Income", "Transfers")}
    super_total = sum(spending_super.values()) if spending_super else Decimal()
    super_categories = []
    for sc, amount in sorted(spending_super.items(), key=lambda x: x[1]):
        pct = (amount / super_total * 100) if super_total else Decimal()
        super_categories.append({
            "group": sc,
            "total": amount,
            "monthly_avg": amount / months_count,
            "pct": pct,
        })

    # Balance trend
    balance_start = all_transactions[0]["balance"] if all_transactions else None
    balance_end = all_transactions[-1]["balance"] if all_transactions else None
    balance_change = (balance_end - balance_start) if balance_start is not None else None

    # Monthly spending/income trend
    monthly_spending = defaultdict(Decimal)
    monthly_income_map = defaultdict(Decimal)
    for trx in all_transactions:
        month_key = trx["purchase_date"].strftime("%Y-%m")
        if trx["amount"] < Decimal():
            cat = categorize_transaction(trx["description"], trx["amount"], recurring_amounts)
            if cat != "Transfers":
                monthly_spending[month_key] += trx["amount"]
        else:
            monthly_income_map[month_key] += trx["amount"]

    monthly_trend = []
    for month in sorted(set(monthly_spending) | set(monthly_income_map)):
        spent = monthly_spending.get(month, Decimal())
        income = monthly_income_map.get(month, Decimal())
        savings = income + spent
        rate = (savings / income * 100) if income else Decimal()
        monthly_trend.append({
            "month": month,
            "income": income,
            "spending": spent,
            "savings": savings,
            "savings_rate": rate,
        })

    # Recommendations
    recommendations = _compute_recommendations(
        total_sums, total_counts, months_count,
        monthly_spending, monthly_income_map, all_transactions,
    )

    return {
        "months_count": months_count,
        "total_income": total_income,
        "total_spending": total_spending,
        "total_net": total_net,
        "savings_rate": savings_rate,
        "balance_start": balance_start,
        "balance_end": balance_end,
        "balance_change": balance_change,
        "categories": categories,
        "super_categories": super_categories,
        "monthly_trend": monthly_trend,
        "recommendations": recommendations,
        "total_transactions": sum(total_counts.values()),
        "uncategorized": all_uncategorized,
    }


def _compute_recommendations(total_sums, total_counts, months_count,
                             monthly_spending, monthly_income, all_transactions):
    """Generate financial recommendations based on spending patterns."""
    recommendations = []
    avg_monthly_income = sum(monthly_income.values()) / months_count if months_count else Decimal()
    avg_monthly_spending = abs(sum(monthly_spending.values()) / months_count) if months_count else Decimal()

    if avg_monthly_income > 0:
        savings_rate = (avg_monthly_income - avg_monthly_spending) / avg_monthly_income * 100
        if savings_rate < 20:
            recommendations.append(
                f"[!] LOW SAVINGS RATE: {savings_rate:.0f}% of income saved on average. "
                f"Target at least 20%. Consider reducing discretionary spending."
            )
        elif savings_rate >= 20:
            recommendations.append(
                f"[+] SAVINGS RATE: {savings_rate:.0f}% -- on track. "
                f"Consider investing surplus in index funds or savings certificates (Certificados de Aforro)."
            )

    uber_total = abs(total_sums.get("Uber", Decimal()) + total_sums.get("Bolt", Decimal()))
    uber_avg = uber_total / months_count if months_count else Decimal()
    if uber_avg > Decimal("100"):
        recommendations.append(
            f"[!] RIDE-HAILING: Averaging {_currency(uber_avg)}/month on rides. "
            f"A monthly transit pass (Navegante) costs ~EUR 40 and covers all Lisbon transit."
        )

    eats_total = abs(total_sums.get("Uber Eats", Decimal()))
    eats_avg = eats_total / months_count if months_count else Decimal()
    if eats_avg > Decimal("50"):
        recommendations.append(
            f"[!] FOOD DELIVERY: Averaging {_currency(eats_avg)}/month on Uber Eats. "
            f"Cooking at home or meal prepping could cut this significantly."
        )

    dining = abs(total_sums.get("Cafe", Decimal()) + total_sums.get("Restaurant", Decimal()))
    dining_avg = dining / months_count if months_count else Decimal()
    if dining_avg > Decimal("100"):
        recommendations.append(
            f"[-] DINING OUT: Averaging {_currency(dining_avg)}/month on cafes and restaurants."
        )

    grocery_total = abs(total_sums.get("Groceries", Decimal()))
    grocery_avg = grocery_total / months_count if months_count else Decimal()
    if grocery_avg > Decimal("300"):
        recommendations.append(
            f"[-] GROCERIES: Averaging {_currency(grocery_avg)}/month. "
            f"Consider shopping more at Lidl/Pingo Doce vs Continente for savings."
        )

    subs_total = abs(total_sums.get("Subscriptions", Decimal()) + total_sums.get("Games", Decimal()))
    subs_avg = subs_total / months_count if months_count else Decimal()
    if subs_avg > Decimal("30"):
        recommendations.append(
            f"[-] SUBSCRIPTIONS: {_currency(subs_avg)}/month on subscriptions and games. "
            f"Review if all are actively used."
        )

    fees_total = abs(total_sums.get("Bank fees", Decimal()))
    fees_avg = fees_total / months_count if months_count else Decimal()
    if fees_avg > Decimal("0"):
        recommendations.append(
            f"[-] BANK FEES: Paying {_currency(fees_avg)}/month in bank fees. "
            f"Consider switching to a free digital bank (Moey, ActivoBank) to eliminate this."
        )

    spending_values = [abs(v) for v in monthly_spending.values()]
    if len(spending_values) >= 3:
        avg_spend = sum(spending_values) / len(spending_values)
        max_spend = max(spending_values)
        if max_spend > avg_spend * Decimal("1.5"):
            max_month = max(monthly_spending, key=lambda k: abs(monthly_spending[k]))
            recommendations.append(
                f"[!] SPENDING SPIKE: {max_month} had {_currency(max_spend)} in spending "
                f"(avg: {_currency(avg_spend)}). Check for large one-off purchases."
            )

    travel_total = abs(total_sums.get("Travel", Decimal()))
    if travel_total > Decimal("0"):
        recommendations.append(
            f"[i] TRAVEL: {_currency(travel_total)} spent on travel over the period. "
            f"Book flights in advance and use price trackers for better deals."
        )

    if avg_monthly_spending > 0 and all_transactions:
        months_covered = all_transactions[-1]["balance"] / avg_monthly_spending
        if months_covered < 6:
            recommendations.append(
                f"[!] EMERGENCY FUND: Current balance covers ~{months_covered:.1f} months of expenses. "
                f"Aim for 6 months of expenses as a safety net."
            )
        else:
            recommendations.append(
                f"[+] EMERGENCY FUND: Current balance covers ~{months_covered:.1f} months of expenses. "
                f"Well above the recommended 6-month buffer."
            )

    return recommendations


def main():
    """CLI entry point — prints reports to stdout (legacy behavior)."""
    import argparse
    import sys
    from tabulate import tabulate

    parser = argparse.ArgumentParser(description="Analyse bank statement PDFs")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing PDF statements")
    parser.add_argument("-n", "--months", type=int, default=0, help="Only show the last N months")
    args = parser.parse_args()

    monthly_groups, all_transactions, recurring_amounts = load_transactions(args.directory, args.months)

    if not monthly_groups:
        print(f"No PDF files found in {os.path.abspath(args.directory)}")
        sys.exit(1)

    pdf_files = discover_pdfs(args.directory)
    print(f"Found {len(pdf_files)} statement(s): {', '.join(os.path.basename(f) for f in pdf_files)}\n")

    monthly_stats = compute_monthly_stats(monthly_groups, recurring_amounts)

    for ms in monthly_stats:
        cd = ms["category_data"]
        print()
        print("=" * 40)
        print(f"  {ms['month']}")
        print("=" * 40)

        d = []
        for c, amount in sorted(cd["sums"].items(), key=lambda x: (x[1] < Decimal(), -abs(x[1]))):
            d.append((c, _currency(amount), cd["counts"][c]))
        print(tabulate(d, headers=["Category", "Amount", "Count"], numalign="left"))
        print()
        print(tabulate(
            [[_currency(cd["debit"]), _currency(cd["credit"]), _currency(cd["credit"] + cd["debit"])]],
            headers=["Spending", "Income", "Net"],
            numalign="left",
        ))

        if cd["balance_start"] is not None:
            print()
            print(tabulate(
                [[_currency(cd["balance_start"]), _currency(cd["balance_end"])]],
                headers=["Balance start", "End"],
                numalign="left",
            ))

        if cd["uncategorized"]:
            print(f"\n  [{len(cd['uncategorized'])} uncategorized transaction(s)]")
            for trx in cd["uncategorized"]:
                print(f"    {trx['purchase_date']}  {_currency(trx['amount']):>12}  {trx['description']}")

    if len(monthly_stats) > 1:
        overall = compute_overall_stats(monthly_stats, all_transactions, recurring_amounts)
        print("\n")
        print("=" * 60)
        print("OVERALL SUMMARY")
        print("=" * 60)
        print(f"\nPeriod: {overall['months_count']} month(s)")
        print(f"Total transactions: {overall['total_transactions']}\n")

        d = []
        for cat_info in overall["categories"]:
            d.append((cat_info["category"], _currency(cat_info["total"]),
                       cat_info["count"], _currency(cat_info["monthly_avg"])))
        print(tabulate(d, headers=["Category", "Total", "Count", "Monthly avg"], numalign="left"))
        print()
        print(tabulate(
            [[_currency(overall["total_spending"]), _currency(overall["total_income"]),
              _currency(overall["total_net"])]],
            headers=["Total spending", "Total income", "Net"],
            numalign="left",
        ))

        if overall["super_categories"]:
            print("\n--- Spending by group ---\n")
            sd = []
            for sc in overall["super_categories"]:
                sd.append((sc["group"], _currency(sc["total"]),
                           _currency(sc["monthly_avg"]), f"{sc['pct']:.1f}%"))
            print(tabulate(sd, headers=["Group", "Total", "Monthly avg", "% of spending"], numalign="left"))

        if overall["balance_start"] is not None:
            print(f"\n--- Balance trend ---\n")
            print(f"  Start:  {_currency(overall['balance_start'])}")
            print(f"  End:    {_currency(overall['balance_end'])}")
            print(f"  Change: {_currency(overall['balance_change'])}")

        print(f"\n--- Monthly spending trend ---\n")
        td = []
        for mt in overall["monthly_trend"]:
            td.append((mt["month"], _currency(mt["income"]), _currency(mt["spending"]),
                        _currency(mt["savings"]), f"{mt['savings_rate']:.0f}%"))
        print(tabulate(td, headers=["Month", "Income", "Spending", "Savings", "Rate"], numalign="left"))

        print("\n" + "=" * 60)
        print("FINANCIAL RECOMMENDATIONS")
        print("=" * 60)
        print()
        for i, rec in enumerate(overall["recommendations"], 1):
            print(f"  {i}. {rec}")
            print()


if __name__ == "__main__":
    main()
