# README

## Overview

Welcome to the Expense and Time Management Dashboard! This project is designed to help users track their expenses and manage their time effectively. Built using Python and Streamlit, it provides an interactive dashboard for visualizing financial data and time spent on various activities. This README will guide you through the codebase, explaining the structure, key components, and how to use the application.

## Table of Contents

- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Code Walkthrough](#code-walkthrough)
  - [Main Components](#main-components)
  - [Utility Functions](#utility-functions)
  - [Data Management](#data-management)
  - [Visualization](#visualization)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

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
├── credentials.json
├── .gitignore
└── requirements.txt
```

## Key Features

- **Expense Tracking**: Users can visualize their expenses through various filters and categories.
- **Time Management**: Track time spent on different activities and visualize it through charts.
- **Interactive Dashboard**: Built with Streamlit, providing a user-friendly interface.
- **Data Visualization**: Utilizes Plotly for creating interactive charts and graphs.

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Google Sheets API credentials by placing the `credentials.json` file in the root directory.

4. Ensure you have the necessary YAML configuration files in the `config` directory.

## Usage

To run the application, use the following command:

```bash
streamlit run Runway.py
```

This will launch the Streamlit application in your default web browser.

## Code Walkthrough

### Main Components

The main entry point of the application is `Runway.py`, which sets up the Streamlit interface and imports necessary functions from the utility modules.

```python
import streamlit as st
from utility.expenses_base import fetch_only_expenses, fetch_default_expenses, format_in_indian_system
```

This file contains the logic for loading data, filtering expenses, and calculating the runway based on the user's net worth and burn rate.

### Utility Functions

The `utility` directory contains several modules that handle data processing and management:

- **expense_parsing.py**: Responsible for parsing expense data from a ledger file and converting it into a structured format.
- **expenses_base.py**: Contains functions to load and filter expenses based on various criteria.
- **time_block_parsing.py**: Parses time blocks from daily notes in Markdown format, categorizing activities and calculating durations.
- **