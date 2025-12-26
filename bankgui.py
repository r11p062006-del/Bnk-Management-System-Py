import json
import random
import os
from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox, ttk


# ======== Account Base Class ========
class Account(ABC):
    def __init__(self, account_number: str, account_holder_id: str, initial_balance: float = 0.0):
        self._account_number = account_number
        self._account_holder_id = account_holder_id
        self._balance = initial_balance

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def account_holder_id(self) -> str:
        return self._account_holder_id

    @abstractmethod
    def deposit(self, amount: float) -> bool:
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        pass

    def display_details(self) -> str:
        return f"Acc No: {self._account_number}, Balance: ${self._balance:.2f}"

    def to_dict(self) -> dict:
        return {
            'account_number': self._account_number,
            'account_holder_id': self._account_holder_id,
            'balance': self._balance,
            'type': 'account'
        }


# ======== SavingsAccount Class ========
class SavingsAccount(Account):
    def __init__(self, account_number: str, account_holder_id: str,
                 initial_balance: float = 0.0, interest_rate: float = 0.01):
        super().__init__(account_number, account_holder_id, initial_balance)
        self._interest_rate = interest_rate if interest_rate >= 0 else 0.01

    @property
    def interest_rate(self) -> float:
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, value: float):
        if value < 0:
            raise ValueError("Interest rate cannot be negative.")
        self._interest_rate = value

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self._balance += amount
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self._balance:
            return False
        self._balance -= amount
        return True

    def apply_interest(self) -> None:
        self._balance += self._balance * self._interest_rate

    def display_details(self) -> str:
        base = super().display_details()
        return f"{base}, Interest Rate: {self._interest_rate * 100:.2f}%"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            'interest_rate': self._interest_rate,
            'type': 'savings'
        })
        return d


# ======== CheckingAccount Class ========
class CheckingAccount(Account):
    def __init__(self, account_number: str, account_holder_id: str,
                 initial_balance: float = 0.0, overdraft_limit: float = 0.0):
        super().__init__(account_number, account_holder_id, initial_balance)
        self._overdraft_limit = overdraft_limit if overdraft_limit >= 0 else 0.0

    @property
    def overdraft_limit(self) -> float:
        return self._overdraft_limit

    @overdraft_limit.setter
    def overdraft_limit(self, value: float):
        if value < 0:
            raise ValueError("Overdraft limit cannot be negative.")
        self._overdraft_limit = value

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self._balance += amount
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if (self._balance - amount) < -self._overdraft_limit:
            return False
        self._balance -= amount
        return True

    def display_details(self) -> str:
        base = super().display_details()
        return f"{base}, Overdraft Limit: ${self._overdraft_limit:.2f}"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            'overdraft_limit': self._overdraft_limit,
            'type': 'checking'
        })
        return d
# ======== Customer Class ========
class Customer:
    def __init__(self, customer_id: str, name: str, address: str):
        self._customer_id = customer_id
        self._name = name
        self._address = address
        self._account_numbers = []

    @property
    def customer_id(self) -> str:
        return self._customer_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value

    @property
    def account_numbers(self) -> list:
        return list(self._account_numbers)

    def add_account_number(self, account_number: str) -> None:
        if account_number not in self._account_numbers:
            self._account_numbers.append(account_number)

    def remove_account_number(self, account_number: str) -> None:
        if account_number in self._account_numbers:
            self._account_numbers.remove(account_number)

    def display_details(self) -> str:
        return (f"Customer ID: {self._customer_id}, Name: {self._name}, Address: {self._address}, "
                f"Accounts: {len(self._account_numbers)}")

    def to_dict(self) -> dict:
        return {
            'customer_id': self._customer_id,
            'name': self._name,
            'address': self._address,
            'account_numbers': self._account_numbers
        }


