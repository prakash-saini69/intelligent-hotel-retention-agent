# Tool: Get churn risk

# Allows the agent to check if a customer is "High Risk".


from langchain_core.tools import tool
from src.ml.predictor import get_churn_risk
from src.tools.fetch_bookings import fetch_customer_booking

@tool
def get_customer_risk_score(customer_id: int):
    """
    Calculates the churn risk score (0 to 1) for a specific customer.
    Uses the ML model to predict probability of cancellation.
    """
    # 1. Fetch data first (Agent doesn't need to pass details, just ID)
    customer_data = fetch_customer_booking(customer_id)
    
    if "error" in customer_data:
        return customer_data["error"]

    # 2. Get Prediction
    risk_score = get_churn_risk(customer_data)
    
    return {
        "customer_id": customer_id,
        "risk_score": risk_score,
        "risk_level": "HIGH" if risk_score >= 0.7 else "LOW"
    }