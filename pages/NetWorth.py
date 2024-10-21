import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def fetch_data_from_google_sheets(sheet_url, sheet_name):
    """
    Fetch data from a Google Sheets file and return it as a DataFrame.

    :param sheet_url: URL of the Google Sheets file
    :param sheet_name: Name of the sheet to fetch data from
    :return: DataFrame containing the sheet data
    """
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

    print(creds)

    # Authorize the clientsheet 
    client = gspread.authorize(creds)

    # Get the instance of the Spreadsheet
    sheet = client.open_by_url(sheet_url)

    # Get the sheet by name
    worksheet = sheet.worksheet(sheet_name)

    # Get all the records of the data
    records = worksheet.get_all_records()

    # Convert the json to dataframe
    df = pd.DataFrame.from_records(records)

    return df

# Example usage
sheet_url = "https://docs.google.com/spreadsheets/d/1786I65hBnedPUf_qYIiyvUwl0VeTwKj4L_Rt4-YMs3Y/edit?gid=0#gid=0"
sheet_name = "Logs"
df = fetch_data_from_google_sheets(sheet_url, sheet_name)

print(df)