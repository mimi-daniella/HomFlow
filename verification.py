import os, requests
from flask import url_for

def send_verification_email(user_email, token):
    domain = os.environ.get("MAILGUN_DOMAIN")
    api_key = os.environ.get("MAILGUN_API_KEY")
    link = url_for('verify', token=token, _external=True)

    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"HomFlow <no-reply@{domain}>",
            "to": [user_email],
            "subject": "Verify your email",
            "text": f"Click the link to verify your account: {link}"
        }
    )