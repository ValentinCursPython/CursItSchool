import tkinter as tk
from tkinter import messagebox, ttk
from models import (
    create_user, authenticate_user,
    add_expense, get_all_expenses
)

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Login")
        self.root.geometry("600x400")

        self.current_user_id = None  # stocăm user_id după login

        self.show_login_screen()

    def clear_screen(self):
        """Șterge tot conținutul ferestrei."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- LOGIN SCREEN ---
    def show_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Login", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text="Email").pack()
        self.login_email_entry = tk.Entry(self.root, width=30)
        self.login_email_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.login_password_entry = tk.Entry(self.root, width=30, show="*")
        self.login_password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login_user).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.show_register_screen).pack()

    def login_user(self):
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get().strip()

        user_id = authenticate_user(email, password)
        if user_id:
            self.current_user_id = user_id
            messagebox.showinfo("Success", f"Welcome back, {email}!")
            self.show_main_app()
        else:
            messagebox.showerror("Error", "Invalid email or password.")

    # --- REGISTER SCREEN ---
    def show_register_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Register", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text="Email").pack()
        self.register_email_entry = tk.Entry(self.root, width=30)
        self.register_email_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.register_password_entry = tk.Entry(self.root, width=30, show="*")
        self.register_password_entry.pack()

        tk.Button(self.root, text="Create Account", command=self.register_user).pack(pady=5)
        tk.Button(self.root, text="Back to Login", command=self.show_login_screen).pack()

    def register_user(self):
        email = self.register_email_entry.get().strip()
        password = self.register_password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Warning", "Please enter both email and password.")
            return

        try:
            create_user(email, password)
            messagebox.showinfo("Success", "Account created! You can log in now.")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create account: {e}")

    # --- MAIN APP SCREEN ---
    def show_main_app(self):
        self.clear_screen()

        tk.Label(self.root, text="Expense Tracker", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Logged in as user ID: {self.current_user_id}").pack()

        # --- FORM ADD EXPENSE ---
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Amount").grid(row=0, column=0)
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Category").grid(row=1, column=0)
        self.category_entry = tk.Entry(form_frame)
        self.category_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Date (YYYY-MM-DD)").grid(row=2, column=0)
        self.date_entry = tk.Entry(form_frame)
        self.date_entry.grid(row=2, column=1)

        tk.Label(form_frame, text="Description").grid(row=3, column=0)
        self.desc_entry = tk.Entry(form_frame)
        self.desc_entry.grid(row=3, column=1)

        tk.Button(form_frame, text="Add Expense", command=self.add_expense_ui).grid(row=4, column=0, columnspan=2, pady=5)

        # --- TREEVIEW TO DISPLAY EXPENSES ---
        self.tree = ttk.Treeview(self.root, columns=("ID", "Amount", "Category", "Date", "Description"), show="headings")
        for col in ("ID", "Amount", "Category", "Date", "Description"):
            self.tree.heading(col, text=col)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=5)

        self.refresh_expenses()

    def add_expense_ui(self):
        """Adaugă cheltuială din formular în baza de date."""
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get().strip()
            date = self.date_entry.get().strip()
            description = self.desc_entry.get().strip()

            if not category or not date:
                messagebox.showwarning("Warning", "Category and Date are required.")
                return

            add_expense(self.current_user_id, amount, category, date, description)
            messagebox.showinfo("Success", "Expense added!")
            self.refresh_expenses()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    def refresh_expenses(self):
        """Încărcă cheltuielile în Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        expenses = get_all_expenses(self.current_user_id)
        for exp in expenses:
            self.tree.insert("", tk.END, values=exp)

    def logout(self):
        self.current_user_id = None
        self.show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
