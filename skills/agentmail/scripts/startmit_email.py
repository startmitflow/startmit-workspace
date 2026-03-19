#!/usr/bin/env python3
"""
Send email via AgentMail for StartMit
Usage: python scripts/send_email.py recipient@example.com "Subject" "Body text"
"""

import sys
import os

# Add the agentmail skill path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentmail import AgentMail

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"
INBOX = "startmit@agentmail.to"

def send_email(to, subject, text, html=None):
    """Send an email from the StartMit inbox."""
    client = AgentMail(api_key=API_KEY)
    
    message = client.inboxes.messages.send(
        inbox_id=INBOX,
        to=to,
        subject=subject,
        text=text,
        html=html or f"<p>{text}</p>"
    )
    
    print(f"Email sent: {message.message_id}")
    return message

def check_inbox(limit=10):
    """Check recent messages in the StartMit inbox."""
    client = AgentMail(api_key=API_KEY)
    inbox = client.inboxes.get(INBOX)
    messages = inbox.messages.list(limit=limit)
    
    for msg in messages.messages:
        print(f"[{msg.created_at}] {msg.from_address[0]['email']}: {msg.subject}")
    
    return messages

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python send_email.py recipient@example.com 'Subject' 'Body text'")
        print("  python send_email.py --check")
        sys.exit(1)
    
    if sys.argv[1] == "--check":
        check_inbox()
    else:
        to = sys.argv[1]
        subject = sys.argv[2] if len(sys.argv) > 2 else "Hello from StartMit"
        text = sys.argv[3] if len(sys.argv) > 3 else "This is a test email from StartMit."
        send_email(to, subject, text)
