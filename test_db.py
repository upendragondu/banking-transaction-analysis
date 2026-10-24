
from database import get_connection


def test_database():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT DATABASE() AS database_name")
        database = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) AS customer_count FROM customers")
        customers = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) AS account_count FROM accounts")
        accounts = cursor.fetchone()

        cursor.execute(
            "SELECT COUNT(*) AS transaction_count FROM transactions"
        )
        transactions = cursor.fetchone()

        print("Connected successfully!")
        print("Database:", database["database_name"])
        print("Customers:", customers["customer_count"])
        print("Accounts:", accounts["account_count"])
        print("Transactions:", transactions["transaction_count"])

    except mysql.connector.Error as error:
        print("Database connection or query failed:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    import mysql.connector
    test_database()
