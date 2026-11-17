# BankGuard – Bank Transaction Analytics & Fraud Risk Detection

## Overview
BankGuard is an academic data analytics project that explores synthetic banking transactions, calculates transparent rule-based risk indicators, and presents interactive visualisations.

## Features
- Interactive filters for date, transaction type, location and risk category
- KPI cards for transaction count, transaction value, labelled fraud cases and high-risk flags
- Charts for transaction type, risk category, monthly value and channel-wise labelled cases
- Searchable transaction review table and CSV export
- SQL queries for transaction analysis and alert review

## Technology
Python, Pandas, Streamlit, Plotly, SQLite/SQL, Excel.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Browser opens the dashboard (usually at http://localhost:8501).

## Dataset
`data/bank_transactions_synthetic.csv` contains 5,000 synthetically generated transaction rows. It is created for academic demonstration and does not contain real customer data.

## SQL
Open `sql/bankguard_queries.sql` in SQLite/DB Browser for SQLite. Import the CSV into a table named `transactions` before running the queries. The schema is included at the top of the SQL file.

## Important limitation
Synthetic fraud labels and illustrative risk rules are not real-world proof of fraud, a regulatory threshold, or a production AML decision system. Alerts require human review.
