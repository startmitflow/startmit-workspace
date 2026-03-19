import httpx
import urllib.parse

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"
INBOX = "startmit@agentmail.to"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Try different endpoint formats
endpoints = [
    f"https://api.agentmail.to/v0/inboxes/{urllib.parse.quote(INBOX, safe='')}/messages",
    f"https://api.agentmail.to/v0/inboxes/{INBOX}/messages",
    f"https://api.agentmail.to/v0/messages",
]

payload = {
    "to": ["mod@example.com"],
    "subject": "Test Email from StartMit",
    "text": "This is a test email from your StartMit AgentMail inbox.\n\nIf you received this, outbound email is working correctly!\n\n- Flow (StartMit Assistant)",
}

for url in endpoints:
    print(f"\nTrying: {url}")
    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Success: {response.json()}")
        break
    else:
        print(f"Response: {response.text[:200]}")
