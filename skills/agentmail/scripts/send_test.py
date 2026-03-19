import httpx
import urllib.parse

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"
INBOX = "startmit@agentmail.to"
INBOX_ENCODED = urllib.parse.quote(INBOX, safe='')

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

payload = {
    "to": ["mod@example.com"],
    "subject": "Test Email from StartMit",
    "text": "This is a test email from your StartMit AgentMail inbox.\n\nIf you received this, outbound email is working correctly!\n\n- Flow (StartMit Assistant)",
    "html": "<p>This is a test email from your <strong>StartMit</strong> AgentMail inbox.</p><p>If you received this, outbound email is working correctly!</p><p>- Flow (StartMit Assistant)</p>"
}

url = f"https://api.agentmail.to/v0/inboxes/{INBOX_ENCODED}/messages"
print(f"Sending to: {url}")

response = httpx.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print("[OK] Email sent successfully!")
    print(f"  Message ID: {data.get('message_id')}")
    print(f"  Thread ID: {data.get('thread_id')}")
else:
    print(f"[FAIL] Status: {response.status_code}")
    print(f"  {response.text}")