# ======== Bank Class ========
class Bank:
    def __init__(self, customer_file='customers.json', account_file='accounts.json'):
        self._customers = {}
        self._accounts = {}
        self._customer_file = customer_file
        self._account_file = account_file
        self._load_data()

    def _load_data(self) -> None:
        # Load customers
        try:
            with open(self._customer_file, 'r') as f:
                customer_data = json.load(f)
            for cust_id, cust_dict in customer_data.items():
                customer = Customer(cust_dict['customer_id'], cust_dict['name'], cust_dict['address'])
                for acc_num in cust_dict.get('account_numbers', []):
                    customer.add_account_number(acc_num)
                self._customers[cust_id] = customer
        except (FileNotFoundError, json.JSONDecodeError):
            self._customers = {}

        # Load accounts
        try:
            with open(self._account_file, 'r') as f:
                account_data = json.load(f)
            for acc_num, acc_dict in account_data.items():
                acc_type = acc_dict.get('type')
                if acc_type == 'savings':
                    account = SavingsAccount(
                        acc_dict['account_number'],
                        acc_dict['account_holder_id'],
                        acc_dict['balance'],
                        acc_dict.get('interest_rate', 0.01)
                    )
                elif acc_type == 'checking':
                    account = CheckingAccount(
                        acc_dict['account_number'],
                        acc_dict['account_holder_id'],
                        acc_dict['balance'],
                        acc_dict.get('overdraft_limit', 0.0)
                    )
                else:
                    continue
                self._accounts[acc_num] = account
        except (FileNotFoundError, json.JSONDecodeError):
            self._accounts = {}

        # Fix relationships
        for customer in self._customers.values():
            valid_accs = [acc for acc in customer.account_numbers if acc in self._accounts]
            customer._account_numbers = valid_accs

    def _save_data(self) -> None:
        # Save customers
        cust_dict = {cid: cust.to_dict() for cid, cust in self._customers.items()}
        with open(self._customer_file, 'w') as f:
            json.dump(cust_dict, f, indent=4)

        # Save accounts
        acc_dict = {acc_num: acc.to_dict() for acc_num, acc in self._accounts.items()}
        with open(self._account_file, 'w') as f:
            json.dump(acc_dict, f, indent=4)

    def clear_all_data(self) -> bool:
        """Clear all customers and accounts data"""
        # Clear in-memory data
        self._customers = {}
        self._accounts = {}
        
        # Delete data files
        try:
            if os.path.exists(self._customer_file):
                os.remove(self._customer_file)
            if os.path.exists(self._account_file):
                os.remove(self._account_file)
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False

    def add_customer(self, customer: Customer) -> bool:
        if customer.customer_id in self._customers:
            return False
        self._customers[customer.customer_id] = customer
        self._save_data()
        return True
    
    def remove_customer(self, customer_id: str) -> bool:
        if customer_id not in self._customers:
            return False
        
        customer = self._customers[customer_id]
        if customer.account_numbers:
            return False
        
        del self._customers[customer_id]
        self._save_data()
        return True
    
    def create_account(self, customer_id: str, account_type: str,
                       initial_balance: float = 0.0, **kwargs) -> Account | None:
        customer = self._customers.get(customer_id)
        if not customer:
            return None

        # Generate unique account number
        account_number = str(random.randint(100000000000, 999999999999))

        account = None
        if account_type.lower() == 'savings':
            interest_rate = kwargs.get('interest_rate', 0.01)
            try:
                account = SavingsAccount(account_number, customer_id, initial_balance, interest_rate)
            except ValueError:
                return None
        elif account_type.lower() == 'checking':
            overdraft_limit = kwargs.get('overdraft_limit', 0.0)
            try:
                account = CheckingAccount(account_number, customer_id, initial_balance, overdraft_limit)
            except ValueError:
                return None
        else:
            return None

        self._accounts[account_number] = account
        customer.add_account_number(account_number)
        self._save_data()
        return account

    def deposit(self, account_number: str, amount: float) -> bool:
        account = self._accounts.get(account_number)
        if not account:
            return False
        result = account.deposit(amount)
        if result:
            self._save_data()
        return result

    def withdraw(self, account_number: str, amount: float) -> bool:
        account = self._accounts.get(account_number)
        if not account:
            return False
        result = account.withdraw(amount)
        if result:
            self._save_data()
        return result

    def transfer_funds(self, from_acc_num: str, to_acc_num: str, amount: float) -> bool:
        from_account = self._accounts.get(from_acc_num)
        to_account = self._accounts.get(to_acc_num)
        if not from_account or not to_account:
            return False
        if amount <= 0:
            return False

        if not from_account.withdraw(amount):
            return False
        if not to_account.deposit(amount):
            from_account.deposit(amount)
            return False
        self._save_data()
        return True

    def get_customer_accounts(self, customer_id: str) -> list[Account]:
        customer = self._customers.get(customer_id)
        if not customer:
            return []
        return [self._accounts[acc_num] for acc_num in customer.account_numbers if acc_num in self._accounts]

    def get_all_customers(self) -> list[Customer]:
        return list(self._customers.values())

    def get_all_accounts(self) -> list[Account]:
        return list(self._accounts.values())

    def apply_all_interest(self) -> None:
        changed = False
        for account in self._accounts.values():
            if isinstance(account, SavingsAccount):
                account.apply_interest()
                changed = True
        if changed:
            self._save_data()


