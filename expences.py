import re
from datetime import date
from decimal import Decimal
from pprint import pp
from collections import defaultdict, Counter
from itertools import groupby

import babel.numbers
import fitz  # PyMuPDF
from tabulate import tabulate

# import sqlite3
# con = sqlite3.connect("tutorial.db")


def _currency(v: Decimal) -> str:
    return babel.numbers.format_currency(v, 'EUR', locale='en_CA')


def _to_date(v: str) -> date:
    return date(*map(int, v.split("-")))


def extract_transactions(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    transactions = []

    # Regex to match the transaction lines
    transaction_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.+) (\d*)"
    )

    # Loop through each page in the PDF
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
                    # pp(transaction)
                    transactions.append(transaction)
                else:
                    pass
                    # print(f"UNPARSED TRX: {line}")
                    # print(lines[i+1])
                    # print(lines[i+2])

    # Close the PDF document
    doc.close()
    return transactions


def categorize(transactions: list[dict]):
    categories = {
        "COMPRAS C.DEB UBER": "Uber",
        "COMPRAS C.DEB BOLT.EU": "Bolt",

        "COMPRA CP CAIS SODRE": "Trains",
        "COMPRA CARREGAMENTO": "Trains",

        "COMPRAS C.DEB FRESCUR": "Groceries",
        "WWW.CONTINENTE": "Groceries",
        "COMPRAS C.DEB CONTINE": "Groceries",
        "COMPRA VASQUES GARC": "Groceries",  # Talho
        "COMPRAS C.DEB PINGO D": "Groceries",
        "COMPRAS C.DEB NESTLE": "Groceries",
        "COMPRAS C.DEB ATALHO": "Groceries",
        "COMPRAS C.DEB EL CORT": "Groceries",
        "COMPRAS C.DEB GAYO-YA": "Groceries",
        "COMPRAS C.DEB AROIOS": "Groceries",
        "COMPRA LIDL AGRADECE": "Groceries",

        "COMPRA IKEA PORTUGAL": "Home goods",

        "COMPRA WORTEN-EQUIPAM": "Tech",

        "COMPRAS C.DEB AMZN": "Amazon",
        "COMPRA CTT - CORREIO": "Amazon",
        "COMPRAS C.DEB WWW.AMA": "Amazon",
        "COMPRAS C.DEB AMAZON": "Amazon",

        "COMPRAS C.DEB NETFLIX": "Subscriptions",
        "COMPRAS C.DEB APPLE.C": "Subscriptions",

        "COMPRAS C.DEB MICROSO": "Games",

        "COMPRAS C.DEB POPPY": "Cafe",
        "COMPRAS C.DEB CAFE MA": "Cafe",
        "COMPRAS C.DEB FAUNA": "Cafe",
        "COMPRAS C.DEB DEJAVU": "Cafe",

        "COMPRAS C.DEB CHAPITO": "Restaurant",
        "COMPRAS C.DEB PILS": "Restaurant",

        "COMPRAS C.DEB NIKE": "Clothes",

        "TRF MBWAY 913xxx401": "Gym",
        "COMPRAS C.DEB SUNSETF": "Gym",

        "COMPRAS C.DEB MARINHA": "Walkout",
        "COMPRAS C.DEB MUSEU": "Walkout",
        "COMPRAS C.DEB FEVER": "Walkout",
        "COMPRAS C.DEB QUIOSQU": "Walkout",
        "COMPRA FUND CALOUSTE": "Walkout",

        "COMPRAS C.DEB OSCAR": "Cleaning",

        "MANUT CONTA PACOTE CAIXA": "Fees",

        "I G F S": "Taxes",
        "INST GEST": "Taxes",
        "PAG 10095 PAG-ESTADO": "Taxes",

        "LEVANTAMENTO": "Withdrawal",

        "COMPRAS C.DEB VET CAI": "Veterinary",
        "COMPRAS C.DEB HOSPITA": "Veterinary",  # TODO too greedy category

        "CR VCHER CRT DB": "Unknown",
        "COMPRAS C.DEB SALA DE": "Unknown",
        "COMPRA MA ALVARES CAB": "Unknown",
        "COMPRAS C.DEB CONTO F": "Unknown",
        "COMPRAS C.DEB REST MC": "Unknown",
        "COMPRAS C.DEB": "Unknown",

        "TFI Deel": "Salary",

        "TRF MBWAY": "Transfers",
    }
    sums = Counter()
    counts = defaultdict(int)
    fns = set()

    # Print extracted transactions
    for trx in transactions:
        fns.add(trx["filename"])
        for i, c in categories.items():
            if i in trx["description"]:

                if "Uber" == c and trx["amount"] < Decimal("-15"):
                    c = "Uber Eats"

                sums[c] += trx["amount"]
                counts[c] += 1

                break
        else:
            pp(trx)
            break

    debit = Decimal()
    credit = Decimal()

    d = []
    for c, amount in sorted(sums.items(), key=lambda x: (x[1] < Decimal(), -abs(x[1]))):
        d.append((c, str(amount), counts[c]))
        if amount < Decimal():
            debit += amount
        else:
            credit += amount
    fns = ", ".join(sorted(fns))
    print(tabulate(d, headers=["Category", "amount", "count"], numalign="left"))
    print(f"Debit: {debit}, credit: {credit}, files: {fns}")
    b1 = _currency(transactions[0]['balance'])
    b2 = _currency(transactions[-1]['balance'])
    print(f"Balance: {b1} -> {b2}")


transactions = []
transactions += extract_transactions('comprovativo_202406.pdf')
transactions += extract_transactions('comprovativo_202407.pdf')
transactions += extract_transactions('comprovativo_202408.pdf')
transactions += extract_transactions('comprovativo_202409.pdf')

transactions.sort(key=lambda x: x["purchase_date"].strftime("%Y%m"))

for month, trxs in groupby(transactions, lambda x: x["purchase_date"].strftime("%Y-%m")):
    print()
    print(month)
    categorize(list(trxs))
