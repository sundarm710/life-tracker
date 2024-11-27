import re
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
import boto3

# Load environment variables from .env file
load_dotenv()

# Define your S3 bucket and key (path) from environment variables
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'obsidian-notes-storage')
S3_OBJECT_KEY = os.getenv('S3_OBJECT_KEY', 'ThoughtDenS3/transactions.ledger')  # Path in your S3 bucket

# Function to fetch the ledger file from S3
def fetch_ledger_from_s3(bucket_name, object_key):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read().decode('utf-8')
    return content

# Function to parse the ledger file content
def parse_ledger_file(content):
    # Split the content into blocks based on empty lines (transaction boundaries)
    blocks = content.strip().split('\n\n')

    result = []
    start_parsing = False  # Initialize flag for starting to parse after "Starting Balances" section

    for block in blocks:
        lines = block.split('\n')

        # Skip blocks related to "Starting Balances" section
        if any("Starting Balances" in line for line in lines):
            continue

        # Activate parsing after the starting balances section
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

                # Assign the parts to the respective expense categories
                expense_1, expense_2, expense_3 = account_parts

                # Add the parsed entry to the result
                result.append([date, description, float(amount), expense_1, expense_2, expense_3])

    return result

# Function to write the parsed data to a CSV file
def write_to_csv(data, output_file):
    # Ensure the 'files' directory exists
    if not os.path.exists('files'):
        os.makedirs('files')

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Description', 'Amount', 'Expense_1', 'Expense_2', 'Expense_3'])
        
        # Write each parsed row to the CSV file
        for row in data:
            writer.writerow(row)

# Function to create the expense CSV
def create_expense_csv():
    # Fetch the ledger file content from S3
    ledger_content = fetch_ledger_from_s3(S3_BUCKET_NAME, S3_OBJECT_KEY)
    
    # Output file location
    output_file = 'files/ledger_output.csv'  # Output CSV file name

    # Parse the ledger content
    parsed_data = parse_ledger_file(ledger_content)

    # Write the parsed data to a CSV file
    write_to_csv(parsed_data, output_file)

    print(f"CSV file '{output_file}' has been created successfully.")

if __name__ == "__main__":
    create_expense_csv()
