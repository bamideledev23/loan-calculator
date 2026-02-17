#!/usr/bin/env python3
from decimal import Decimal, getcontext, ROUND_HALF_UP
from datetime import datetime
import math

getcontext().prec = 28

def format_naira(amount: Decimal) -> str:
    amt = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    parts = f"{amt:,.2f}"
    return f"₦{parts}"

def get_decimal(prompt: str, allow_zero: bool = False) -> Decimal:
    while True:
        try:
            val = input(prompt).strip()
            d = Decimal(val)
            if d < 0:
                print("Please enter a non-negative number.")
                continue
            if not allow_zero and d == 0:
                print("Value must be greater than zero.")
                continue
            return d
        except Exception:
            print("Invalid number. Try again.")

def get_int(prompt: str, allow_zero: bool = False) -> int:
    while True:
        try:
            val = input(prompt).strip()
            i = int(val)
            if i < 0:
                print("Please enter a non-negative integer.")
                continue
            if not allow_zero and i == 0:
                print("Value must be greater than zero.")
                continue
            return i
        except Exception:
            print("Invalid integer. Try again.")

def calculate_flat(principal: Decimal, annual_rate: Decimal, months: int):
    years = Decimal(months) / Decimal(12)
    interest = principal * (annual_rate / Decimal(100)) * years
    total_payment = principal + interest
    monthly_payment = total_payment / Decimal(months)
    return {
        'monthly_payment': monthly_payment.quantize(Decimal('0.01')),
        'total_payment': total_payment.quantize(Decimal('0.01')),
        'total_interest': interest.quantize(Decimal('0.01')),
        'months': months
    }

def calculate_reducing(principal: Decimal, annual_rate: Decimal, months: int, extra: Decimal = Decimal('0')):
    if annual_rate == 0:
        base_monthly = principal / Decimal(months)
        monthly = base_monthly
        if extra == 0:
            total_payment = monthly * Decimal(months)
            total_interest = Decimal('0')
            return {
                'monthly_payment': monthly.quantize(Decimal('0.01')),
                'total_payment': total_payment.quantize(Decimal('0.01')),
                'total_interest': total_interest.quantize(Decimal('0.01')),
                'months': months
            }

    monthly_rate = (annual_rate / Decimal(100)) / Decimal(12)
    # standard amortization payment without extra
    if monthly_rate == 0:
        monthly_payment = principal / Decimal(months)
    else:
        monthly_payment = principal * (monthly_rate / (1 - (1 + monthly_rate) ** (-months)))

    if extra == 0:
        total_payment = monthly_payment * Decimal(months)
        total_interest = total_payment - principal
        return {
            'monthly_payment': monthly_payment.quantize(Decimal('0.01')),
            'total_payment': total_payment.quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'months': months
        }

    # If extra payment provided, simulate amortization to get actual interest and months
    balance = principal
    monthly = monthly_payment + extra
    month_count = 0
    total_interest = Decimal('0')
    # cap iterations to avoid infinite loops
    while balance > Decimal('0.005') and month_count < 1000:
        interest = (balance * monthly_rate).quantize(Decimal('0.0000001'))
        principal_paid = monthly - interest
        if principal_paid <= 0:
            # payment too small to cover interest
            break
        balance -= principal_paid
        total_interest += interest
        month_count += 1

    if balance > 0:
        # final tiny payment adjustment
        total_payment = (monthly * Decimal(month_count)) + balance
        total_interest += (balance * monthly_rate)
        month_count += 1
    else:
        total_payment = (monthly * Decimal(month_count))

    return {
        'monthly_payment': (monthly.quantize(Decimal('0.01'))),
        'total_payment': Decimal(total_payment).quantize(Decimal('0.01')),
        'total_interest': Decimal(total_interest).quantize(Decimal('0.01')),
        'months': month_count
    }

def save_result(text: str, filename: str = "calculations.txt"):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(text + "\n")

