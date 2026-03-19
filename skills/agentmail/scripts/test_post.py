import httpx
import urllib.parse

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"
INBOX = "startmit@agentmail.to"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

url = f"https://api.agentmail.to/v0/inboxes/{urllib.parse.quote(INBOX, safe='')}/messages"

# Try different payload formats
payloads = [
    {"to": "mod@example.com", "subject": "Test", "text": "Hello"},
    {"to": ["mod@example.com"], "subject": "Test", "text": "Hello"},
    {"to": "mod@example.com", "to_address": "mod@example.com", "subject": "Test", "text": "Hello"},
]

for i, payload in enumerate(payloads):
    print(f"\n--- Test {i+1} ---")
    print(f"Payload: {payload}")
    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
