import pandas as pd
import csv
import os
from datetime import datetime
from data_entry import (
    get_amount, get_category, get_date, get_description,
    clear_screen, success, error, warn, info, colored_input,
    DATE_FORMAT, console,
)
import matplotlib.pyplot as plt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.bar import Bar
from rich.progress import BarColumn, Progress
from rich import box


# ── Banner ───────────────────────────────────────────────────
BANNER_TEXT = Text.from_markup(
    "\n[bold cyan]💰  F I N A N C E   T R A C K E R  💰[/bold cyan]\n"
    "[dim]Track your income & expenses with style[/dim]\n"
)

BANNER = Panel(
    Align.center(BANNER_TEXT),
    border_style="bold cyan",
    box=box.DOUBLE_EDGE,
    padding=(0, 2),
)


def build_menu():
    """Build a rich-styled menu panel."""
    menu_items = [
        ("[bold green]1[/bold green]", "Add Transaction", "📝"),
        ("[bold green]2[/bold green]", "View Transactions", "📋"),
        ("[bold green]3[/bold green]", "Dashboard (Summary)", "📊"),
        ("[bold green]4[/bold green]", "Plot Income vs Expense", "📈"),
        ("[bold green]5[/bold green]", "Delete Transaction", "🗑️"),
        ("[bold red]0[/bold red]", "Exit", "👋"),
    ]
    menu_text = "\n".join(
        f"   {icon}  {key}  →  {label}" for key, label, icon in menu_items
    )
    return Panel(
        menu_text,
        title="[bold white]Menu[/bold white]",
        title_align="center",
        border_style="bright_white",
        box=box.ROUNDED,
        padding=(1, 3),
    )


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = DATE_FORMAT

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)

    @classmethod
    def get_all_transactions(cls):
        cls.initialize_csv()
        df = pd.read_csv(cls.CSV_FILE)
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT)
        return df

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = cls.get_all_transactions()
        if df.empty:
            return df
        start = datetime.strptime(start_date, cls.FORMAT)
        end = datetime.strptime(end_date, cls.FORMAT)
        mask = (df["date"] >= start) & (df["date"] <= end)
        return df.loc[mask]

    @classmethod
    def delete_entry(cls, index):
        df = pd.read_csv(cls.CSV_FILE)
        if index < 0 or index >= len(df):
            return False
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(cls.CSV_FILE, index=False)
        return True


# ── Helpers ──────────────────────────────────────────────────
def print_table(df):
    """Pretty-print a transactions dataframe using a Rich table."""
    if df.empty:
        warn("No transactions to display.")
        return

    table = Table(
        title=None,
        box=box.ROUNDED,
        show_lines=False,
        header_style="bold white",
        border_style="bright_black",
        padding=(0, 1),
    )
    table.add_column("#", style="dim", justify="right", width=5)
    table.add_column("Date", style="white", width=12)
    table.add_column("Category", width=10)
    table.add_column("Amount", justify="right", width=12)
    table.add_column("Description", style="dim white", min_width=15)

    for i, row in df.iterrows():
        date_str = (
            row["date"].strftime(CSV.FORMAT)
            if isinstance(row["date"], pd.Timestamp)
            else row["date"]
        )
        cat = row["category"]
        cat_color = "green" if cat == "Income" else "red"
        sign = "+" if cat == "Income" else "-"
        amt = f"{sign}${row['amount']:.2f}"
        desc = row.get("description", "") or ""
        table.add_row(
            str(i),
            date_str,
            f"[{cat_color}]{cat}[/{cat_color}]",
            f"[bold {cat_color}]{amt}[/bold {cat_color}]",
            desc,
        )

    console.print()
    console.print(table)
    console.print()


