import argparse
import sys
from decimal import Decimal

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static, ListView, ListItem, Label, Select
from textual.containers import VerticalScroll

from expences import (
    _currency,
    compute_monthly_stats,
    compute_overall_stats,
    compute_recurring_amounts,
    load_transactions,
)


MENU_ITEMS = [
    ("months", "Months", "Monthly breakdown of income and spending"),
    ("categories", "Categories", "All categories aggregated across months"),
    ("uncategorized", "Uncategorized", "Transactions that couldn't be categorized"),
    ("recommendations", "Recommendations", "Financial advice based on your spending"),
]

PERIOD_OPTIONS = [
    ("Last month", 1),
    ("Last 3 months", 3),
    ("Last 6 months", 6),
    ("Last year", 12),
    ("All time", 0),
]


def _filter_by_period(app, n_months: int):
    """Return (monthly_stats, overall) filtered to last n_months (0 = all)."""
    stats = app.monthly_stats
    if n_months and len(stats) > n_months:
        stats = stats[-n_months:]
    all_trx = []
    for ms in stats:
        cd = ms["category_data"]
        all_trx.extend(cd["categorized_transactions"])
        all_trx.extend(cd["uncategorized"])
    all_trx.sort(key=lambda t: (t["purchase_date"], t.get("transaction_date", t["purchase_date"])), reverse=True)
    overall = compute_overall_stats(stats, all_trx, app.recurring_amounts)
    return stats, overall


