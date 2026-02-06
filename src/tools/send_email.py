# Tool: Draft/send email
# Simulates sending the final email to the customer.

from langchain_core.tools import tool

@tool
def send_retention_email(customer_name: str, email_address: str, subject: str, body: str):
    """
    Sends a final retention offer email to the customer.
    """
    # In a real app, this would use SMTP. For Capstone, we print to console.
    print("\n" + "="*40)
    print(f"📧 SENDING EMAIL TO: {customer_name} ({email_address})")
    print(f"📝 SUBJECT: {subject}")
    print("-" * 40)
    print(body)
    print("="*40 + "\n")
    
    return "Email sent successfully."