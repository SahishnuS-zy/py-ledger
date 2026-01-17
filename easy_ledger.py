import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

class EasyLedgerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyLedger - Personal Accounting")
        self.root.geometry("600x500")

        self.filename = "my_ledger.csv"
        self.ensure_file_exists()

        # UI Variables
        self.date_var = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        self.desc_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Expense")

        # Layout
        self.create_widgets()
        self.load_data()

    def ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Description", "Amount", "Type"])

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="New Transaction", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.date_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.desc_var).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Type:").grid(row=1, column=2, padx=5, pady=5)
        type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, values=["Income", "Expense"], state="readonly")
        type_combo.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Add Transaction", command=self.add_transaction).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side="left", padx=5)

        # Treeview (Table)
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Date", "Description", "Amount", "Type")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Balance Label
        self.balance_label = ttk.Label(self.root, text="Balance: 0.00", font=("Arial", 14, "bold"))
        self.balance_label.pack(pady=10)

    def add_transaction(self):
        date = self.date_var.get()
        desc = self.desc_var.get()
        amount = self.amount_var.get()
        trans_type = self.type_var.get()

        if not date or not desc or not amount:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            amount_float = float(amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number.")
            return

        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, desc, f"{amount_float:.2f}", trans_type])

        # Clear inputs
        self.desc_var.set("")
        self.amount_var.set("")
        
        self.load_data()

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data?"):
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Description", "Amount", "Type"])
            self.load_data()

    def load_data(self):
        # Clear current view
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_income = 0.0
        total_expense = 0.0

        if os.path.exists(self.filename):
            with open(self.filename, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header
                for row in reader:
                    if row:
                        self.tree.insert("", "end", values=row)
                        try:
                            amt = float(row[2])
                            if row[3] == "Income":
                                total_income += amt
                            elif row[3] == "Expense":
                                total_expense += amt
                        except ValueError:
                            pass

        balance = total_income - total_expense
        self.balance_label.config(text=f"Balance: {balance:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyLedgerApp(root)
    root.mainloop()
