# Python Accounting System

A robust, double-entry accounting application built with Python and Tkinter. This desktop application provides a full graphical user interface for managing personal or small business finances, backed by a local SQLite database.

## Features

*   **Double-Entry Bookkeeping**: Enforces the fundamental accounting equation. Transactions must be balanced (Debits = Credits) before saving.
*   **Desktop GUI**: Clean, tabbed interface using `tkinter` for easy navigation.
*   **Dynamic Journal Entries**: Add unlimited lines to a single transaction (e.g., split expenses).
*   **Account Management**: Create and manage accounts with strict typing (Assets, Liabilities, Equity, Revenue, Expenses).
*   **Financial Reports**:
    *   **Income Statement (P&L)**: Real-time calculation of Net Income.
    *   **Balance Sheet**: Checks the financial health and verifies the accounting equation ($Assets = Liabilities + Equity$).
    *   **Ledger View**: Detailed transaction history for any specific account.
*   **Data Persistence**: All data is stored in a local `accounting.db` SQLite file.

## Requirements

*   **Python 3.x**
*   **Tkinter** (Usually included with standard Python installations)
*   **SQLite3** (Standard Python library)

## Installation

1.  **Clone or Download** this repository.
2.  Ensure you have Python installed.
3.  No external `pip` packages are required as it uses standard libraries.

## Usage

1.  **Run the Application**:
    ```bash
    python accounting.py
    ```
2.  **Navigation**: use the tabs at the top of the window.

### 1. Manage Accounts
*   Start here to set up your Chart of Accounts.
*   Enter a unique **Account Name** and select the **Type**.
*   Click **Create Account**.

### 2. Add Journal Entry
*   Enter the **Date** and **Description**.
*   Use the **Add Line** button to add as many rows as needed.
*   Select an **Account** for each line (type in the box to search).
    *   *Tip: If you type a new name here, the app will prompt you to create it instantly.*
*   Enter **Debit** and **Credit** amounts.
*   Click **Save Transaction**. The app will alert you if the transaction is unbalanced.

### 3. View Ledger
*   Select an account from the dropdown.
*   Click **Load** to see every transaction affecting that account, including a running balance.

### 4. Reports
*   **Income Statement**: Click "Generate" to see Revenue, Expenses, and Net Income.
*   **Balance Sheet**: Click "Generate" to see Assets, Liabilities, and Equity. The report automatically calculates Retained Earnings to ensure the sheet balances.

## Database Schema

The application automatically creates `accounting.db` with the following schema:
*   **`accounts`**: `id`, `name`, `type`
*   **`journal_entries`**: `id`, `transaction_id`, `date`, `description`, `account_id`, `debit`, `credit`

## License
MIT License