class DashboardScreen(Screen):
    BINDINGS = [
        Binding("m", "months", "Months"),
        Binding("c", "categories", "Categories"),
        Binding("u", "uncategorized", "Uncategorized"),
        Binding("r", "recommendations", "Recommendations"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="dashboard-content")
        yield ListView(
            *(ListItem(Label(f"[b]{label}[/b]  {desc}"), name=key)
              for key, label, desc in MENU_ITEMS),
            id="dashboard-menu",
        )
        yield Footer()

    def on_mount(self) -> None:
        overall = self.app.overall
        if not overall:
            self.query_one("#dashboard-content", Static).update("No data loaded.")
            return

        lines = []
        lines.append(f"Period: {overall['months_count']} month(s)")
        lines.append(f"Total transactions: {overall['total_transactions']}")
        lines.append("")
        lines.append(f"Total income:   {_currency(overall['total_income'])}")
        lines.append(f"Total spending: {_currency(overall['total_spending'])}")
        lines.append(f"Net:            {_currency(overall['total_net'])}")
        lines.append(f"Savings rate:   {overall['savings_rate']:.0f}%")
        lines.append("")
        if overall["balance_start"] is not None:
            lines.append(f"Balance start:  {_currency(overall['balance_start'])}")
            lines.append(f"Balance end:    {_currency(overall['balance_end'])}")
            lines.append(f"Balance change: {_currency(overall['balance_change'])}")

        self.query_one("#dashboard-content", Static).update("\n".join(lines))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        key = event.item.name
        actions = {
            "months": MonthsScreen,
            "categories": CategoriesScreen,
            "uncategorized": UncategorizedScreen,
            "recommendations": RecommendationsScreen,
        }
        screen_cls = actions.get(key)
        if screen_cls:
            self.app.push_screen(screen_cls())

    def action_months(self) -> None:
        self.app.push_screen(MonthsScreen())

    def action_categories(self) -> None:
        self.app.push_screen(CategoriesScreen())

    def action_uncategorized(self) -> None:
        self.app.push_screen(UncategorizedScreen())

    def action_recommendations(self) -> None:
        self.app.push_screen(RecommendationsScreen())

    def action_quit(self) -> None:
        self.app.exit()


class MonthsScreen(Screen):
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("h", "home", "Home"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="months-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#months-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Month", "Income", "Spending", "Net", "Savings %")
        for ms in reversed(self.app.monthly_stats):
            table.add_row(
                ms["month"],
                _currency(ms["income"]),
                _currency(ms["spending"]),
                _currency(ms["net"]),
                f"{ms['savings_rate']:.0f}%",
                key=ms["month"],
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        month = str(event.row_key.value)
        self.app.push_screen(MonthDetailScreen(month))

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_home(self) -> None:
        self.app.pop_screen_until_dashboard()

    def action_quit(self) -> None:
        self.app.exit()


class MonthDetailScreen(Screen):
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("h", "home", "Home"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, month: str) -> None:
        super().__init__()
        self.month = month

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="month-detail-table")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.month
        ms = next((m for m in self.app.monthly_stats if m["month"] == self.month), None)
        if not ms:
            return

        table = self.query_one("#month-detail-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Category", "Amount", "Count")

        cd = ms["category_data"]
        for cat, amount in sorted(cd["sums"].items(), key=lambda x: abs(x[1]), reverse=True):
            table.add_row(cat, _currency(amount), str(cd["counts"][cat]), key=cat)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        category = str(event.row_key.value)
        self.app.push_screen(TransactionsScreen(month=self.month, category=category))

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_home(self) -> None:
        self.app.pop_screen_until_dashboard()

    def action_quit(self) -> None:
        self.app.exit()


class CategoriesScreen(Screen):
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("h", "home", "Home"),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_PERIOD = 3

    def compose(self) -> ComposeResult:
        yield Header()
        yield Select(
            [(label, value) for label, value in PERIOD_OPTIONS],
            value=self.DEFAULT_PERIOD,
            id="period-select",
        )
        yield DataTable(id="categories-table")
        yield Footer()

    def on_mount(self) -> None:
        self._current_period = self.DEFAULT_PERIOD
        self._refresh_table(self._current_period)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "period-select" and event.value != Select.BLANK:
            self._current_period = event.value
            self._refresh_table(self._current_period)

    def _refresh_table(self, n_months: int) -> None:
        _, overall = _filter_by_period(self.app, n_months)
        if not overall:
            return

        table = self.query_one("#categories-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("Category", "Total", "Count", "Monthly avg")

        for cat_info in overall["categories"]:
            table.add_row(
                cat_info["category"],
                _currency(cat_info["total"]),
                str(cat_info["count"]),
                _currency(cat_info["monthly_avg"]),
                key=cat_info["category"],
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        category = str(event.row_key.value)
        self.app.push_screen(TransactionsScreen(category=category, n_months=self._current_period))

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_home(self) -> None:
        self.app.pop_screen_until_dashboard()

    def action_quit(self) -> None:
        self.app.exit()


class TransactionsScreen(Screen):
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("h", "home", "Home"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, month: str | None = None, category: str | None = None, n_months: int = 0) -> None:
        super().__init__()
        self.month = month
        self.category = category
        self.n_months = n_months

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="transactions-table")
        yield Footer()

    def on_mount(self) -> None:
        parts = []
        if self.month:
            parts.append(self.month)
        if self.category:
            parts.append(self.category)
        self.sub_title = " / ".join(parts) if parts else "Transactions"

        # Collect transactions, respecting period filter
        stats = self.app.monthly_stats
        if self.n_months and len(stats) > self.n_months:
            stats = stats[-self.n_months:]
        all_trx = []
        for ms in stats:
            cd = ms["category_data"]
            all_trx.extend(cd["categorized_transactions"])
            all_trx.extend(cd["uncategorized"])

        # Filter
        if self.month:
            all_trx = [t for t in all_trx if t["purchase_date"].strftime("%Y-%m") == self.month]
        if self.category:
            all_trx = [t for t in all_trx if t.get("category") == self.category]

        all_trx.sort(key=lambda t: t["purchase_date"], reverse=True)

        table = self.query_one("#transactions-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Date", "Description", "Amount", "Balance", "Category")

        for trx in all_trx:
            table.add_row(
                str(trx["purchase_date"]),
                trx["description"],
                _currency(trx["amount"]),
                _currency(trx["balance"]),
                trx.get("category") or "???",
            )

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_home(self) -> None:
        self.app.pop_screen_until_dashboard()

    def action_quit(self) -> None:
        self.app.exit()


class UncategorizedScreen(Screen):
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("h", "home", "Home"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="uncategorized-table")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Uncategorized"
        uncategorized = self.app.overall.get("uncategorized", []) if self.app.overall else []

        table = self.query_one("#uncategorized-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Date", "Description", "Amount", "Balance")

        for trx in sorted(uncategorized, key=lambda t: t["purchase_date"], reverse=True):
            table.add_row(
                str(trx["purchase_date"]),
                trx["description"],
                _currency(trx["amount"]),
                _currency(trx["balance"]),
            )

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_home(self) -> None:
        self.app.pop_screen_until_dashboard()

    def action_quit(self) -> None:
        self.app.exit()


class RecommendationsScreen(Screen):
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("h", "home", "Home"),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_PERIOD = 3

    def compose(self) -> ComposeResult:
        yield Header()
        yield Select(
            [(label, value) for label, value in PERIOD_OPTIONS],
            value=self.DEFAULT_PERIOD,
            id="period-select",
        )
        yield VerticalScroll(Static(id="recommendations-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = "Recommendations"
        self._refresh_content(self.DEFAULT_PERIOD)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "period-select" and event.value != Select.BLANK:
            self._refresh_content(event.value)

    def _refresh_content(self, n_months: int) -> None:
        _, overall = _filter_by_period(self.app, n_months)
        recs = overall.get("recommendations", []) if overall else []
        if not recs:
            text = "No recommendations available."
        else:
            text = "\n\n".join(f"{i}. {rec}" for i, rec in enumerate(recs, 1))
        self.query_one("#recommendations-content", Static).update(text)

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_home(self) -> None:
        self.app.pop_screen_until_dashboard()

    def action_quit(self) -> None:
        self.app.exit()


class ExpencesApp(App):
    TITLE = "Expences"
    CSS = """
    #dashboard-content {
        padding: 1 2;
        margin-bottom: 1;
        height: auto;
    }
    #recommendations-content {
        padding: 1 2;
    }
    #dashboard-menu {
        height: auto;
        margin: 0 2 1 2;
    }
    #dashboard-menu > ListItem {
        padding: 0 1;
    }
    #period-select {
        height: auto;
        margin: 1 2 0 2;
        width: 30;
    }
    DataTable {
        height: 1fr;
    }
    """

    def __init__(self, directory: str = ".", last_n_months: int = 0) -> None:
        super().__init__()
        self.directory = directory
        self.last_n_months = last_n_months
        self.monthly_stats: list[dict] = []
        self.overall: dict | None = None
        self.recurring_amounts: set = set()

    def on_mount(self) -> None:
        monthly_groups, all_transactions, self.recurring_amounts = load_transactions(
            self.directory, self.last_n_months
        )
        if not monthly_groups:
            self.exit(message=f"No PDF files found in {self.directory}")
            return

        self.monthly_stats = compute_monthly_stats(monthly_groups, self.recurring_amounts)
        self.overall = compute_overall_stats(self.monthly_stats, all_transactions, self.recurring_amounts)
        self.push_screen(DashboardScreen())

    def pop_screen_until_dashboard(self) -> None:
        """Pop all screens until we're back at the DashboardScreen."""
        while self.screen_stack and not isinstance(self.screen, DashboardScreen):
            self.pop_screen()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Expences TUI")
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing PDF statements")
    parser.add_argument("-n", "--months", type=int, default=0, help="Only show the last N months")
    args = parser.parse_args()

    app = ExpencesApp(directory=args.directory, last_n_months=args.months)
    app.run()
