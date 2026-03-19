import httpx

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"
INBOX = "startmit@agentmail.to"

headers = {"Authorization": f"Bearer {API_KEY}"}

response = httpx.get(
    f"https://api.agentmail.to/v0/inboxes/{INBOX}/messages",
    headers=headers,
    params={"limit": 10}
)

data = response.json()
print(f"Found {data.get('count', 0)} messages:")

for msg in data.get('messages', []):
    sender = msg.get('from_address', [{}])[0].get('email', 'unknown') if msg.get('from_address') else 'unknown'
    print(f"  - From: {sender}")
    print(f"    Subject: {msg.get('subject', 'No subject')}")
    print(f"    Date: {msg.get('created_at', 'unknown')}")
    print()
