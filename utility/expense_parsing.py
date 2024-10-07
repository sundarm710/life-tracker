import re
import csv
from datetime import datetime

# Get the path to Obsidian ledger.txt from environment variable
# OBSIDIAN_LEDGER_PATH = os.getenv('OBSIDIAN_LEDGER_PATH')
OBSIDIAN_LEDGER_PATH = '/Users/sundar/Documents/Obsidian/Thought Den/transactions.ledger'

def parse_ledger_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content into blocks based on empty lines (transaction boundaries)
    blocks = content.strip().split('\n\n')

    result = []

    for block in blocks:
        lines = block.split('\n')

        # Check if the block is part of the "Starting Balances" section
        if any("Starting Balances" in line for line in lines):
            continue

        # Activate parsing after the starting balances
        if any(re.match(r'\d{4}/\d{2}/\d{2}', line) for line in lines):
            start_parsing = True

        if not start_parsing:
            continue

        # Extract date and description from the first line
        first_line = lines[0].strip()
        date_description_match = re.match(r'(\d{4}/\d{2}/\d{2})\s+(.+)', first_line)

        if date_description_match:
            date_str, description = date_description_match.groups()
            date = datetime.strptime(date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
        else:
            # Skip this block if the date/description line doesn't match
            continue

        # Extract the transaction details from the remaining lines
        for line in lines[1:]:
            # Match accounts and amounts in the format 'Account:SubAccount:SubSubAccount ₹Amount'
            account_match = re.match(r'([\w:]+)\s+₹([\d.,]+)', line.strip())
            if account_match:
                account, amount = account_match.groups()

                # Remove commas from amounts, if present
                amount = amount.replace(',', '')

                # Split the account string into its parts (Expense_1, Expense_2, Expense_3)
                account_parts = account.split(':')

                # Ensure there are exactly 3 parts, fill missing parts with empty strings
                while len(account_parts) < 3:
                    account_parts.append('')

                expense_1, expense_2, expense_3 = account_parts

                # Add the parsed entry to the result
                result.append([date, description, float(amount), expense_1, expense_2, expense_3])

    return result

def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Description', 'Amount', 'Expense_1', 'Expense_2', 'Expense_3'])
        
        for row in data:
            writer.writerow(row)

def parse_main():
    file_path = OBSIDIAN_LEDGER_PATH  # Path to your ledger file
    output_file = 'files/ledger_output.csv'  # Output CSV file name

    parsed_data = parse_ledger_file(file_path)
    write_to_csv(parsed_data, output_file)

    print(f"CSV file '{output_file}' has been created successfully.")

if __name__ == "__main__":
    parse_main()
