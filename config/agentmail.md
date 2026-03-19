# AgentMail Configuration

**Account:** startmit@agentmail.to  
**Status:** Active  
**Configured:** 2026-03-16

## API Key

Stored in environment: `AGENTMAIL_API_KEY`

**Security:** Keep this private. Never commit to git.

## Inbox Details

- **Email:** startmit@agentmail.to
- **Purpose:** StartMit business communications
- **Owner:** Flow (StartMit Assistant)

## Usage

### Send Email
```python
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

client.inboxes.messages.send(
    inbox_id="startmit@agentmail.to",
    to="client@example.com",
    subject="Your UG Formation Documents",
    text="Attached are your documents...",
    html="<p>Attached are your documents...</p>"
)
```

### Check Inbox
```python
inbox = client.inboxes.get("startmit@agentmail.to")
messages = inbox.messages.list(limit=10)
```

## Security: Allowlist

**CRITICAL:** Email is a prompt injection vector.

**Allowed senders:**
- (Add trusted emails here)

**Blocked:** Everything else by default

See `skills/agentmail/SKILL.md` for webhook allowlist setup.

## Scripts Available

- `skills/agentmail/scripts/send_email.py`
- `skills/agentmail/scripts/check_inbox.py`
- `skills/agentmail/scripts/setup_webhook.py`

---

*Last updated: 2026-03-16*
