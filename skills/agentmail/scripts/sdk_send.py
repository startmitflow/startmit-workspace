from agentmail import AgentMail

client = AgentMail(api_key='am_us_a825ac718c74845bc0d748f46c0cd9b3327fc57a5f5f983785ac729f840ea3a9')

# Try to send using SDK
result = client.inboxes.messages.send(
    inbox_id='startmit@agentmail.to',
    to='mod@example.com',
    subject='Test from StartMit',
    text='This is a test email from your StartMit AgentMail inbox.\n\n- Flow'
)

print(f"Sent! Message ID: {result.message_id}")
print(f"Thread ID: {result.thread_id}")
