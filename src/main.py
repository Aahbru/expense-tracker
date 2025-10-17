# --------------------------
# Expense Tracker (CLI)
# Focus: clear functions + simple automation (auto-categorisation)
# File layout expected:
#   expense-tracker/
#     src/main.py  <- this file
#     data/expenses.csv  <- will be created on first save
# --------------------------

from pathlib import Path
from datetime import datetime  # we'll need this a bit later
import csv                     # we'll need this a bit later

# Global path for data file (relative to project root)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CSV_PATH = DATA_DIR / "expenses.csv"

def ensure_data_file_exists() -> None:
    """Create data/expenses.csv if missing (and create the folder too)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        CSV_PATH.write_text("date,amount,category,description\n", encoding="utf-8")

# --- Automation rules: simple keyword → category mapping
KEYWORD_RULES = {
    "tesco": "Groceries",
    "sainsbury": "Groceries",
    "aldi": "Groceries",
    "uber": "Transport",
    "tfl": "Transport",
    "bus": "Transport",
    "train": "Transport",
    "netflix": "Entertainment",
    "prime": "Entertainment",
    "cinema": "Entertainment",
    "gym": "Health",
    "pharmacy": "Health",
    "boots": "Health",
}

def ensure_data_file_exists():
    """Create data folder and CSV with header if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # CSV header: consistent schema
            writer.writerow(["date", "description", "amount", "category"])


def auto_categorise(description: str) -> str:
    """
    Basic automation: infer a category from the description using keyword rules.
    If no rule matches, default to 'Uncategorised'.
    """
    text = description.lower()
    for kw, cat in KEYWORD_RULES.items():
        if kw in text:
            return cat
    return "Uncategorised"


def add_expense(date_str: str, description: str, amount: float, category: str | None = None):
    """
    Append a single expense to the CSV. If category is not provided,
    use auto_categorise() to guess one.
    """
    ensure_data_file_exists()
    if category is None or not category.strip():
        category = auto_categorise(description)

    # Normalise/validate the date (store as YYYY-MM-DD)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    safe_date = date_obj.strftime("%Y-%m-%d")

    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([safe_date, description.strip(), f"{amount:.2f}", category])


def read_expenses() -> list[dict]:
    """
    Load all expenses from CSV into a list of dicts for easy processing.
    """
    ensure_data_file_exists()
    rows: list[dict] = []
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Convert amount to float once here
            r["amount"] = float(r["amount"])
            rows.append(r)
    return rows


def total_by_category() -> dict[str, float]:
    """
    Aggregate total spend per category.
    """
    totals: dict[str, float] = {}
    for r in read_expenses():
        cat = r["category"]
        totals[cat] = totals.get(cat, 0.0) + r["amount"]
    return totals


def list_expenses():
    """
    Print all expenses in a simple table.
    """
    rows = read_expenses()
    if not rows:
        print("No expenses recorded yet.")
        return

    print("\nDate        | Amount  | Category       | Description")
    print("-" * 62)
    for r in rows:
        print(f"{r['date']} | £{r['amount']:>6.2f} | {r['category']:<13} | {r['description']}")
    print()


def show_totals():
    """
    Print category totals, sorted by highest spend.
    """
    totals = total_by_category()
    if not totals:
        print("No expenses to summarise yet.")
        return

    print("\nTotal by category")
    print("-" * 20)
    for cat, val in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat:<15} £{val:,.2f}")

def _get_float(prompt: str) -> float:
    """Ask user for a number until they give a valid one."""
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")

def add_expense_from_prompt():
    """Collect details from the keyboard and save one expense."""
    print("\nAdd expense")
    print("-" * 20)
    date_str = input("Date (YYYY-MM-DD): ").strip()
    desc     = input("Description: ").strip()
    amount   = _get_float("Amount (e.g. 9.99): ")
    # Let automation choose category unless user types one
    cat_in   = input("Category (optional, press Enter to auto-categorise): ").strip() or None

    add_expense(date_str, desc, amount, cat_in)
    print("Saved ✅")

def main():
    """Simple command-line menu."""
    ensure_data_file_exists()

    while True:
        print("\nExpense Tracker")
        print("-" * 20)
        print("1) Add expense")
        print("2) List expenses")
        print("3) Show totals by category")
        print("4) Quit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            add_expense_from_prompt()
        elif choice == "2":
            list_expenses()
        elif choice == "3":
            show_totals()
        elif choice == "4":
            print("Bye!")
            break
        else:
            print("Invalid option. Please choose 1–4.")
    
# --- Entry point: only runs when you execute python src/main.py
if __name__ == "__main__":
    ensure_data_file_exists()   # cria a pasta/ficheiro data/expenses.csv se não existir
    main()                      # chama o menu principal