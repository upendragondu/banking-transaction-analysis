
import mysql.connector
from config import DB_CONFIG


def get_connection():
    """Create and return a MySQL database connection."""
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "DB_PASSWORD is missing. Check your .env file."
        )

    return mysql.connector.connect(**DB_CONFIG)
