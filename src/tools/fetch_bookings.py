# Tool: Get booking details
# Allows the agent to look up a customer's details from the database.


import sqlite3
import pandas as pd
from langchain_core.tools import tool

# Path to your database
DB_PATH = "data/hotel_retention.db"

@tool
def fetch_customer_booking(customer_id: int):
    """
    Fetches the latest booking details for a specific customer ID from the database.
    Returns: A dictionary containing name, room_type, price, and cancellation history.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM bookings WHERE customer_id = ?"
        df = pd.read_sql(query, conn, params=(customer_id,))
        conn.close()

        if df.empty:
            return {"error": f"Customer ID {customer_id} not found."}
        
        # Return the first matching row as a dictionary
        return df.iloc[0].to_dict()
    except Exception as e:
        return {"error": str(e)}