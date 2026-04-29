
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер расходов")
        self.root.geometry("950x600")

        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()
        self.categories = ["Еда", "Транспорт", "Развлечения", "Жилье", "Коммунальные", "Другое"]

        # --- Стили --- 
        style = ttk.Style(self.root)
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'))

        # --- Основные фреймы --- 
        input_frame = ttk.LabelFrame(root, text="Добавить новый расход", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(root, text="Фильтры и статистика", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tree_frame = ttk.Frame(root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # --- Поля ввода --- 
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, width=20)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set(self.categories[0])

        ttk.Label(input_frame, text="Дата:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_button.grid(row=0, column=6, padx=10, pady=5, sticky="e")
        input_frame.grid_columnconfigure(6, weight=1)

        # --- Фильтры и статистика ---
        ttk.Label(filter_frame, text="От:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_filter = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.start_date_filter.grid(row=0, column=1, padx=5)
        self.start_date_filter.set_date(None)

        ttk.Label(filter_frame, text="До:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_filter = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.end_date_filter.grid(row=0, column=3, padx=5)
        self.end_date_filter.set_date(None)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=4, padx=5, pady=5)
        self.category_filter = ttk.Combobox(filter_frame, values=["Все"] + self.categories, width=15)
        self.category_filter.grid(row=0, column=5, padx=5)
        self.category_filter.set("Все")

        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters)
        filter_button.grid(row=0, column=6, padx=10)
        
        self.total_label = ttk.Label(filter_frame, text="Итого: 0.00", font=("Calibri", 12, "bold"))
        self.total_label.grid(row=0, column=7, padx=20, sticky="e")
        filter_frame.grid_columnconfigure(7, weight=1)

        # --- Таблица расходов --- 
        self.tree = ttk.Treeview(tree_frame, columns=("date", "category", "amount"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        self.tree.column("date", anchor=tk.W, width=100)
        self.tree.column("category", anchor=tk.W, width=150)
        self.tree.column("amount", anchor=tk.E, width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.populate_tree(self.expenses)

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_combo.get()
        date_str = self.date_entry.get()

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
                return
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Сумма должна быть числом.")
            return

        if not category:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, выберите категорию.")
            return
            
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД.")
            return

        new_expense = {"date": date_str, "category": category, "amount": amount}
        self.expenses.append(new_expense)
        self.save_expenses()
        self.apply_filters() # Обновляем с учетом фильтров
        self.amount_entry.delete(0, tk.END)

    def populate_tree(self, expenses_to_show):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        total = 0
        # Сортируем по дате для наглядности
        sorted_expenses = sorted(expenses_to_show, key=lambda x: x['date'], reverse=True)

        for expense in sorted_expenses:
            self.tree.insert("", tk.END, values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))
            total += expense['amount']
        
        self.total_label.config(text=f"Итого: {total:.2f}")

    def apply_filters(self):
        start_date_str = self.start_date_filter.get()
        end_date_str = self.end_date_filter.get()
        category = self.category_filter.get()

        filtered_expenses = self.expenses

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e['date'], '%Y-%m-%d').date() >= start_date]
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e['date'], '%Y-%m-%d').date() <= end_date]
        except ValueError:
            messagebox.showerror("Ошибка даты", "Некорректный формат даты в фильтре.")
            return

        if category != "Все":
            filtered_expenses = [e for e in filtered_expenses if e["category"] == category]

        self.populate_tree(filtered_expenses)

    def load_expenses(self):
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showwarning("Ошибка загрузки", "Не удалось загрузить данные. Файл может быть поврежден.")
            return []

    def save_expenses(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
