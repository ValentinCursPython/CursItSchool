from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
from datetime import date, datetime
import os
import platform
import subprocess
from database import init_db
import models
from utils import show_graph_window, export_csv, export_txt_summary, show_remaining_vs_days

# --------------------- CONSTANTS ---------------------
CATEGORIES = ["Mâncare", "Transport", "Utilități", "Chirie", "Divertisment", "Altele"]
BG_COLOR = "#E6EEF5"
CARD_BG = "#FFFFFF"
CARD_SHADOW = "#D8E0EA"
ACCENT_BLUE = "#2563EB"
ACCENT_GREEN = "#10B981"
TEXT_MUTED = "#6B7280"


# --------------------- DATE PICKER ---------------------
class DatePicker(tk.Toplevel):
    def __init__(self, master, initial_date: date | None = None, on_selected=None):
        super().__init__(master)
        self.title("Select date")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.on_selected = on_selected
        today = initial_date or date.today()
        self.curr_year = today.year
        self.curr_month = today.month

        header = tk.Frame(self)
        header.pack(padx=8, pady=6, fill="x")
        tk.Button(header, text="◀", width=3, command=self.prev_month).pack(side="left")
        self.title_lbl = tk.Label(header, text="", font=("Arial", 11, "bold"))
        self.title_lbl.pack(side="left", expand=True)
        tk.Button(header, text="▶", width=3, command=self.next_month).pack(side="right")

        days_frame = tk.Frame(self)
        days_frame.pack(padx=8, pady=(0, 4))
        for wd in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            tk.Label(days_frame, text=wd, width=3, anchor="center").pack(side="left", padx=2)

        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(padx=8, pady=(0, 8))
        self.render_calendar()
        self.bind("<Escape>", lambda _e: self.destroy())

    def render_calendar(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        cal = calendar.Calendar(firstweekday=0)
        self.title_lbl.config(text=f"{calendar.month_name[self.curr_month]} {self.curr_year}")
        for week in cal.monthdayscalendar(self.curr_year, self.curr_month):
            row = tk.Frame(self.grid_frame)
            row.pack()
            for d in week:
                if d == 0:
                    tk.Label(row, text=" ", width=3).pack(side="left", padx=2, pady=2)
                else:
                    tk.Button(row, text=f"{d:02d}", width=3,
                              command=lambda dd=d: self.pick_day(dd)).pack(side="left", padx=2, pady=2)

    def prev_month(self):
        if self.curr_month == 1:
            self.curr_month, self.curr_year = 12, self.curr_year - 1
        else:
            self.curr_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.curr_month == 12:
            self.curr_month, self.curr_year = 1, self.curr_year + 1
        else:
            self.curr_month += 1
        self.render_calendar()

    def pick_day(self, d: int):
        chosen = date(self.curr_year, self.curr_month, d)
        if self.on_selected:
            self.on_selected(chosen)
        self.destroy()


# --------------------- MAIN APP ---------------------
class ExpenseApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_COLOR)
        init_db()
        models.ensure_default_admin()

        self.current_user_id: int | None = None
        self.current_is_admin: int = 0
        self.selected_expense_id: int | None = None

        # budget state
        self.payday_var = tk.IntVar(value=1)
        self.budget_var = tk.StringVar(value="0")
        self.remaining_var = tk.StringVar(value="Remaining amount: 0.00 RON")
        self.cycle_range_var = tk.StringVar(value="")

        # filter state (from/to date)
        self.filter_from_var = tk.StringVar(value="")
        self.filter_to_var = tk.StringVar(value="")

        self.show_login()

    # ---------- helpers ----------
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    @staticmethod
    def valid_date_str(s: str) -> bool:
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def safe_date_from_str(s: str) -> date:
        try:
            return datetime.strptime(s.strip(), "%Y-%m-%d").date()
        except Exception:
            return date.today()

    @staticmethod
    def darken(hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"

    def make_colored_button(self, parent, text, bg, command):
        btn = tk.Label(parent, text=text, bg=bg, fg="white", padx=16, pady=8, cursor="hand2")
        btn.bind("<Button-1>", lambda _e: command())
        btn.bind("<Enter>", lambda _e: btn.config(bg=self.darken(bg, 0.9)))
        btn.bind("<Leave>", lambda _e: btn.config(bg=bg))
        btn.pack(side="left", padx=6)
        return btn

    # ---------- LOGIN / REGISTER ----------
    def show_login(self):
        self.build_auth_card("login")

    def show_register(self):
        self.build_auth_card("register")

    def build_auth_card(self, mode="login"):
        self.clear()
        self.root.configure(bg=BG_COLOR)
        container = tk.Frame(self.root, bg=BG_COLOR)
        container.pack(expand=True, fill="both")

        shadow = tk.Frame(container, bg=CARD_SHADOW)
        shadow.place(relx=0.5, rely=0.5, anchor="center", width=460, height=420, x=6, y=6)

        card = tk.Frame(container, bg=CARD_BG)
        card.place(relx=0.5, rely=0.5, anchor="center", width=460, height=420)

        tk.Label(card, text="💰 Expense Tracker", bg=CARD_BG, fg="#111827",
                 font=("Helvetica", 18, "bold")).place(x=24, y=24)
        subtitle = "Login to your account" if mode == "login" else "Create a new account"
        tk.Label(card, text=subtitle, bg=CARD_BG, fg=TEXT_MUTED,
                 font=("Helvetica", 11)).place(x=24, y=58)

        y0 = 110
        tk.Label(card, text="Email", bg=CARD_BG, fg="#111827", font=("Helvetica", 11)).place(x=24, y=y0)
        entry_w = 412

        if mode == "login":
            self.login_email = tk.Entry(card, bd=1, relief="solid")
            self.login_email.place(x=24, y=y0+24, width=entry_w, height=32)
            tk.Label(card, text="Password", bg=CARD_BG, fg="#111827",
                     font=("Helvetica", 11)).place(x=24, y=y0+70)
            self.login_password = tk.Entry(card, show="*", bd=1, relief="solid")
            self.login_password.place(x=24, y=y0+94, width=entry_w-40, height=32)

            def toggle_pw():
                if self.login_password.cget("show") == "*":
                    self.login_password.config(show="")
                    pw_btn.config(text="🙈")
                else:
                    self.login_password.config(show="*")
                    pw_btn.config(text="👁")
            pw_btn = tk.Button(card, text="👁", bd=0, bg=CARD_BG, command=toggle_pw)
            pw_btn.place(x=24+entry_w-34, y=y0+94, width=30, height=32)

            btn_row = tk.Frame(card, bg=CARD_BG)
            btn_row.place(x=24, y=y0+150)
            self.make_colored_button(btn_row, "Login", ACCENT_BLUE, self.on_login)
            self.make_colored_button(btn_row, "Register", ACCENT_GREEN, self.show_register)

            fp = tk.Label(card, text="Forgot password?", fg=ACCENT_BLUE, bg=CARD_BG,
                          cursor="hand2", font=("Helvetica", 10, "underline"))
            fp.place(x=24, y=y0+200)
            fp.bind("<Button-1>", lambda _e: self.open_reset_password())

        else:
            self.reg_email = tk.Entry(card, bd=1, relief="solid")
            self.reg_email.place(x=24, y=y0+24, width=entry_w, height=32)
            tk.Label(card, text="Password", bg=CARD_BG, fg="#111827",
                     font=("Helvetica", 11)).place(x=24, y=y0+70)
            self.reg_password = tk.Entry(card, show="*", bd=1, relief="solid")
            self.reg_password.place(x=24, y=y0+94, width=entry_w-40, height=32)
            self.make_colored_button(card, "Create", ACCENT_GREEN, self.on_register)
            back = tk.Label(card, text="Back to Login", fg=ACCENT_BLUE, bg=CARD_BG,
                            cursor="hand2", font=("Helvetica", 10, "underline"))
            back.place(x=24, y=y0+200)
            back.bind("<Button-1>", lambda _e: self.show_login())

    def on_login(self):
        res = models.authenticate_user(self.login_email.get(), self.login_password.get())
        if not res:
            messagebox.showerror("Login failed", "Invalid email or password.")
            return
        uid, is_admin = res
        self.current_user_id, self.current_is_admin = uid, is_admin
        if is_admin:
            self.show_admin_dashboard()
        else:
            self.show_main()

    def on_register(self):
        try:
            models.create_user(self.reg_email.get(), self.reg_password.get())
            messagebox.showinfo("Success", "Account created. Please login.")
            self.show_login()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_reset_password(self):
        win = tk.Toplevel(self.root)
        win.title("Reset password")
        tk.Label(win, text="Enter your e-mail:").pack(pady=(10, 5))
        email_entry = tk.Entry(win, width=40)
        email_entry.pack(padx=10, pady=(0, 10))

        def do_reset():
            tmp = models.reset_password_local(email_entry.get())
            if not tmp:
                messagebox.showerror("Not found", "No account found for this e-mail.")
                return
            messagebox.showinfo("Temporary password",
                                f"A temporary password has been set:\n\n{tmp}\n\nUse it to log in.")
            win.destroy()

        tk.Button(win, text="Generate new password", command=do_reset).pack(pady=(0, 10))

    # ---------- MAIN (user) ----------
    def show_main(self):
        self.clear()
        self.root.configure(bg="SystemButtonFace")

        # top bar
        top = tk.Frame(self.root)
        top.pack(fill="x", pady=8, padx=10)
        tk.Label(top, text=f"Logged in (user_id={self.current_user_id})").pack(side="left")
        tk.Button(top, text="Logout", command=self.logout).pack(side="right")

        # ===== Budget panel =====
        budget = tk.LabelFrame(self.root, text="Budget")
        budget.pack(fill="x", padx=10, pady=(0, 8))

        # load settings
        payday, monthly_budget = models.get_user_settings(self.current_user_id)
        self.payday_var.set(payday)
        self.budget_var.set(f"{monthly_budget:.2f}")

        tk.Label(budget, text="Payday (1–31)").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.payday_cb = ttk.Combobox(budget, values=[str(i) for i in range(1, 32)],
                                      textvariable=self.payday_var, state="readonly", width=5)
        self.payday_cb.grid(row=0, column=1, padx=4, pady=6, sticky="w")

        tk.Label(budget, text="Monthly budget (RON)").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.budget_entry = tk.Entry(budget, textvariable=self.budget_var, width=12)
        self.budget_entry.grid(row=0, column=3, padx=4, pady=6, sticky="w")

        tk.Button(budget, text="Save", command=self.save_budget).grid(row=0, column=4, padx=10)

        self.remaining_label = tk.Label(budget, textvariable=self.remaining_var,
                                        font=("Arial", 11, "bold"), fg="#0f5132")
        self.remaining_label.grid(row=0, column=5, padx=12, sticky="w")

        self.cycle_label = tk.Label(budget, textvariable=self.cycle_range_var, fg="#6b7280")
        self.cycle_label.grid(row=0, column=6, padx=12, sticky="w")

        tk.Button(budget, text="📈 Remaining vs Days", command=self.open_remaining_chart).grid(row=0, column=7, padx=10)

        # form
        form = tk.LabelFrame(self.root, text="Expense")
        form.pack(fill="x", padx=10, pady=6)
        tk.Label(form, text="Amount").grid(row=0, column=0)
        self.amount_entry = tk.Entry(form, width=14)
        self.amount_entry.grid(row=0, column=1)
        tk.Label(form, text="Category").grid(row=0, column=2)
        self.category_var = tk.StringVar()
        self.category_cb = ttk.Combobox(form, textvariable=self.category_var, values=CATEGORIES, state="readonly", width=16)
        self.category_cb.grid(row=0, column=3)
        self.category_cb.set(CATEGORIES[0])
        tk.Label(form, text="Date").grid(row=1, column=0)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.date_entry = tk.Entry(form, textvariable=self.date_var, width=14)
        self.date_entry.grid(row=1, column=1)
        tk.Button(form, text="📅", command=self.open_datepicker_main).grid(row=1, column=2)
        tk.Label(form, text="Description").grid(row=1, column=3)
        self.desc_entry = tk.Entry(form, width=24)
        self.desc_entry.grid(row=1, column=4)

        # buttons
        btns = tk.Frame(form)
        btns.grid(row=2, column=0, columnspan=5, pady=6)
        tk.Button(btns, text="Add", command=self.add_expense_ui).pack(side="left", padx=4)
        tk.Button(btns, text="Update", command=self.update_expense_ui).pack(side="left", padx=4)
        tk.Button(btns, text="Delete", command=self.delete_expense_ui).pack(side="left", padx=4)
        tk.Button(btns, text="📊 Graphs", command=self.show_charts).pack(side="left", padx=4)
        tk.Button(btns, text="💾 Export report", command=self.export_report).pack(side="left", padx=4)

        # ===== Filters / Sort (cu From/To + date pickers) =====
        filt = tk.LabelFrame(self.root, text="Filters / Sort")
        filt.pack(fill="x", padx=10, pady=4)

        tk.Label(filt, text="Category").grid(row=0, column=0, padx=(0, 2))
        self.filter_cat = ttk.Combobox(filt, values=["All"] + CATEGORIES, state="readonly", width=16)
        self.filter_cat.grid(row=0, column=1, padx=(0, 8))
        self.filter_cat.set("All")

        tk.Label(filt, text="Sort by").grid(row=0, column=2)
        self.sort_by = ttk.Combobox(filt, values=["date", "amount", "category"], state="readonly", width=12)
        self.sort_by.grid(row=0, column=3, padx=(0, 8))
        self.sort_by.set("date")

        tk.Label(filt, text="Order").grid(row=0, column=4)
        self.sort_order = ttk.Combobox(filt, values=["ASC", "DESC"], state="readonly", width=8)
        self.sort_order.grid(row=0, column=5, padx=(0, 12))
        self.sort_order.set("ASC")

        # From / To
        tk.Label(filt, text="From").grid(row=0, column=6)
        self.filter_from_entry = tk.Entry(filt, textvariable=self.filter_from_var, width=12)
        self.filter_from_entry.grid(row=0, column=7)
        tk.Button(filt, text="📅", command=self.open_datepicker_from).grid(row=0, column=8, padx=(2, 10))

        tk.Label(filt, text="To").grid(row=0, column=9)
        self.filter_to_entry = tk.Entry(filt, textvariable=self.filter_to_var, width=12)
        self.filter_to_entry.grid(row=0, column=10)
        tk.Button(filt, text="📅", command=self.open_datepicker_to).grid(row=0, column=11, padx=(2, 10))

        tk.Button(filt, text="Apply", command=self.apply_filters).grid(row=0, column=12, padx=(6, 0))

        # table
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Amount", "Category", "Date", "Description"),
                                 show="headings", height=16)
        for col, w in (("ID", 50), ("Amount", 100), ("Category", 160), ("Date", 110), ("Description", 460)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)
        self.refresh_table()
        self.refresh_budget_badge()  # initial compute

    # ---------- Budget logic ----------
    def open_remaining_chart(self):
        show_remaining_vs_days(self.root, self.current_user_id)

    def save_budget(self):
        try:
            payday = int(self.payday_var.get())
            budget = float(self.budget_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid budget value.")
            return
        models.update_user_settings(self.current_user_id, payday, budget)
        self.refresh_budget_badge()
        messagebox.showinfo("Saved", "Budget settings saved.")

    def refresh_budget_badge(self):
        remaining, spent, start, end = models.get_cycle_remaining(self.current_user_id)
        self.remaining_var.set(f"Remaining amount: {remaining:.2f} RON (spent {spent:.2f})")
        self.cycle_range_var.set(f"{start.isoformat()} → {end.isoformat()}")

    # ---------- EXPORT ----------
    def export_report(self) -> None:
        today = date.today().strftime("%Y%m%d")

        # folosim filtrele curente dacă sunt completate
        dfrom = self.filter_from_var.get().strip() or None
        dto = self.filter_to_var.get().strip() or None
        # validam rapid formatul dacă sunt completate
        if dfrom and not self.valid_date_str(dfrom):
            messagebox.showerror("Error", "From date must be YYYY-MM-DD.")
            return
        if dto and not self.valid_date_str(dto):
            messagebox.showerror("Error", "To date must be YYYY-MM-DD.")
            return

        default_filename = f"expenses_report_{today}"
        file_path = filedialog.asksaveasfilename(
            title="Save report as...",
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        if file_path.lower().endswith(".csv"):
            txt_path = file_path[:-4] + ".txt"
        else:
            txt_path = file_path + ".txt"

        export_csv(self.current_user_id, file_path, dfrom, dto)
        export_txt_summary(self.current_user_id, txt_path, dfrom, dto)

        # deschide automat
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", file_path])
                subprocess.run(["open", txt_path])
            elif platform.system() == "Windows":
                os.startfile(file_path)
                os.startfile(txt_path)
            else:
                subprocess.run(["xdg-open", file_path])
                subprocess.run(["xdg-open", txt_path])
        except Exception as e:
            print(f"Could not open files automatically: {e}")

        messagebox.showinfo("Export done", f"Saved:\n\n• {file_path}\n• {txt_path}")

    # ---------- Date pickers ----------
    def open_datepicker_main(self):
        DatePicker(
            self.root,
            initial_date=self.safe_date_from_str(getattr(self, "date_var", tk.StringVar()).get()),
            on_selected=lambda d: self.date_var.set(d.strftime("%Y-%m-%d"))
        )

    def open_datepicker_from(self):
        initial = self.filter_from_var.get().strip()
        init_date = self.safe_date_from_str(initial) if initial else date.today()
        DatePicker(
            self.root,
            initial_date=init_date,
            on_selected=lambda d: self.filter_from_var.set(d.strftime("%Y-%m-%d"))
        )

    def open_datepicker_to(self):
        initial = self.filter_to_var.get().strip()
        init_date = self.safe_date_from_str(initial) if initial else date.today()
        DatePicker(
            self.root,
            initial_date=init_date,
            on_selected=lambda d: self.filter_to_var.set(d.strftime("%Y-%m-%d"))
        )

    # ---------- CRUD ----------
    def add_expense_ui(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Amount must be numeric.")
            return
        category, date_str, desc = self.category_var.get(), self.date_var.get().strip(), self.desc_entry.get().strip()
        if not self.valid_date_str(date_str):
            messagebox.showerror("Error", "Invalid date format (YYYY-MM-DD).")
            return
        models.add_expense(self.current_user_id, amount, category, date_str, desc)
        self.refresh_table()
        self.refresh_budget_badge()

    def update_expense_ui(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a row to update.")
            return
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Amount must be numeric.")
            return
        category, date_str, desc = self.category_var.get(), self.date_var.get().strip(), self.desc_entry.get().strip()
        if not self.valid_date_str(date_str):
            messagebox.showerror("Error", "Invalid date format (YYYY-MM-DD).")
            return
        exp_id = int(self.tree.item(sel[0], "values")[0])
        models.update_expense(exp_id, self.current_user_id, amount, category, date_str, desc)
        self.refresh_table()
        self.refresh_budget_badge()

    def delete_expense_ui(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a row to delete.")
            return
        exp_id = int(self.tree.item(sel[0], "values")[0])
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            models.delete_expense(exp_id, self.current_user_id)
            self.refresh_table()
            self.refresh_budget_badge()

    def on_row_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, vals[1])
        self.category_cb.set(vals[2])
        self.date_var.set(vals[3])
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, vals[4])

    # ---------- Filters / Sort ----------
    def apply_filters(self):
        cat = self.filter_cat.get()
        sort_field = self.sort_by.get()
        order = self.sort_order.get()

        dfrom = self.filter_from_var.get().strip()
        dto = self.filter_to_var.get().strip()

        # validari (daca sunt completate)
        if dfrom and not self.valid_date_str(dfrom):
            messagebox.showerror("Error", "From date must be YYYY-MM-DD.")
            return
        if dto and not self.valid_date_str(dto):
            messagebox.showerror("Error", "To date must be YYYY-MM-DD.")
            return
        if dfrom and dto and dfrom > dto:
            messagebox.showerror("Error", "From date cannot be after To date.")
            return

        rows = models.get_all_expenses(self.current_user_id)

        # category
        if cat != "All":
            rows = [r for r in rows if r[3] == cat]

        # date range (r[4] este YYYY-MM-DD, deci compararea funcționeaza)
        if dfrom:
            rows = [r for r in rows if r[4] >= dfrom]
        if dto:
            rows = [r for r in rows if r[4] <= dto]

        # sorting
        index_map = {"date": 4, "amount": 2, "category": 3}
        idx = index_map[sort_field]
        if sort_field == "amount":
            rows.sort(key=lambda r: float(r[idx]), reverse=(order == "DESC"))
        else:
            rows.sort(key=lambda r: r[idx], reverse=(order == "DESC"))

        # populate table
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[2], r[3], r[4], r[5]))

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = models.get_all_expenses(self.current_user_id)
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[2], r[3], r[4], r[5]))

    # ---------- Charts ----------
    def show_charts(self):
        show_graph_window(self.root, self.current_user_id, None, None)

    # ---------- Admin ----------
    def show_admin_dashboard(self) -> None:
        self.clear()
        self.root.configure(bg="SystemButtonFace")

        top = tk.Frame(self.root)
        top.pack(fill="x", pady=8, padx=10)
        tk.Label(top, text=f"Admin Dashboard (user_id={self.current_user_id})",
                 font=("Arial", 12, "bold")).pack(side="left")
        tk.Button(top, text="Logout", command=self.logout).pack(side="right")

        lf = tk.LabelFrame(self.root, text="All Users")
        lf.pack(fill="both", expand=True, padx=10, pady=8)
        cols = ("ID", "Email", "Created At", "Admin")
        self.users_tree = ttk.Treeview(lf, columns=cols, show="headings", height=18)
        for col, w in (("ID", 60), ("Email", 320), ("Created At", 220), ("Admin", 80)):
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=w, anchor="center")
        self.users_tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")

        act = tk.Frame(self.root)
        act.pack(fill="x", padx=10, pady=6)
        tk.Button(act, text="Refresh", command=self.refresh_users).pack(side="left")
        tk.Button(act, text="Promote to Admin", command=self.promote_selected_user).pack(side="left", padx=6)

        self.refresh_users()

    def refresh_users(self) -> None:
        for i in getattr(self, "users_tree").get_children():
            self.users_tree.delete(i)
        for uid, email, _hash, created, is_admin in models.list_users():
            self.users_tree.insert("", "end", values=(uid, email, created or "-", "Yes" if is_admin else "No"))

    def promote_selected_user(self) -> None:
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a user to promote.")
            return
        vals = self.users_tree.item(sel[0], "values")
        uid, email = int(vals[0]), vals[1]
        if messagebox.askyesno("Confirm", f"Promote {email} to admin?"):
            models.promote_user_to_admin(uid)
            self.refresh_users()
            messagebox.showinfo("Done", f"{email} is now admin.")

    # ---------- misc ----------
    def logout(self):
        self.current_user_id = None
        self.current_is_admin = 0
        self.show_login()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
