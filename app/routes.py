
from flask import Blueprint, jsonify, render_template, request
from database import get_connection
from decimal import Decimal, InvalidOperation
api = Blueprint("api", __name__)


@api.get("/customers")
def get_customers():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, display_name
            FROM customers
            ORDER BY customer_id
        """)

        customers = cursor.fetchall()

        return jsonify({
            "count": len(customers),
            "customers": customers
        }), 200

    except Exception as error:
        print("Customers error:", error)
        return jsonify({
            "error": "Unable to retrieve customers."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


@api.get("/accounts")
def get_accounts():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                a.account_id,
                a.customer_id,
                c.display_name,
                a.account_type,
                a.opening_balance,
                a.created_at
            FROM accounts AS a
            JOIN customers AS c
                ON a.customer_id = c.customer_id
            ORDER BY a.account_id
        """)

        accounts = cursor.fetchall()

        for account in accounts:
            account["opening_balance"] = float(
                account["opening_balance"]
            )
            account["created_at"] = account["created_at"].isoformat()

        return jsonify({
            "count": len(accounts),
            "accounts": accounts
        }), 200

    except Exception as error:
        print("Accounts error:", error)
        return jsonify({
            "error": "Unable to retrieve accounts."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

@api.get("/transactions")
def get_transactions():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                t.transaction_id,
                t.account_id,
                c.display_name,
                a.account_type,
                t.transaction_date,
                t.transaction_type,
                t.amount,
                t.description
            FROM transactions AS t
            JOIN accounts AS a
                ON t.account_id = a.account_id
            JOIN customers AS c
                ON a.customer_id = c.customer_id
            ORDER BY t.transaction_date DESC
        """)

        transactions = cursor.fetchall()

        for transaction in transactions:
            transaction["amount"] = float(transaction["amount"])
            transaction["transaction_date"] = (
                transaction["transaction_date"].isoformat()
            )

        return jsonify({
            "count": len(transactions),
            "transactions": transactions
        }), 200

    except Exception as error:
        print("Transactions error:", error)
        return jsonify({
            "error": "Unable to retrieve transactions."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

from analysis import load_transactions
import numpy as np


@api.get("/analytics")
def get_analytics():
    try:
        df = load_transactions()

        if df.empty:
            return jsonify({
                "message": "No transactions available.",
                "total_transactions": 0
            }), 200

        deposits = df.loc[
            df["transaction_type"] == "Deposit", "amount"
        ]

        withdrawals = df.loc[
            df["transaction_type"] == "Withdrawal", "amount"
        ]

        q1 = df["amount"].quantile(0.25)
        q3 = df["amount"].quantile(0.75)
        iqr = q3 - q1
        threshold = max(20000.0, q3 + 1.5 * iqr)

        df["review_flag"] = np.where(
            df["amount"] >= threshold,
            "Review",
            "Normal"
        )

        flagged = df[df["review_flag"] == "Review"]

        return jsonify({
            "total_transactions": int(len(df)),
            "total_deposits": round(float(deposits.sum()), 2),
            "total_withdrawals": round(float(withdrawals.sum()), 2),
            "net_transaction_flow": round(
                float(deposits.sum() - withdrawals.sum()), 2
            ),
            "average_transaction": round(float(df["amount"].mean()), 2),
            "maximum_transaction": round(float(df["amount"].max()), 2),
            "minimum_transaction": round(float(df["amount"].min()), 2),
            "review_threshold": round(float(threshold), 2),
            "transactions_flagged_for_review": int(len(flagged)),
            "flagged_transaction_ids": [
                int(value) for value in flagged["transaction_id"].tolist()
            ]
        }), 200

    except Exception as error:
        print("Analytics error:", error)
        return jsonify({
            "error": "Unable to calculate analytics."
        }), 500




@api.post("/transactions")
def create_transaction():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Send a valid JSON object."
        }), 400

    account_id = data.get("account_id")
    transaction_type = data.get("transaction_type")
    raw_amount = data.get("amount")
    description = data.get("description", "")

    # Validate account ID.
    if (
        isinstance(account_id, bool)
        or not isinstance(account_id, int)
        or account_id <= 0
    ):
        return jsonify({
            "error": "account_id must be a positive integer."
        }), 400

    # Validate transaction type.
    if transaction_type not in ("Deposit", "Withdrawal"):
        return jsonify({
            "error": "transaction_type must be Deposit or Withdrawal."
        }), 400

    # Validate amount without floating-point rounding.
    try:
        if isinstance(raw_amount, bool) or raw_amount is None:
            raise InvalidOperation

        amount = Decimal(str(raw_amount))

        if not amount.is_finite() or amount <= 0:
            raise InvalidOperation

        if amount.as_tuple().exponent < -2:
            raise InvalidOperation

        if amount > Decimal("9999999999999.99"):
            raise InvalidOperation

    except (InvalidOperation, ValueError, TypeError):
        return jsonify({
            "error": "Amount must be positive and have at most 2 decimal places."
        }), 400

    if not isinstance(description, str) or len(description) > 255:
        return jsonify({
            "error": "description must be text of at most 255 characters."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True)

        # Lock the account row so concurrent requests cannot
        # spend the same simulated balance.
        cursor.execute("""
            SELECT account_id, current_balance
            FROM accounts
            WHERE account_id = %s
            FOR UPDATE
        """, (account_id,))

        account = cursor.fetchone()

        if account is None:
            connection.rollback()
            return jsonify({
                "error": "Account not found."
            }), 404

        current_balance = Decimal(str(account["current_balance"]))

        if transaction_type == "Withdrawal":
            if amount > current_balance:
                connection.rollback()
                return jsonify({
                    "error": "Insufficient simulated balance.",
                    "current_balance": str(current_balance)
                }), 400

            new_balance = current_balance - amount

        else:
            new_balance = current_balance + amount

        # Record the transaction.
        cursor.execute("""
            INSERT INTO transactions (
                account_id,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, %s, %s, %s)
        """, (
            account_id,
            transaction_type,
            amount,
            description.strip()
        ))

        transaction_id = cursor.lastrowid

        # Update the account balance within the same transaction.
        cursor.execute("""
            UPDATE accounts
            SET current_balance = %s
            WHERE account_id = %s
        """, (new_balance, account_id))

        connection.commit()

        return jsonify({
            "message": "Transaction recorded successfully.",
            "transaction_id": transaction_id,
            "account_id": account_id,
            "transaction_type": transaction_type,
            "amount": str(amount),
            "previous_balance": str(current_balance),
            "current_balance": str(new_balance)
        }), 201

    except Exception as error:
        if connection is not None:
            connection.rollback()

        print("Transaction creation error:", error)

        return jsonify({
            "error": "Unable to process transaction."
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
