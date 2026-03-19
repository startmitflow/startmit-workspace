from agentmail import AgentMail

client = AgentMail(api_key='am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9')
messages = client.messages.list(inbox_id='startmit@agentmail.to', limit=5)

print(f"Found {len(messages.messages)} messages:")
for msg in messages.messages:
    sender = msg.from_address[0]['email'] if msg.from_address else 'unknown'
    print(f"  - From: {sender}, Subject: {msg.subject}, Date: {msg.created_at}")
