# Banking Transaction Analysis System

A Python-based educational banking transaction analysis project that combines MySQL, Flask, Pandas, NumPy, Matplotlib, and Streamlit to record simulated transactions, analyze financial activity, identify transactions for review, and visualize transaction patterns.

> **Disclaimer:** This is an educational simulation using synthetic data. It is not a real banking application and must not be used to handle real customer accounts or money.

## Features

- **MySQL database:** Stores synthetic customers, accounts, and transaction records.
- **Flask REST API:** Retrieves customers, accounts, transactions, and analytics.
- **Transaction processing:** Supports simulated deposits and withdrawals with amount validation and insufficient-balance protection.
- **Data analysis:** Uses Pandas and NumPy to calculate deposit totals, withdrawal totals, net transaction flow, and transaction summaries.
- **Review flags:** Identifies unusually large transactions for further review using a configurable statistical threshold.
- **Visualizations:** Uses Matplotlib to generate transaction charts.
- **Interactive dashboard:** Uses Streamlit to filter transactions, explore charts, and download CSV reports.
- **Reporting:** Generates account-wise and monthly transaction summaries.

## Technology Stack

- Python
- Flask
- MySQL
- Pandas
- NumPy
- Matplotlib
- Streamlit
- python-dotenv
- MySQL Connector/Python

## Project Structure

```text
banking_transaction_analysis/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   └── templates/
├── reports/
├── analysis.py
├── config.py
├── database.py
├── run.py
├── streamlit_app.py
├── test_reports.py
├── test_transaction_api.py
├── visualize.py
├── .env
├── .gitignore
└── README.md
```

## Setup

### 1. Prerequisites

Install Python, MySQL Server, and Git.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Create a `requirements.txt` containing the project's required packages, then run:

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the database

Create the `banking_analysis` database and the required `customers`, `accounts`, and `transactions` tables. Populate them with synthetic sample data.

Configure a `.env` file in the project root:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_LOCAL_MYSQL_PASSWORD
DB_NAME=banking_analysis
```

Replace the placeholder with your local MySQL password. Never commit `.env` or real credentials to GitHub.

### 5. Run the Flask API

```powershell
python run.py
```

The API runs locally at `http://127.0.0.1:5000`.

### 6. Run the Streamlit dashboard

Open a second terminal, activate the same virtual environment, and run:

```powershell
python -m streamlit run streamlit_app.py
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/customers` | List synthetic customers |
| GET | `/accounts` | List accounts |
| GET | `/transactions` | Retrieve transactions |
| GET | `/analytics` | Retrieve transaction analytics |
| POST | `/transactions` | Create a simulated deposit or withdrawal |

Example simulated deposit request:

```json
{
  "account_id": 1,
  "transaction_type": "Deposit",
  "amount": "500.00",
  "description": "Demo deposit"
}
```

## Analysis and Reports

The project supports:

- Deposit and withdrawal totals
- Net transaction flow
- Average, minimum, and maximum transaction amounts
- Account-wise transaction summaries
- Monthly transaction summaries
- Review flags for unusually large transactions
- CSV exports and visual charts

Net transaction flow is calculated as deposits minus withdrawals. It is not the same as an account's current balance.

## Testing

Run the API tests while the Flask server is running:

```powershell
python test_transaction_api.py
```

Generate account-wise and monthly reports:

```powershell
python test_reports.py
```

## Future Improvements

- Automated unit and integration tests
- Improved error handling and logging
- Authentication and authorization
- More detailed monthly analytics
- Deployment with production-appropriate server configuration
- Expanded documentation and dashboard screenshots

## Author

Developed as a Python, database, API, and data analysis learning project.
