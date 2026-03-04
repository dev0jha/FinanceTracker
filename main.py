import pandas as pd
import csv
import os
from datetime import datetime
from data_entry import (
    get_amount, get_category, get_date, get_description,
    clear_screen, success, error, warn, info, colored_input,
    DATE_FORMAT, RESET, BOLD, DIM, RED, GREEN, YELLOW, CYAN, WHITE, MAGENTA,
)
import matplotlib.pyplot as plt


# ── Banner ───────────────────────────────────────────────────
BANNER = f"""
{CYAN}{BOLD}  ╔══════════════════════════════════════════════╗
  ║        💰  FINANCE TRACKER  💰              ║
  ║     Track your income & expenses easily      ║
  ╚══════════════════════════════════════════════╝{RESET}
"""

MENU = f"""
  {BOLD}{WHITE}┌──────────────────────────────────────┐{RESET}
  {BOLD}{WHITE}│{RESET}  {GREEN}1{RESET} ➜  Add Transaction                {BOLD}{WHITE}│{RESET}
  {BOLD}{WHITE}│{RESET}  {GREEN}2{RESET} ➜  View Transactions              {BOLD}{WHITE}│{RESET}
  {BOLD}{WHITE}│{RESET}  {GREEN}3{RESET} ➜  Dashboard (Summary)            {BOLD}{WHITE}│{RESET}
  {BOLD}{WHITE}│{RESET}  {GREEN}4{RESET} ➜  Plot Income vs Expense         {BOLD}{WHITE}│{RESET}
  {BOLD}{WHITE}│{RESET}  {GREEN}5{RESET} ➜  Delete Transaction             {BOLD}{WHITE}│{RESET}
  {BOLD}{WHITE}│{RESET}  {RED}0{RESET} ➜  Exit                           {BOLD}{WHITE}│{RESET}
  {BOLD}{WHITE}└──────────────────────────────────────┘{RESET}
"""


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
def separator():
    print(f"  {DIM}{'─' * 52}{RESET}")


def print_table(df):
    """Pretty-print a transactions dataframe."""
    if df.empty:
        warn("No transactions to display.")
        return

    separator()
    header = f"  {BOLD}{'#':>4}  {'Date':<12} {'Category':<10} {'Amount':>10}  {'Description'}{RESET}"
    print(header)
    separator()

    for i, row in df.iterrows():
        date_str = row["date"].strftime(CSV.FORMAT) if isinstance(row["date"], pd.Timestamp) else row["date"]
        cat = row["category"]
        cat_color = GREEN if cat == "Income" else RED
        sign = "+" if cat == "Income" else "-"
        amt = f"{sign}${row['amount']:.2f}"
        desc = row.get("description", "") or ""
        print(f"  {DIM}{i:>4}{RESET}  {date_str:<12} {cat_color}{cat:<10}{RESET} {cat_color}{amt:>10}{RESET}  {desc}")

    separator()


def print_summary(df):
    """Print income/expense summary for a dataframe."""
    if df.empty:
        return

    total_income = df[df["category"] == "Income"]["amount"].sum()
    total_expense = df[df["category"] == "Expense"]["amount"].sum()
    net = total_income - total_expense

    print()
    print(f"  {BOLD}{WHITE}Summary{RESET}")
    separator()
    print(f"    {GREEN}Income :  ${total_income:>10.2f}{RESET}")
    print(f"    {RED}Expense:  ${total_expense:>10.2f}{RESET}")
    separator()
    net_color = GREEN if net >= 0 else RED
    print(f"    {BOLD}{net_color}Net    :  ${net:>10.2f}{RESET}")
    print()


# ── Commands ─────────────────────────────────────────────────
def cmd_add():
    """Add a new transaction."""
    print(f"\n  {BOLD}{CYAN}── Add Transaction ──{RESET}\n")
    CSV.initialize_csv()
    date = get_date("Date (dd-mm-yyyy) [Enter=today]: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)

    cat_color = GREEN if category == "Income" else RED
    success(f"Added: {cat_color}{category}{RESET} {GREEN}${amount:.2f}{RESET} on {date}")


def cmd_view():
    """View transactions in a date range."""
    print(f"\n  {BOLD}{CYAN}── View Transactions ──{RESET}\n")
    start_date = get_date("Start date (dd-mm-yyyy): ")
    end_date = get_date("End date (dd-mm-yyyy): ")
    df = CSV.get_transactions(start_date, end_date)

    if df.empty:
        warn("No transactions found in that date range.")
    else:
        print(f"\n  Transactions from {BOLD}{start_date}{RESET} to {BOLD}{end_date}{RESET}")
        print_table(df)
        print_summary(df)


def cmd_dashboard():
    """Show overall dashboard."""
    print(f"\n  {BOLD}{CYAN}── Dashboard ──{RESET}\n")
    df = CSV.get_all_transactions()

    if df.empty:
        warn("No transactions yet. Add one to get started!")
        return

    total = len(df)
    info(f"Total transactions: {BOLD}{total}{RESET}")

    print_summary(df)

    # Show last 5 transactions
    print(f"  {BOLD}{WHITE}Recent Transactions{RESET}")
    recent = df.tail(5)
    print_table(recent)


def cmd_plot():
    """Plot income vs expenses over time."""
    print(f"\n  {BOLD}{CYAN}── Plot ──{RESET}\n")
    start_date = get_date("Start date (dd-mm-yyyy): ")
    end_date = get_date("End date (dd-mm-yyyy): ")
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

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="#22c55e", linewidth=2)
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="#ef4444", linewidth=2)
    plt.fill_between(income_df.index, income_df["amount"], alpha=0.1, color="#22c55e")
    plt.fill_between(expense_df.index, expense_df["amount"], alpha=0.1, color="#ef4444")
    plt.xlabel("Date")
    plt.ylabel("Amount ($)")
    plt.title("Income vs Expenses Over Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    info("Displaying chart...")
    plt.show()
    success("Chart closed.")


def cmd_delete():
    """Delete a transaction by index."""
    print(f"\n  {BOLD}{CYAN}── Delete Transaction ──{RESET}\n")
    df = CSV.get_all_transactions()

    if df.empty:
        warn("No transactions to delete.")
        return

    print_table(df)
    try:
        idx = int(colored_input("Enter row # to delete (or -1 to cancel): "))
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
        print(BANNER)
        print(MENU)

        choice = colored_input("Choose an option: ").strip()

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
            print(f"\n  {CYAN}{BOLD}Thanks for using Finance Tracker! Goodbye 👋{RESET}\n")
            break
        else:
            error("Invalid choice. Please enter 0-5.")

        if choice in ("1", "2", "3", "4", "5"):
            print()
            colored_input("Press Enter to continue...")


if __name__ == "__main__":
    main()