def main():
    print("Pro Loan Calculator — Nigeria")
    while True:
        print("\nSelect loan type:")
        print("1) Personal")
        print("2) Car")
        print("3) Mortgage")
        choice = input("Enter choice (1-3): ").strip()
        if choice not in ('1', '2', '3'):
            print("Invalid choice. Please enter 1, 2 or 3.")
            continue

        loan_types = {'1': 'Personal', '2': 'Car', '3': 'Mortgage'}
        loan_type = loan_types[choice]

        principal = get_decimal("Enter loan amount: ")
        annual_rate = get_decimal("Enter annual interest rate (in %): ", allow_zero=True)
        months = get_int("Enter duration (in months): ")
        print("Choose interest type:")
        print("1) Flat")
        print("2) Reducing balance")
        itype = input("Enter choice (1-2): ").strip()
        if itype not in ('1', '2'):
            print("Invalid choice; defaulting to Reducing balance.")
            itype = '2'

        extra = Decimal('0')
        extra_input = input("Enter extra monthly payment (or press Enter to skip): ").strip()
        if extra_input:
            try:
                extra = Decimal(extra_input)
                if extra < 0:
                    print("Extra payment cannot be negative; ignoring.")
                    extra = Decimal('0')
            except Exception:
                print("Invalid extra value; ignoring.")
                extra = Decimal('0')

        if itype == '1':
            res = calculate_flat(principal, annual_rate, months)
            monthly_base = res['monthly_payment']
            if extra > 0:
                monthly_with_extra = (monthly_base + extra).quantize(Decimal('0.01'))
                total_payment_with_extra = (monthly_with_extra * Decimal(months)).quantize(Decimal('0.01'))
            else:
                monthly_with_extra = monthly_base
                total_payment_with_extra = res['total_payment']

            print('\n--- Results ---')
            print(f"Loan type: {loan_type}")
            print(f"Loan amount: {format_naira(principal)}")
            print(f"Interest type: Flat")
            print(f"Monthly payment: {format_naira(monthly_base)}")
            if extra > 0:
                print(f"Monthly payment (with extra): {format_naira(monthly_with_extra)}")
            print(f"Total payment: {format_naira(res['total_payment'])}")
            if extra > 0:
                print(f"Total payment (with extra): {format_naira(total_payment_with_extra)}")
            print(f"Total interest: {format_naira(res['total_interest'])}")

            save_choice = input("Save result to file? (y/N): ").strip().lower()
            if save_choice == 'y':
                stamp = datetime.now().isoformat(sep=' ', timespec='seconds')
                txt = f"[{stamp}] {loan_type} | Flat | Amount: {format_naira(principal)} | Months: {months} | Monthly: {format_naira(monthly_with_extra)} | Total: {format_naira(total_payment_with_extra)} | Interest: {format_naira(res['total_interest'])}"
                save_result(txt)
                print("Saved to calculations.txt")

        else:
            res = calculate_reducing(principal, annual_rate, months, extra)
            print('\n--- Results ---')
            print(f"Loan type: {loan_type}")
            print(f"Loan amount: {format_naira(principal)}")
            print(f"Interest type: Reducing balance")
            print(f"Monthly payment: {format_naira(res['monthly_payment'])}")
            if extra > 0:
                print(f"Months to repay (with extra): {res['months']}")
            else:
                print(f"Months to repay: {res['months']}")
            print(f"Total payment: {format_naira(res['total_payment'])}")
            print(f"Total interest: {format_naira(res['total_interest'])}")

            save_choice = input("Save result to file? (y/N): ").strip().lower()
            if save_choice == 'y':
                stamp = datetime.now().isoformat(sep=' ', timespec='seconds')
                txt = f"[{stamp}] {loan_type} | Reducing | Amount: {format_naira(principal)} | Months: {res['months']} | Monthly: {format_naira(res['monthly_payment'])} | Total: {format_naira(res['total_payment'])} | Interest: {format_naira(res['total_interest'])}"
                save_result(txt)
                print("Saved to calculations.txt")

        again = input("\nCalculate another loan? (Y/n): ").strip().lower()
        if again == 'n':
            print("Goodbye.")
            break

if __name__ == '__main__':
    main()
    