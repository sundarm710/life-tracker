# README

## Welcome to the Expense and Time Tracker Dashboard

This repository contains a comprehensive application designed to help users track their expenses and manage their time effectively. Built using Python and Streamlit, the application provides an interactive dashboard for visualizing financial data and time management activities. Below, we will take you through the various components of the codebase, explaining their purpose and functionality.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Installation](#installation)
3. [Directory Structure](#directory-structure)
4. [Key Components](#key-components)
   - [Expense Dashboard](#expense-dashboard)
   - [Time Tracker Dashboard](#time-tracker-dashboard)
   - [Budget Management](#budget-management)
   - [Data Handling](#data-handling)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [License](#license)

---

## Project Overview

The Expense and Time Tracker Dashboard is designed to provide users with insights into their spending habits and time allocation. The application allows users to visualize their expenses through various charts and manage their time effectively by tracking different activities. The dashboard is built using Streamlit, a powerful framework for creating web applications in Python.

---

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Google Sheets credentials by placing the `credentials.json` file in the root directory.

4. Run the application:
   ```bash
   streamlit run Runway.py
   ```

---

## Directory Structure

The project is organized into several directories and files:

```
.
├── components
│   ├── __init__.py
│   └── budget_manager.py
├── pages
│   ├── ExpensesBreakdown.py
│   ├── NetWorth.py
│   ├── TimeGoals.py
│   └── TimeSpent.py
├── utility
│   ├── expense_parsing.py
│   ├── expenses_base.py
│   ├── net_expenses.py
│   ├── time_block_parsing.py
│   └── time_goals.py
├── config
│   ├── payins.yaml
│   └── time-goals.yaml
├── .gitignore
├── credentials.json
└── requirements.txt
```

---

## Key Components

### Expense Dashboard

The `Runway.py` file serves as the main entry point for the Expense Dashboard. It provides a Streamlit interface where users can:

- Load and preprocess expense data.
- Filter expenses based on various criteria.
- Visualize expenses through interactive charts.

The dashboard includes features such as:

- **Expense Type Selection**: Users can choose between viewing all expenses or only default categories.
- **Runway Calculation**: The application calculates how long the user can sustain their expenses based on their net worth and average monthly burn rate.

### Time Tracker Dashboard

The `TimeSpent.py` and `TimeGoals.py` files provide functionality for tracking and managing time. Users can:

- View their time allocation across different activities.
- Set and track goals for various activities, such as workouts or reading.

The time tracker includes features like:

- **Activity Categorization**: Activities are categorized for better visualization and tracking.
- **Time Charts**: Users can view their time spent on different activities in daily, weekly, or monthly formats.

### Budget Management

The `budget_manager.py` component handles budget-related functionalities. It allows users to:

- Define budgets with specific targets and time frames.
- Track progress against these budgets.
- Manage active budgets and their statuses.

### Data Handling

The `utility` directory contains various modules responsible for data handling:

- **Expense Parsing**: The `expense_parsing.py` module reads and processes expense data from a ledger file, converting it into a structured format for analysis.
- **Time Block Parsing**: The `time_block_parsing.py` module processes time blocks from Obsidian daily notes, categorizing activities and saving them to CSV files.
- **Net Expenses Calculation**: The `net_expenses.py` module calculates net expenses by comparing payins and expenses over time.

---

## Usage

Once the application is running, users can navigate through the dashboard to explore their expenses and time management activities. The interface is intuitive, allowing users to interact with various components seamlessly.

1. **Expense Dashboard**: Users can filter expenses, view charts, and calculate their runway.
2. **Time Tracker**: Users can track their time spent on different activities and visualize their progress against set goals.

---

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request.

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

Thank you for exploring the Expense and Time Tracker Dashboard! We hope this application helps you manage your finances and time more effectively. If you have any questions or feedback, feel free to reach out.