def print_summary(df):
    """Print income/expense summary with a styled panel and visual bar."""
    if df.empty:
        return

    total_income = df[df["category"] == "Income"]["amount"].sum()
    total_expense = df[df["category"] == "Expense"]["amount"].sum()
    net = total_income - total_expense
    net_color = "green" if net >= 0 else "red"
    net_icon = "▲" if net >= 0 else "▼"

    # Build a visual breakdown bar
    total = total_income + total_expense
    if total > 0:
        inc_pct = total_income / total * 100
        exp_pct = total_expense / total * 100
        bar_width = 30
        inc_bars = round(inc_pct / 100 * bar_width)
        exp_bars = bar_width - inc_bars
        bar_visual = f"[green]{'█' * inc_bars}[/green][red]{'█' * exp_bars}[/red]"
        bar_label = f"  [green]{inc_pct:.0f}% Income[/green]  [red]{exp_pct:.0f}% Expense[/red]"
    else:
        bar_visual = "[dim]No data[/dim]"
        bar_label = ""

    summary_text = (
        f"  [green]Income  :[/green]  [bold green]$ {total_income:>10.2f}[/bold green]\n"
        f"  [red]Expense :[/red]  [bold red]$ {total_expense:>10.2f}[/bold red]\n"
        f"  {'─' * 30}\n"
        f"  [bold {net_color}]Net {net_icon}   :  $ {net:>10.2f}[/bold {net_color}]\n\n"
        f"  {bar_visual}\n"
        f"{bar_label}"
    )

    summary_panel = Panel(
        summary_text,
        title="[bold white]💵 Financial Summary[/bold white]",
        title_align="left",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(summary_panel)


# ── Commands ─────────────────────────────────────────────────
def section_header(title, icon=""):
    """Print a styled section header."""
    console.print()
    console.print(Rule(f"[bold cyan]{icon}  {title}[/bold cyan]", style="cyan"))
    console.print()


def cmd_add():
    """Add a new transaction."""
    section_header("Add Transaction", "📝")
    CSV.initialize_csv()
    date = get_date("Date (dd-mm-yyyy) [Enter=today]", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)

    cat_color = "green" if category == "Income" else "red"
    console.print()
    success(f"Added: [{cat_color}]{category}[/{cat_color}] [green]${amount:.2f}[/green] on {date}")


def cmd_view():
    """View transactions in a date range."""
    section_header("View Transactions", "📋")
    start_date = get_date("Start date (dd-mm-yyyy)")
    end_date = get_date("End date (dd-mm-yyyy)")
    df = CSV.get_transactions(start_date, end_date)

    if df.empty:
        warn("No transactions found in that date range.")
    else:
        console.print(
            f"\n  Transactions from [bold]{start_date}[/bold] to [bold]{end_date}[/bold]"
        )
        print_table(df)
        print_summary(df)


def cmd_dashboard():
    """Show overall dashboard."""
    section_header("Dashboard", "📊")
    df = CSV.get_all_transactions()

    if df.empty:
        warn("No transactions yet. Add one to get started!")
        return

    total = len(df)
    info(f"Total transactions: [bold]{total}[/bold]")

    print_summary(df)

    # Show last 5 transactions
    console.print(Rule("[bold white]Recent Transactions[/bold white]", style="dim"))
    recent = df.tail(5)
    print_table(recent)


def cmd_plot():
    """Plot income vs expenses over time."""
    section_header("Plot", "📈")
    start_date = get_date("Start date (dd-mm-yyyy)")
    end_date = get_date("End date (dd-mm-yyyy)")
    df = CSV.get_transactions(start_date, end_date)

    if df.empty:
        warn("No transactions to plot.")
        return

    df = df.copy()
    df.set_index("date", inplace=True)

    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum(numeric_only=True)
        .reindex(df.index, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum(numeric_only=True)
        .reindex(df.index, fill_value=0)
    )

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    ax.plot(income_df.index, income_df["amount"], label="Income",
            color="#22c55e", linewidth=2, marker="o", markersize=4)
    ax.plot(expense_df.index, expense_df["amount"], label="Expense",
            color="#ef4444", linewidth=2, marker="o", markersize=4)
    ax.fill_between(income_df.index, income_df["amount"], alpha=0.15, color="#22c55e")
    ax.fill_between(expense_df.index, expense_df["amount"], alpha=0.15, color="#ef4444")

    ax.set_xlabel("Date", fontsize=11, color="#cdd6f4")
    ax.set_ylabel("Amount ($)", fontsize=11, color="#cdd6f4")
    ax.set_title("Income vs Expenses Over Time", fontsize=14, fontweight="bold",
                 color="#cdd6f4", pad=15)
    ax.legend(frameon=False, fontsize=10, labelcolor="#cdd6f4")
    ax.grid(True, alpha=0.15, color="#6c7086")
    ax.tick_params(colors="#6c7086")
    for spine in ax.spines.values():
        spine.set_color("#6c7086")

    plt.tight_layout()
    info("Displaying chart...")
    plt.show()
    success("Chart closed.")


def cmd_delete():
    """Delete a transaction by index."""
    section_header("Delete Transaction", "🗑️")
    df = CSV.get_all_transactions()

    if df.empty:
        warn("No transactions to delete.")
        return

    print_table(df)
    try:
        idx = int(colored_input("Enter row # to delete (or -1 to cancel)"))
        if idx == -1:
            info("Cancelled.")
            return
        if CSV.delete_entry(idx):
            success(f"Transaction #{idx} deleted.")
        else:
            error("Invalid row number.")
    except ValueError:
        error("Please enter a valid number.")


# ── Main Loop ────────────────────────────────────────────────
def main():
    CSV.initialize_csv()

    while True:
        clear_screen()
        console.print()
        console.print(BANNER)
        console.print(build_menu())

        choice = colored_input("Choose an option").strip()

        if choice == "1":
            cmd_add()
        elif choice == "2":
            cmd_view()
        elif choice == "3":
            cmd_dashboard()
        elif choice == "4":
            cmd_plot()
        elif choice == "5":
            cmd_delete()
        elif choice == "0":
            clear_screen()
            goodbye = Panel(
                Align.center(
                    "[bold cyan]Thanks for using Finance Tracker! Goodbye 👋[/bold cyan]"
                ),
                border_style="cyan",
                box=box.DOUBLE_EDGE,
                padding=(1, 2),
            )
            console.print()
            console.print(goodbye)
            console.print()
            break
        else:
            error("Invalid choice. Please enter 0-5.")

        if choice in ("1", "2", "3", "4", "5"):
            console.print()
            colored_input("Press Enter to continue...")


if __name__ == "__main__":
    main()