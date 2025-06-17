import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date

# --- Ensure data files exist ---
for filename in ["accounts.txt", "payments.txt"]:
    if not os.path.exists(filename):
        with open(filename, "w"):
            pass  # Just create the file if missing

# --- Initialize FastAPI app ---
app = FastAPI()

# --- Data models for storage and responses (include ID) ---
class Account(BaseModel):
    id: int
    type: str
    person_name: str
    address: str

class Payment(BaseModel):
    id: int
    from_account_id: int
    to_account_id: int 
    amount_in_euros: int
    payment_date: date

# --- Input models (no ID) for POST requests ---
class AccountInput(BaseModel):
    type: str
    person_name: str
    address: str

class PaymentInput(BaseModel):
    from_account_id: int
    to_account_id: int 
    amount_in_euros: int
    payment_date: date

# --- File helper functions to add/read/delete accounts ---
def add_account_to_file(account: Account):
    with open("accounts.txt", "a") as file:
        file.write(f"{account.id},{account.type},{account.person_name},{account.address}\n")

def read_account_from_file():
    accounts = []
    with open("accounts.txt", "r") as file:
        for line in file:
            id, type, person_name, address = line.strip().split(',')
            accounts.append(Account(id=int(id), type=type, person_name=person_name, address=address))
    return accounts

def delete_account_from_file(account_id: int):
    accounts = read_account_from_file()
    with open("accounts.txt", "w") as file:
        for account in accounts:
            if account.id != account_id:
                file.write(f"{account.id},{account.type},{account.person_name},{account.address}\n")

# --- File helper functions to add/read payments ---
def add_payment_to_file(payment: Payment):
    with open("payments.txt", "a") as file:
        file.write(f"{payment.id},{payment.from_account_id},{payment.to_account_id},{payment.amount_in_euros},{payment.payment_date}\n")

def read_payments_from_file():
    payments = []
    with open("payments.txt", "r") as file:
        for line in file:
            id, from_account_id, to_account_id, amount_in_euros, payment_date = line.strip().split(',')
            payments.append(Payment(
                id=int(id),
                from_account_id=int(from_account_id),
                to_account_id=int(to_account_id),
                amount_in_euros=int(amount_in_euros),
                payment_date=date.fromisoformat(payment_date)
            ))
    return payments

# --- Load existing data from files at startup ---
accounts: list[Account] = read_account_from_file()
payments: list[Payment] = read_payments_from_file()

# --- Initialize ID counters based on max existing IDs ---
next_account_id = max((account.id for account in accounts), default=0) + 1
next_payment_id = max((payment.id for payment in payments), default=0) + 1

# --- API to create a new account with generated ID ---
@app.post("/accounts/")
def create_account(account_input: AccountInput):
    global next_account_id
    account = Account(id=next_account_id, **account_input.dict())
    next_account_id += 1
    accounts.append(account)
    add_account_to_file(account)
    return {"message": "Account created successfully", "account_id": account.id}

# --- API to retrieve all accounts ---
@app.get("/accounts/")
def get_accounts():
    return accounts

# --- API to retrieve a specific account by ID ---
@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    for account in accounts:
        if account.id == account_id:
            return account
    return {"error": "Account not found"}

# --- API to delete an account by ID ---
@app.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    for account in accounts:
        if account.id == account_id:
            accounts.remove(account)
            delete_account_from_file(account_id)
            return {"message": "Account deleted successfully"}
    return {"error": "Account not found"}

# --- API to create a new payment with generated ID ---
@app.post("/payments/")
def create_payment(payment_input: PaymentInput):
    global next_payment_id
    payment = Payment(id=next_payment_id, **payment_input.dict())
    next_payment_id += 1
    payments.append(payment)
    add_payment_to_file(payment)
    return {"message": "Payment created successfully", "payment_id": payment.id}

# --- API to retrieve all payments ---
@app.get("/payments/")
def get_payments():
    return payments

# --- API to retrieve a specific payment by ID ---
@app.get("/payments/{payment_id}")
def get_payment(payment_id: int):
    for payment in payments:
        if payment.id == payment_id:
            return payment
    return {"error": "Payment not found"}

# --- API to generate a report of all payments with names ---
@app.get("/report")
def get_report():
    account_lookup = {account.id: account.person_name for account in accounts}
    report = []
    for payment in payments:
        from_name = account_lookup.get(payment.from_account_id, "Unknown")
        to_name = account_lookup.get(payment.to_account_id, "Unknown")
        report.append({
            "from_person_name": from_name,
            "to_person_name": to_name,
            "amount_in_euros": payment.amount_in_euros,
            "payment": payment.payment_date
        })
    return report