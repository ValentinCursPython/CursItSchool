from __future__ import annotations

import csv
from datetime import date, datetime
from typing import Optional, Iterable, Tuple, List

import matplotlib
matplotlib.use("TkAgg")  # backend pentru Tkinter
import matplotlib.pyplot as plt

import models


# ============== Utilitare interne ==============
def _iter_expenses(
    user_id: int,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Iterable[Tuple[int, int, float, str, str, str]]:
    """
    Itereaza cheltuielile userului, optional filtrate intre from_date si to_date (string YYYY-MM-DD).
    Returnează tuple: (id, user_id, amount, category, date, description)
    """
    rows = models.get_all_expenses(user_id)
    for r in rows:
        # r: (id, user_id, amount, category, date, description)
        if from_date and r[4] < from_date:
            continue
        if to_date and r[4] > to_date:
            continue
        yield r


# ============== Exporturi ==============
def export_csv(
    user_id: int,
    path: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Amount", "Category", "Date", "Description"])
        for r in _iter_expenses(user_id, from_date, to_date):
            writer.writerow([r[0], f"{r[2]:.2f}", r[3], r[4], r[5]])


def export_txt_summary(
    user_id: int,
    path: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> None:
    # sum pe total și pe categorie
    total = 0.0
    per_cat = {}
    rows = list(_iter_expenses(user_id, from_date, to_date))
    for _, _, amount, cat, _, _ in rows:
        total += float(amount)
        per_cat[cat] = per_cat.get(cat, 0.0) + float(amount)

    remaining, spent, start, end = models.get_cycle_remaining(user_id)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Expense Report\n")
        f.write("=================\n")
        if from_date or to_date:
            f.write(f"Period: {from_date or '-∞'} .. {to_date or '+∞'}\n")
        f.write(f"Generated at: {datetime.now().isoformat(sep=' ', timespec='seconds')}\n\n")
        f.write(f"Total expenses: {total:.2f}\n\n")
        f.write("By category:\n")
        for cat, val in sorted(per_cat.items(), key=lambda x: x[0].lower()):
            f.write(f"  - {cat}: {val:.2f}\n")
        f.write("\n")
        f.write(f"Current salary cycle: {start.isoformat()} → {end.isoformat()} (end exclusive)\n")
        f.write(f"Spent in cycle: {spent:.2f}\n")
        f.write(f"Remaining in cycle: {remaining:.2f}\n")


# ============== Grafice de bază ==============
def show_graph_window(
    parent,
    user_id: int,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> None:
    """
    2 grafice:
      1) Cheltuieli pe categorii (bar)
      2) Cheltuieli pe zile (linie)
    """
    rows = list(_iter_expenses(user_id, from_date, to_date))
    if not rows:
        _alert_no_data(parent, "Nu există cheltuieli pentru intervalul selectat.")
        return

    # sum pe categorie și pe zile
    per_cat = {}
    per_day = {}
    for _, _, amount, cat, d, _ in rows:
        per_cat[cat] = per_cat.get(cat, 0.0) + float(amount)
        per_day[d] = per_day.get(d, 0.0) + float(amount)

    # fig 1: categorii
    fig1 = plt.figure(figsize=(6.5, 4.2))
    fig1.canvas.manager.set_window_title("Cheltuieli pe categorii")
    cats = list(per_cat.keys())
    vals = [per_cat[c] for c in cats]
    plt.bar(cats, vals)
    plt.title("Cheltuieli pe categorii")
    plt.xlabel("Categorie")
    plt.ylabel("RON")
    plt.xticks(rotation=20)
    plt.tight_layout()

    # fig 2: pe zile (ordonăm după dată)
    fig2 = plt.figure(figsize=(7.2, 4.2))
    fig2.canvas.manager.set_window_title("Cheltuieli pe zile")
    days = sorted(per_day.keys())
    dvals = [per_day[d] for d in days]
    plt.plot(days, dvals, marker="o")
    plt.title("Cheltuieli pe zile")
    plt.xlabel("Dată")
    plt.ylabel("RON")
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.show(block=False)


def _alert_no_data(parent, msg: str):
    import tkinter.messagebox as mb
    mb.showinfo("Info", msg)


# ============== Grafic: Remaining vs Zile rămase ==============
def show_remaining_vs_days(parent, user_id: int) -> None:
    """
    Grafic clar, fără suprapuneri:
      - două bare side-by-side pe aceeași axă X:
          [Remaining (RON)] și [Days left]
      - etichete de valori desenate direct pe fiecare bară (în interior sau deasupra dacă e prea mică)
    """
    remaining, spent, start, end = models.get_cycle_remaining(user_id)
    today = date.today()
    days_left = max(0, (end - today).days)  # end este exclusiv

    labels = ["Remaining (RON)", "Days left"]
    values = [max(0.0, float(remaining)), float(days_left)]

    # Figură mai lată + margin sus pentru etichete deasupra
    fig = plt.figure(figsize=(7.5, 4.8))
    fig.canvas.manager.set_window_title("Remaining vs Days")
    ax = plt.gca()

    bars = ax.bar(labels, values)
    ax.set_title(
        f"Cycle: {start.isoformat()} → {end.isoformat()}  |  Spent: {float(spent):.2f} RON"
    )
    ax.set_ylabel("Values (RON / days)")

    # Stabilim un y_max cu puțin headroom pentru etichete
    y_max = max(values + [1.0]) * 1.25
    ax.set_ylim(0, y_max)

    # Etichete pe bare (folosim indexul barei pentru a ști ce format aplicăm)
    for i, (rect, val) in enumerate(zip(bars, values)):
        height = rect.get_height()
        label = labels[i]
        text = f"{int(val)}" if label == "Days left" else f"{val:.2f}"

        # Dacă bara e suficient de înaltă, afișăm textul în interior (alb), altfel deasupra (negru)
        if height > 0.18 * y_max:
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                height * 0.55,
                text,
                ha="center",
                va="center",
                color="white",
                fontsize=11,
            )
        else:
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.03 * y_max,
                text,
                ha="center",
                va="bottom",
                color="black",
                fontsize=11,
            )

    ax.margins(y=0.1)
    plt.tight_layout()
    plt.show(block=False)
