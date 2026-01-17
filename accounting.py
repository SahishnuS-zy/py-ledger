import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime

DB_NAME = "accounting.db"
ACCOUNT_TYPES = ["Asset", "Liability", "Equity", "Revenue", "Expense"]

# --- Database Logic (Adapted) ---

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            account_id INTEGER NOT NULL,
            debit REAL DEFAULT 0,
            credit REAL DEFAULT 0,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    ''')
    conn.commit()
    conn.close()

def get_accounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type FROM accounts ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_account(name, type_):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO accounts (name, type) VALUES (?, ?)", (name, type_))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def save_transaction(date, desc, lines):
    # lines is list of dicts: {account_id, debit, credit}
    transaction_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for line in lines:
            cursor.execute('''
                INSERT INTO journal_entries (transaction_id, date, description, account_id, debit, credit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction_id, date, desc, line['account_id'], line['debit'], line['credit']))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        conn.rollback()
        return False
    finally:
        conn.close()

# --- GUI Application ---

class AccountingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Accounting System")
        self.geometry("900x600")
        
        init_db()
        
        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_entry = ttk.Frame(self.notebook)
        self.tab_ledger = ttk.Frame(self.notebook)
        self.tab_pl = ttk.Frame(self.notebook)
        self.tab_bs = ttk.Frame(self.notebook)
        self.tab_accounts = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_entry, text="Add Journal Entry")
        self.notebook.add(self.tab_ledger, text="View Ledger")
        self.notebook.add(self.tab_pl, text="Income Statement")
        self.notebook.add(self.tab_bs, text="Balance Sheet")
        self.notebook.add(self.tab_accounts, text="Manage Accounts")
        
        # Build Tabs
        self.build_entry_tab()
        self.build_ledger_tab()
        self.build_pl_tab()
        self.build_bs_tab()
        self.build_accounts_tab()

    # --- Tab 1: Journal Entry ---
    def build_entry_tab(self):
        main_frame = ttk.Frame(self.tab_entry, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=5)
        
        ttk.Label(header_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.entry_date = ttk.Entry(header_frame, width=15)
        self.entry_date.insert(0, str(datetime.date.today()))
        self.entry_date.pack(side="left", padx=5)
        
        ttk.Label(header_frame, text="Description:").pack(side="left", padx=5)
        self.entry_desc = ttk.Entry(header_frame, width=40)
        self.entry_desc.pack(side="left", padx=5, fill="x", expand=True)

        # Lines Area (Scrollable simplified for this demo, usually needs Canvas)
        # We will use a dedicated Frame for rows
        self.lines_frame = ttk.LabelFrame(main_frame, text="Transaction Lines")
        self.lines_frame.pack(fill="both", expand=True, pady=10)
        
        self.line_widgets = [] # List of row dicts {combo, debit, credit}
        
        # Add initial 2 lines
        self.add_line_row()
        self.add_line_row()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="+ Add Line", command=self.add_line_row).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Transaction", command=self.submit_transaction).pack(side="right", padx=5)

    def add_line_row(self):
        row_frame = ttk.Frame(self.lines_frame)
        row_frame.pack(fill="x", pady=2, padx=5)
        
        accounts = get_accounts()
        acc_names = [a['name'] for a in accounts]
        
        combo = ttk.Combobox(row_frame, values=acc_names, width=25)
        combo.pack(side="left", padx=5)
        combo.bind("<<ComboboxSelected>>", lambda e: self.check_new_account(combo))
        combo.bind("<Return>", lambda e: self.check_new_account(combo))
        
        ttk.Label(row_frame, text="Dr:").pack(side="left")
        dr_entry = ttk.Entry(row_frame, width=10)
        dr_entry.pack(side="left", padx=2)
        dr_entry.insert(0, "0.0")
        
        ttk.Label(row_frame, text="Cr:").pack(side="left")
        cr_entry = ttk.Entry(row_frame, width=10)
        cr_entry.pack(side="left", padx=2)
        cr_entry.insert(0, "0.0")
        
        self.line_widgets.append({"combo": combo, "dr": dr_entry, "cr": cr_entry})

    def check_new_account(self, combo):
        name = combo.get().strip().title()
        if not name: return
        accounts = get_accounts()
        existing = [a['name'] for a in accounts]
        
        if name not in existing:
            # Prompt for type
            type_win = tk.Toplevel(self)
            type_win.title("New Account Type")
            ttk.Label(type_win, text=f"Select type for '{name}':").pack(padx=10, pady=10)
            
            selected_type = tk.StringVar(value=ACCOUNT_TYPES[0])
            for t in ACCOUNT_TYPES:
                ttk.Radiobutton(type_win, text=t, variable=selected_type, value=t).pack(anchor="w", padx=20)
            
            def confirm():
                create_account(name, selected_type.get())
                self.refresh_account_combos()
                type_win.destroy()
                combo.set(name)
                
            ttk.Button(type_win, text="Create", command=confirm).pack(pady=10)
            self.wait_window(type_win)

    def refresh_account_combos(self):
        accounts = get_accounts()
        names = [a['name'] for a in accounts]
        for row in self.line_widgets:
            row['combo']['values'] = names

    def submit_transaction(self):
        date = self.entry_date.get()
        desc = self.entry_desc.get()
        if not desc:
            messagebox.showerror("Error", "Description required.")
            return
            
        lines_data = []
        total_dr = 0.0
        total_cr = 0.0
        
        accounts = get_accounts()
        acc_map = {a['name']: a['id'] for a in accounts}
        
        for row in self.line_widgets:
            name = row['combo'].get().strip().title()
            if not name: continue # Skip empty lines
            
            if name not in acc_map:
                messagebox.showerror("Error", f"Account '{name}' does not exist.")
                return

            try:
                dr = float(row['dr'].get())
                cr = float(row['cr'].get())
            except ValueError:
                messagebox.showerror("Error", "Invalid number.")
                return
            
            if dr == 0 and cr == 0: continue
            
            lines_data.append({'account_id': acc_map[name], 'debit': dr, 'credit': cr})
            total_dr += dr
            total_cr += cr
            
        if not lines_data:
            messagebox.showwarning("Warning", "No entries.")
            return

        if abs(total_dr - total_cr) > 0.01:
            messagebox.showerror("Unbalanced", f"Debits: {total_dr:.2f}\nCredits: {total_cr:.2f}\nDiff: {total_dr-total_cr:.2f}")
            return
            
        if save_transaction(date, desc, lines_data):
            messagebox.showinfo("Success", "Transaction Saved.")
            # Reset
            self.entry_desc.delete(0, tk.END)
            for row in self.line_widgets:
                row['combo'].set('')
                row['dr'].delete(0, tk.END); row['dr'].insert(0, "0.0")
                row['cr'].delete(0, tk.END); row['cr'].insert(0, "0.0")
            # Refresh other tabs if needed (simple way: user clicks refresh button there)
        else:
            messagebox.showerror("Error", "Database error.")

    # --- Tab 2: Ledger ---
    def build_ledger_tab(self):
        frame = ttk.Frame(self.tab_ledger, padding="10")
        frame.pack(fill="both", expand=True)
        
        ctrl_frame = ttk.Frame(frame)
        ctrl_frame.pack(fill="x", pady=5)
        
        ttk.Label(ctrl_frame, text="Account:").pack(side="left")
        self.ledger_combo = ttk.Combobox(ctrl_frame, postcommand=self.update_ledger_combo)
        self.ledger_combo.pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Load", command=self.load_ledger).pack(side="left")
        
        cols = ("Date", "Description", "Debit", "Credit", "Balance")
        self.ledger_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.ledger_tree.heading(c, text=c)
            self.ledger_tree.column(c, width=100)
        
        self.ledger_tree.pack(fill="both", expand=True, pady=5)

    def update_ledger_combo(self):
        self.ledger_combo['values'] = [a['name'] for a in get_accounts()]

    def load_ledger(self):
        name = self.ledger_combo.get()
        if not name: return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM accounts WHERE name = ?", (name,))
        res = cursor.fetchone()
        if not res: return
        acc_id = res['id']
        
        for i in self.ledger_tree.get_children():
            self.ledger_tree.delete(i)
            
        cursor.execute("SELECT date, description, debit, credit FROM journal_entries WHERE account_id=? ORDER BY date, id", (acc_id,))
        rows = cursor.fetchall()
        
        bal = 0.0
        for r in rows:
            bal += (r['debit'] - r['credit'])
            self.ledger_tree.insert("", "end", values=(r['date'], r['description'], f"{r['debit']:.2f}", f"{r['credit']:.2f}", f"{bal:.2f}"))
        conn.close()

    # --- Tab 3: Income Statement ---
    def build_pl_tab(self):
        frame = ttk.Frame(self.tab_pl, padding="10")
        frame.pack(fill="both", expand=True)
        ttk.Button(frame, text="Generate Profit & Loss", command=self.load_pl).pack(pady=5)
        
        self.pl_text = tk.Text(frame, width=80, height=20)
        self.pl_text.pack(fill="both", expand=True)

    def load_pl(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        self.pl_text.delete(1.0, tk.END)
        self.pl_text.insert(tk.END, "=== INCOME STATEMENT ===\n\n")
        
        # Revenue
        cursor.execute("SELECT a.name, SUM(j.credit)-SUM(j.debit) as bal FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Revenue' GROUP BY a.id")
        revs = cursor.fetchall()
        
        total_rev = 0.0
        self.pl_text.insert(tk.END, "REVENUE:\n")
        for r in revs:
            amt = r['bal'] or 0
            total_rev += amt
            self.pl_text.insert(tk.END, f"{r['name']:<30} : {amt:10.2f}\n")
        self.pl_text.insert(tk.END, f"{'TOTAL REVENUE':<30} : {total_rev:10.2f}\n\n")
        
        # Expenses
        cursor.execute("SELECT a.name, SUM(j.debit)-SUM(j.credit) as bal FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Expense' GROUP BY a.id")
        exps = cursor.fetchall()
        
        total_exp = 0.0
        self.pl_text.insert(tk.END, "EXPENSES:\n")
        for r in exps:
            amt = r['bal'] or 0
            total_exp += amt
            self.pl_text.insert(tk.END, f"{r['name']:<30} : {amt:10.2f}\n")
        self.pl_text.insert(tk.END, f"{'TOTAL EXPENSES':<30} : {total_exp:10.2f}\n\n")
        
        net_inc = total_rev - total_exp
        self.pl_text.insert(tk.END, "-"*45 + "\n")
        self.pl_text.insert(tk.END, f"{'NET INCOME':<30} : {net_inc:10.2f}\n")
        conn.close()

    # --- Tab 4: Balance Sheet ---
    def build_bs_tab(self):
        frame = ttk.Frame(self.tab_bs, padding="10")
        frame.pack(fill="both", expand=True)
        ttk.Button(frame, text="Generate Balance Sheet", command=self.load_bs).pack(pady=5)
        
        self.bs_text = tk.Text(frame, width=80, height=20)
        self.bs_text.pack(fill="both", expand=True)

    def load_bs(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get Net Income first
        cursor.execute("SELECT SUM(credit)-SUM(debit) FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Revenue'")
        rev = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(debit)-SUM(credit) FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Expense'")
        exp = cursor.fetchone()[0] or 0
        net_inc = rev - exp
        
        self.bs_text.delete(1.0, tk.END)
        self.bs_text.insert(tk.END, "=== BALANCE SHEET ===\n\n")
        
        # Assets
        cursor.execute("SELECT a.name, SUM(j.debit)-SUM(j.credit) FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Asset' GROUP BY a.id")
        assets = cursor.fetchall()
        total_assets = 0.0
        self.bs_text.insert(tk.END, "ASSETS:\n")
        for r in assets:
            amt = r[1] or 0
            total_assets += amt
            self.bs_text.insert(tk.END, f"{r[0]:<30} : {amt:10.2f}\n")
        self.bs_text.insert(tk.END, f"{'TOTAL ASSETS':<30} : {total_assets:10.2f}\n\n")
        
        # Liabilities
        cursor.execute("SELECT a.name, SUM(j.credit)-SUM(j.debit) FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Liability' GROUP BY a.id")
        liabs = cursor.fetchall()
        total_liabs = 0.0
        self.bs_text.insert(tk.END, "LIABILITIES:\n")
        for r in liabs:
            amt = r[1] or 0
            total_liabs += amt
            self.bs_text.insert(tk.END, f"{r[0]:<30} : {amt:10.2f}\n")
        self.bs_text.insert(tk.END, f"{'TOTAL LIABILITIES':<30} : {total_liabs:10.2f}\n\n")

        # Equity
        cursor.execute("SELECT a.name, SUM(j.credit)-SUM(j.debit) FROM accounts a JOIN journal_entries j ON a.id=j.account_id WHERE a.type='Equity' GROUP BY a.id")
        eqs = cursor.fetchall()
        total_eq = 0.0
        self.bs_text.insert(tk.END, "EQUITY:\n")
        for r in eqs:
            amt = r[1] or 0
            total_eq += amt
            self.bs_text.insert(tk.END, f"{r[0]:<30} : {amt:10.2f}\n")
        
        self.bs_text.insert(tk.END, f"{'Retained Earnings (Net Inc)':<30} : {net_inc:10.2f}\n")
        total_eq += net_inc
        self.bs_text.insert(tk.END, f"{'TOTAL EQUITY':<30} : {total_eq:10.2f}\n\n")
        
        self.bs_text.insert(tk.END, "-"*45 + "\n")
        self.bs_text.insert(tk.END, f"ASSETS: {total_assets:.2f}  |  LIAB+EQUITY: {total_liabs + total_eq:.2f}\n")
        
        if abs(total_assets - (total_liabs + total_eq)) < 0.01:
            self.bs_text.insert(tk.END, "STATUS: BALANCED\n")
        else:
            self.bs_text.insert(tk.END, "STATUS: UNBALANCED\n")
        conn.close()

    # --- Tab 5: Manage Accounts ---
    def build_accounts_tab(self):
        frame = ttk.Frame(self.tab_accounts, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(frame, text="Create New Account", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form Container
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)
        
        # Name
        ttk.Label(form_frame, text="Account Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_acc_name = ttk.Entry(form_frame, width=30)
        self.new_acc_name.grid(row=0, column=1, padx=5, pady=5)
        
        # Type
        ttk.Label(form_frame, text="Account Type:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_acc_type = ttk.Combobox(form_frame, values=ACCOUNT_TYPES, state="readonly", width=27)
        self.new_acc_type.grid(row=1, column=1, padx=5, pady=5)
        self.new_acc_type.current(0)
        
        # Button
        ttk.Button(frame, text="Create Account", command=self.submit_create_account).pack(pady=20)

    def submit_create_account(self):
        name = self.new_acc_name.get().strip().title()
        type_ = self.new_acc_type.get()
        
        if not name:
            messagebox.showerror("Error", "Account Name is required.")
            return
            
        if not type_ or type_ not in ACCOUNT_TYPES:
            messagebox.showerror("Error", "Invalid Account Type.")
            return
            
        result = create_account(name, type_)
        
        if result:
            messagebox.showinfo("Success", f"Account '{name}' created successfully.")
            self.new_acc_name.delete(0, tk.END)
            self.new_acc_type.current(0)
            
            # Refresh other tabs
            self.refresh_account_combos()
            self.update_ledger_combo()
        else:
            messagebox.showerror("Error", f"Account '{name}' already exists.")

if __name__ == "__main__":
    app = AccountingApp()
    app.mainloop()
