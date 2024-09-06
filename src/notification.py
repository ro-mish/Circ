import requests

def send_notification(message):
    """
    Send a notification with the given message.
    This is a placeholder function - implement your preferred notification method here.
    """
    print(f"Notification: {message}")
    
    # Example: Send a message to a Slack webhook
    # webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    # requests.post(webhook_url, json={"text": message})