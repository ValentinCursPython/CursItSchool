"""from database import init_db

def main():
    # Inițializăm baza de date
    init_db()
    print("Aplicația Expense Tracker a pornit!")

if __name__ == "__main__":
    main()"""

from database import init_db
from models import add_expense, get_all_expenses, update_expense, delete_expense

def main():
    init_db()

    # Adăugăm o cheltuială
    expense_id = add_expense(120.5, "Alimentatie", "2025-09-17", "Cumpărături supermarket")
    print(f"Cheltuială adăugată cu ID: {expense_id}")

    # Citim toate cheltuielile
    print("Lista cheltuielilor:")
    for exp in get_all_expenses():
        print(exp)

    # Actualizăm cheltuiala
    update_expense(expense_id, 150.0, "Alimentatie", "2025-09-17", "Cumpărături Mega Image")
    print("Cheltuială actualizată!")

    # Ștergem cheltuiala
    delete_expense(expense_id)
    print("Cheltuială ștearsă!")

if __name__ == "__main__":
    main()
