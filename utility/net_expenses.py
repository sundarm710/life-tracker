import csv
import yaml
from datetime import datetime
from collections import defaultdict

def load_payins(file_path):
    with open(file_path, 'r') as file:
        payins = yaml.safe_load(file)
    return payins

def load_expenses(file_path):
    expenses = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            date = datetime.strptime(row[0], '%Y-%m-%d')
            amount = float(row[2])
            expenses.append((date, amount))
    return expenses

def calculate_net_expenses():
    payins = load_payins('config/payins.yaml')
    expenses = load_expenses('files/ledger_output.csv')

    monthly_net = defaultdict(float)
    print (payins)
    # Process payins

    for date, payin_info in payins.items():
        month_key = date.strftime('%Y-%m')
        amount = payin_info['amount']
        monthly_net[month_key] += amount

    # Process expenses
    for date, amount in expenses:
        month_key = date.strftime('%Y-%m')
        monthly_net[month_key] -= amount

    # Calculate net expenses
    for month in monthly_net:   
        if month in payins:
            monthly_net[month] = payins[month]['amount'] - monthly_net[month]
        else:
            monthly_net[month] = -monthly_net[month]  # If no payin, net is negative of expenses

    # Sort and print results
    for month in sorted(monthly_net.keys()):
        net_amount = monthly_net[month]
        status = "positive" if net_amount >= 0 else "negative"
        print(f"{month}: Net {status} ₹{abs(net_amount):.2f}")

if __name__ == "__main__":
    calculate_net_expenses()

