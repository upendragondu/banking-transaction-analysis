
import json
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://127.0.0.1:5000"


def post_transaction(payload):
    """Send a transaction request to the running Flask API."""
    request = Request(
        f"{BASE_URL}/transactions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8")
        return error.code, json.loads(body)


class TransactionAPITests(unittest.TestCase):

    def test_valid_deposit(self):
        status, result = post_transaction({
            "account_id": 1,
            "transaction_type": "Deposit",
            "amount": "1.00",
            "description": "Automated test deposit",
        })

        self.assertEqual(status, 201, result)
        self.assertEqual(
            result["transaction_type"], "Deposit"
        )


        print("PASS: Valid deposit accepted.")

    def test_valid_withdrawal(self):
        status, result = post_transaction({
            "account_id": 1,
            "transaction_type": "Withdrawal",
            "amount": "1.00",
            "description": "Automated test withdrawal",
        })

        self.assertEqual(status, 201, result)
        self.assertEqual(result["transaction_type"], "Withdrawal")

        print("PASS: Valid withdrawal accepted.")

    def test_zero_amount_rejected(self):
        status, result = post_transaction({
            "account_id": 1,
            "transaction_type": "Deposit",
            "amount": "0",
            "description": "Invalid test",
        })

        self.assertEqual(status, 400, result)
        print("PASS: Zero amount rejected.")

    def test_insufficient_balance_rejected(self):
        status, result = post_transaction({
            "account_id": 1,
            "transaction_type": "Withdrawal",
            "amount": "999999999.00",
            "description": "Overdraft protection test",
        })

        self.assertEqual(status, 400, result)
        self.assertIn("Insufficient", result["error"])

        print("PASS: Insufficient balance rejected.")

    def test_nonexistent_account_rejected(self):
        status, result = post_transaction({
            "account_id": 999999,
            "transaction_type": "Deposit",
            "amount": "1.00",
            "description": "Nonexistent account test",
        })

        self.assertEqual(status, 404, result)
        print("PASS: Nonexistent account rejected.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
