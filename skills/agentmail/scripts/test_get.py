import httpx
import urllib.parse

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"
INBOX = "startmit@agentmail.to"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Try GET messages first
url = f"https://api.agentmail.to/v0/inboxes/{urllib.parse.quote(INBOX, safe='')}/messages"
print(f"GET {url}")
response = httpx.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Try without v0
url2 = f"https://api.agentmail.to/inboxes/{urllib.parse.quote(INBOX, safe='')}/messages"
print(f"\nGET {url2}")
response2 = httpx.get(url2, headers=headers)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text[:500]}")
