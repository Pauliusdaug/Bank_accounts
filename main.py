import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date

# Ensure data files exist
for filename in ["accounts.txt", "payments.txt"]:
    if not os.path.exists(filename):
        with open(filename, "w"):
            pass  # Just create the file


app = FastAPI()

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

def add_payment_to_file(payment: Payment):
    with open("payments.txt", "a") as file:
        file.write(f"{payment.id},{payment.from_account_id},{payment.to_account_id},{payment.amount_in_euros},{payment.payment_date}\n")

def read_payments_from_file():
    payments = []
    with open("payments.txt", "r") as file:
        for line in file:
            id, from_account_id, to_account_id, amount_in_euros, payment_date = line.strip().split(',')
            payments.append(Payment(id=int(id), from_account_id=int(from_account_id), to_account_id=int(to_account_id), amount_in_euros=int(amount_in_euros), payment_date=date.fromisoformat(payment_date)))
    return payments

accounts: list[Account] = read_account_from_file()
payments: list[Payment] = read_payments_from_file()

@app.post("/accounts/")
def create_account(account: Account):
    accounts.append(account)
    add_account_to_file(account)
    return {"message": "Account created successfully"}

@app.get("/accounts/")
def get_accounts():
    return accounts

@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    for account in accounts:
        if account.id == account_id:
            return account
    return {"error": "Account not found"}

@app.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    for account in accounts:
        if account.id == account_id:
            accounts.remove(account)
            delete_account_from_file(account_id)
            return {"message": "Account deleted successfully"}
    return {"error": "Account not found"}


@app.post("/payments/")
def create_payment(payment: Payment):
    payments.append(payment)
    add_payment_to_file(payment)
    return {"message": "Payment created successfully"}

@app.get("/payments/")
def get_payments():
    return payments

@app.get("/payments/{payment_id}")
def get_payment(payment_id: int):
    for payment in payments:
        if payment.id == payment_id:
            return payment
    return {"error": "Payment not found"}