# ======== GUI Application ========
class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banking System")
        self.root.geometry("800x600")
        
        self.bank = Bank()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_customer_tab()
        self.create_account_tab()
        self.create_transaction_tab()
        self.create_view_tab()
        self.create_admin_tab()
        
    def create_customer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Customer Management")
        
        # Add Customer Frame
        add_frame = ttk.LabelFrame(tab, text="Add Customer", padding=10)
        add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(add_frame, text="Customer ID:").grid(row=0, column=0, sticky="e")
        self.cust_id_entry = ttk.Entry(add_frame)
        self.cust_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Name:").grid(row=1, column=0, sticky="e")
        self.name_entry = ttk.Entry(add_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Address:").grid(row=2, column=0, sticky="e")
        self.address_entry = ttk.Entry(add_frame)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(add_frame, text="Add Customer", command=self.add_customer).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Remove Customer Frame
        remove_frame = ttk.LabelFrame(tab, text="Remove Customer", padding=10)
        remove_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(remove_frame, text="Customer ID:").grid(row=0, column=0, sticky="e")
        self.remove_cust_id_entry = ttk.Entry(remove_frame)
        self.remove_cust_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(remove_frame, text="Remove Customer", command=self.remove_customer).grid(row=1, column=0, columnspan=2, pady=10)
        
    def create_account_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Account Management")
        
        # Create Account Frame
        account_frame = ttk.LabelFrame(tab, text="Create Account", padding=10)
        account_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(account_frame, text="Customer ID:").grid(row=0, column=0, sticky="e")
        self.account_cust_id_entry = ttk.Entry(account_frame)
        self.account_cust_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(account_frame, text="Account Type:").grid(row=1, column=0, sticky="e")
        self.account_type_var = tk.StringVar()
        self.account_type_combobox = ttk.Combobox(account_frame, textvariable=self.account_type_var, 
                                                values=["Savings", "Checking"])
        self.account_type_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.account_type_combobox.current(0)
        
        ttk.Label(account_frame, text="Initial Balance:").grid(row=2, column=0, sticky="e")
        self.initial_balance_entry = ttk.Entry(account_frame)
        self.initial_balance_entry.grid(row=2, column=1, padx=5, pady=5)
        self.initial_balance_entry.insert(0, "0.0")
        
        # Additional parameters frame
        self.params_frame = ttk.Frame(account_frame)
        self.params_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Initially show savings account params
        self.show_account_params()
        
        # Bind combobox change event
        self.account_type_combobox.bind("<<ComboboxSelected>>", self.show_account_params)
        
        ttk.Button(account_frame, text="Create Account", command=self.create_account).grid(row=4, column=0, columnspan=2, pady=10)
        
    def show_account_params(self, event=None):
        # Clear params frame
        for widget in self.params_frame.winfo_children():
            widget.destroy()
            
        account_type = self.account_type_var.get()
        
        if account_type == "Savings":
            ttk.Label(self.params_frame, text="Interest Rate:").grid(row=0, column=0, sticky="e")
            self.interest_rate_entry = ttk.Entry(self.params_frame)
            self.interest_rate_entry.grid(row=0, column=1, padx=5, pady=5)
            self.interest_rate_entry.insert(0, "0.01")
        elif account_type == "Checking":
            ttk.Label(self.params_frame, text="Overdraft Limit:").grid(row=0, column=0, sticky="e")
            self.overdraft_limit_entry = ttk.Entry(self.params_frame)
            self.overdraft_limit_entry.grid(row=0, column=1, padx=5, pady=5)
            self.overdraft_limit_entry.insert(0, "0.0")
        
    def create_transaction_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Transactions")
        
        # Deposit Frame
        deposit_frame = ttk.LabelFrame(tab, text="Deposit", padding=10)
        deposit_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(deposit_frame, text="Account Number:").grid(row=0, column=0, sticky="e")
        self.deposit_acc_num_entry = ttk.Entry(deposit_frame)
        self.deposit_acc_num_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(deposit_frame, text="Amount:").grid(row=1, column=0, sticky="e")
        self.deposit_amount_entry = ttk.Entry(deposit_frame)
        self.deposit_amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(deposit_frame, text="Deposit", command=self.deposit).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Withdraw Frame
        withdraw_frame = ttk.LabelFrame(tab, text="Withdraw", padding=10)
        withdraw_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(withdraw_frame, text="Account Number:").grid(row=0, column=0, sticky="e")
        self.withdraw_acc_num_entry = ttk.Entry(withdraw_frame)
        self.withdraw_acc_num_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(withdraw_frame, text="Amount:").grid(row=1, column=0, sticky="e")
        self.withdraw_amount_entry = ttk.Entry(withdraw_frame)
        self.withdraw_amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(withdraw_frame, text="Withdraw", command=self.withdraw).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Transfer Frame
        transfer_frame = ttk.LabelFrame(tab, text="Transfer", padding=10)
        transfer_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(transfer_frame, text="From Account:").grid(row=0, column=0, sticky="e")
        self.from_acc_num_entry = ttk.Entry(transfer_frame)
        self.from_acc_num_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(transfer_frame, text="To Account:").grid(row=1, column=0, sticky="e")
        self.to_acc_num_entry = ttk.Entry(transfer_frame)
        self.to_acc_num_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(transfer_frame, text="Amount:").grid(row=2, column=0, sticky="e")
        self.transfer_amount_entry = ttk.Entry(transfer_frame)
        self.transfer_amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(transfer_frame, text="Transfer", command=self.transfer).grid(row=3, column=0, columnspan=2, pady=10)
        
    def create_view_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="View Data")
        
        # View Customers Frame
        cust_frame = ttk.LabelFrame(tab, text="Customers", padding=10)
        cust_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.cust_tree = ttk.Treeview(cust_frame, columns=("ID", "Name", "Address", "Accounts"), show="headings")
        self.cust_tree.heading("ID", text="Customer ID")
        self.cust_tree.heading("Name", text="Name")
        self.cust_tree.heading("Address", text="Address")
        self.cust_tree.heading("Accounts", text="Accounts")
        self.cust_tree.column("ID", width=100)
        self.cust_tree.column("Name", width=150)
        self.cust_tree.column("Address", width=200)
        self.cust_tree.column("Accounts", width=100)
        self.cust_tree.pack(fill="both", expand=True)
        
        ttk.Button(cust_frame, text="Refresh", command=self.refresh_customers).pack(pady=5)
        
        # View Accounts Frame
        acc_frame = ttk.LabelFrame(tab, text="Accounts", padding=10)
        acc_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.acc_tree = ttk.Treeview(acc_frame, columns=("Number", "Holder", "Balance", "Type", "Details"), show="headings")
        self.acc_tree.heading("Number", text="Account No")
        self.acc_tree.heading("Holder", text="Holder ID")
        self.acc_tree.heading("Balance", text="Balance")
        self.acc_tree.heading("Type", text="Type")
        self.acc_tree.heading("Details", text="Details")
        self.acc_tree.column("Number", width=120)
        self.acc_tree.column("Holder", width=100)
        self.acc_tree.column("Balance", width=100)
        self.acc_tree.column("Type", width=100)
        self.acc_tree.column("Details", width=200)
        self.acc_tree.pack(fill="both", expand=True)
        
        ttk.Button(acc_frame, text="Refresh", command=self.refresh_accounts).pack(pady=5)
        
        # Initial refresh
        self.refresh_customers()
        self.refresh_accounts()
        
    def create_admin_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Admin")
        
        # Apply Interest Frame
        interest_frame = ttk.LabelFrame(tab, text="Interest", padding=10)
        interest_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Button(interest_frame, text="Apply Interest to All Savings Accounts", 
                  command=self.apply_interest).pack(pady=10)
        
        # Clear Data Frame
        clear_frame = ttk.LabelFrame(tab, text="Clear Data", padding=10)
        clear_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Button(clear_frame, text="Clear All Data", 
                  command=self.clear_data).pack(pady=10)
        
    # ====== Business Logic Methods ======
    def add_customer(self):
        cust_id = self.cust_id_entry.get()
        name = self.name_entry.get()
        address = self.address_entry.get()
        
        if not cust_id or not name or not address:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        customer = Customer(cust_id, name, address)
        if self.bank.add_customer(customer):
            messagebox.showinfo("Success", "Customer added successfully!")
            self.cust_id_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
            self.refresh_customers()
        else:
            messagebox.showerror("Error", "Customer ID already exists!")
            
    def remove_customer(self):
        cust_id = self.remove_cust_id_entry.get()
        
        if not cust_id:
            messagebox.showerror("Error", "Customer ID is required!")
            return
            
        if self.bank.remove_customer(cust_id):
            messagebox.showinfo("Success", "Customer removed successfully!")
            self.remove_cust_id_entry.delete(0, tk.END)
            self.refresh_customers()
            self.refresh_accounts()
        else:
            messagebox.showerror("Error", "Customer not found or has active accounts!")
            
    def create_account(self):
        cust_id = self.account_cust_id_entry.get()
        account_type = self.account_type_var.get().lower()
        
        try:
            initial_balance = float(self.initial_balance_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid initial balance!")
            return
            
        kwargs = {}
        if account_type == "savings":
            try:
                interest_rate = float(self.interest_rate_entry.get())
                kwargs['interest_rate'] = interest_rate
            except ValueError:
                messagebox.showerror("Error", "Invalid interest rate!")
                return
        elif account_type == "checking":
            try:
                overdraft_limit = float(self.overdraft_limit_entry.get())
                kwargs['overdraft_limit'] = overdraft_limit
            except ValueError:
                messagebox.showerror("Error", "Invalid overdraft limit!")
                return
                
        account = self.bank.create_account(cust_id, account_type, initial_balance, **kwargs)
        if account:
            messagebox.showinfo("Success", 
                              f"Account created successfully!\nAccount Number: {account.account_number}")
            self.account_cust_id_entry.delete(0, tk.END)
            self.initial_balance_entry.delete(0, tk.END)
            self.initial_balance_entry.insert(0, "0.0")
            self.refresh_accounts()
        else:
            messagebox.showerror("Error", "Failed to create account. Check customer ID and inputs!")
            
    def deposit(self):
        acc_num = self.deposit_acc_num_entry.get()
        
        try:
            amount = float(self.deposit_amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
            return
            
        if self.bank.deposit(acc_num, amount):
            messagebox.showinfo("Success", "Deposit successful!")
            self.deposit_acc_num_entry.delete(0, tk.END)
            self.deposit_amount_entry.delete(0, tk.END)
            self.refresh_accounts()
        else:
            messagebox.showerror("Error", "Deposit failed. Check account number and amount!")
            
    def withdraw(self):
        acc_num = self.withdraw_acc_num_entry.get()
        
        try:
            amount = float(self.withdraw_amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
            return
            
        if self.bank.withdraw(acc_num, amount):
            messagebox.showinfo("Success", "Withdrawal successful!")
            self.withdraw_acc_num_entry.delete(0, tk.END)
            self.withdraw_amount_entry.delete(0, tk.END)
            self.refresh_accounts()
        else:
            messagebox.showerror("Error", "Withdrawal failed. Check account number, amount, or available balance!")
            
    def transfer(self):
        from_acc = self.from_acc_num_entry.get()
        to_acc = self.to_acc_num_entry.get()
        
        try:
            amount = float(self.transfer_amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
            return
            
        if self.bank.transfer_funds(from_acc, to_acc, amount):
            messagebox.showinfo("Success", "Transfer successful!")
            self.from_acc_num_entry.delete(0, tk.END)
            self.to_acc_num_entry.delete(0, tk.END)
            self.transfer_amount_entry.delete(0, tk.END)
            self.refresh_accounts()
        else:
            messagebox.showerror("Error", "Transfer failed.Check account numbers and amount!")
            
    def apply_interest(self):
        self.bank.apply_all_interest()
        messagebox.showinfo("Success", "Interest applied to all savings accounts!")
        self.refresh_accounts()
        
    def clear_data(self):
        if messagebox.askyesno("Confirm", "WARNING: This will delete ALL data. Are you sure?"):
            if self.bank.clear_all_data():
                messagebox.showinfo("Success", "All data has been cleared.")
                self.refresh_customers()
                self.refresh_accounts()
            else:
                messagebox.showerror("Error", "Failed to clear data!")
                
    def refresh_customers(self):
        # Clear existing data
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
            
        # Add new data
        for customer in self.bank.get_all_customers():
            self.cust_tree.insert("", "end", values=(
                customer.customer_id,
                customer.name,
                customer.address,
                len(customer.account_numbers)
            ))
            
    def refresh_accounts(self):
        # Clear existing data
        for item in self.acc_tree.get_children():
            self.acc_tree.delete(item)
            
        # Add new data
        for account in self.bank.get_all_accounts():
            if isinstance(account, SavingsAccount):
                acc_type = "Savings"
                details = f"Interest: {account.interest_rate * 100:.2f}%"
            else:
                acc_type = "Checking"
                details = f"Overdraft: ${account.overdraft_limit:.2f}"
                
            self.acc_tree.insert("", "end", values=(
                account.account_number,
                account.account_holder_id,
                f"${account.balance:.2f}",
                acc_type,
                details
            ))


# ======== Main Application ========
if __name__ == "__main__":
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()