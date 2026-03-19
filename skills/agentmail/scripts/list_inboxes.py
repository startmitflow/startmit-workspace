import httpx

API_KEY = "am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9"

headers = {"Authorization": f"Bearer {API_KEY}"}

# List inboxes
response = httpx.get("https://api.agentmail.to/v0/inboxes", headers=headers)
print(f"List inboxes: {response.status_code}")
print(response.text[:500] if response.text else "No response")
