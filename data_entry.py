from datetime import datetime
import os

DATE_FORMAT = "%d-%m-%Y"
CATEGORIES = {"I": "Income", "E": "Expense"}

# ── ANSI Colors ──────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def colored_input(prompt):
    """Styled input prompt."""
    return input(f"  {CYAN}{BOLD}> {RESET}{prompt}")


def success(msg):
    print(f"  {GREEN}{BOLD}✓ {msg}{RESET}")


def error(msg):
    print(f"  {RED}{BOLD}✗ {msg}{RESET}")


def warn(msg):
    print(f"  {YELLOW}{BOLD}! {msg}{RESET}")


def info(msg):
    print(f"  {CYAN}ℹ {msg}{RESET}")


def get_date(prompt, allow_default=False):
    date_str = colored_input(prompt)
    if allow_default and not date_str:
        today = datetime.today().strftime(DATE_FORMAT)
        info(f"Using today's date: {today}")
        return today

    try:
        valid_date = datetime.strptime(date_str, DATE_FORMAT)
        return valid_date.strftime(DATE_FORMAT)
    except ValueError:
        error("Invalid date format. Please use dd-mm-yyyy")
        return get_date(prompt, allow_default)


def get_amount():
    try:
        amount = float(colored_input("Amount: $"))
        if amount <= 0:
            raise ValueError("Amount must be a positive value.")
        return amount
    except ValueError as e:
        error(str(e))
        return get_amount()


def get_category():
    print(f"\n  {DIM}Categories:{RESET}")
    print(f"    {GREEN}[I]{RESET} Income    {RED}[E]{RESET} Expense")
    category = colored_input("Category: ").upper()
    if category in CATEGORIES:
        return CATEGORIES[category]

    error("Invalid choice. Enter 'I' or 'E'.")
    return get_category()


def get_description():
    return colored_input("Description (optional): ")