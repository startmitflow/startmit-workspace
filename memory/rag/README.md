# StartMit RAG Integration Guide

**Purpose:** Connect StartMit knowledge base to WhatsApp AI RAG system  
**Format:** JSONL embeddings + structured metadata  
**Last Updated:** 2026-03-16

---

## File Structure

```
memory/rag/
├── startmit-embeddings.jsonl    # Chunked knowledge (15 records)
└── README.md                     # This file
```

---

## Data Format

Each line in `startmit-embeddings.jsonl`:

```json
{
  "id": "startmit-001",
  "text": "...",              // Text to embed and search
  "metadata": {                 // Filtering/attribution
    "source": "homepage",
    "category": "overview",
    "url": "https://startmit.com/",
    "region": "germany",
    "language": "german"
  }
}
```

---

## Categories

| Category | Description | Example IDs |
|----------|-------------|-------------|
| `overview` | Company description | 001-002 |
| `services` | Service offerings | 003 |
| `legal` | German legal info | 004-005, 011 |
| `contact` | Contact details | 006, 013 |
| `audience` | Target customers | 007 |
| `positioning` | Unique value props | 008 |
| `competitors` | Competitor info | 009 |
| `infrastructure` | Tech stack | 010 |
| `process` | Formation process | 011 |
| `gaps` | Identified gaps | 012 |
| `booking` | Booking links | 013 |
| `compliance` | Legal pages | 014 |
| `localization` | German content | 015 |

---

## Integration Options

### Option 1: Load into Vector DB

```python
import json

# Load chunks
with open('memory/rag/startmit-embeddings.jsonl') as f:
    chunks = [json.loads(line) for line in f]

# Embed and store
for chunk in chunks:
    embedding = embed_model.encode(chunk['text'])
    vector_db.add(
        id=chunk['id'],
        embedding=embedding,
        text=chunk['text'],
        metadata=chunk['metadata']
    )
```

### Option 2: Simple Text Search

```python
# Load as context for prompt
with open('memory/rag/startmit-embeddings.jsonl') as f:
    context = "\n\n".join([
        json.loads(line)['text'] 
        for line in f
    ])

# Use in prompt
prompt = f"""
Context about StartMit:
{context}

User question: {question}

Answer based on the context above.
"""
```

### Option 3: WhatsApp AI Integration

```javascript
// Load chunks on startup
const chunks = require('./memory/rag/startmit-embeddings.jsonl')
  .split('\n')
  .filter(Boolean)
  .map(JSON.parse);

// Search function
function searchStartMit(query, category = null) {
  // Filter by category if specified
  const filtered = category 
    ? chunks.filter(c => c.metadata.category === category)
    : chunks;
  
  // Simple keyword search (replace with semantic search)
  return filtered.filter(chunk => 
    chunk.text.toLowerCase().includes(query.toLowerCase())
  );
}

// Use in WhatsApp handler
app.message(async (ctx) => {
  const relevant = searchStartMit(ctx.message.text);
  const context = relevant.map(r => r.text).join('\n\n');
  
  const response = await ai.complete({
    prompt: `Context:\n${context}\n\nUser: ${ctx.message.text}`,
    system: "You are StartMit's AI assistant. Use the context to answer accurately."
  });
  
  ctx.reply(response);
});
```

---

## Query Patterns

### Company Info
```
"What does StartMit do?"
"Tell me about StartMit"
"Who are StartMit?"
→ Categories: overview, services
```

### Services
```
"What services do you offer?"
"How can you help me?"
"What is UG formation?"
→ Categories: services, legal
```

### Contact
```
"How do I contact you?"
"What is your email?"
"Where are you located?"
→ Categories: contact
```

### Pricing
```
"How much does it cost?"
"What is your pricing?"
→ Categories: gaps (explain no public pricing, redirect to consultation)
```

### Process
```
"How long does UG formation take?"
"What is the formation process?"
→ Categories: process, legal
```

### Competitors
```
"How are you different from firma.de?"
"Why choose StartMit over others?"
→ Categories: positioning, competitors
```

---

## Updating the Knowledge Base

**When to update:**
- Website content changes significantly
- New services added
- Pricing structure published
- New competitors emerge
- Process changes (legal updates)

**How to update:**
1. Re-crawl with Tavily: `mcporter call tavily.tavily_crawl url="https://startmit.com"`
2. Update `startmit-embeddings.jsonl`
3. Re-index in vector DB
4. Test queries

---

## Fallback Behavior

When RAG has no relevant chunks:

1. **Acknowledge:** "I don't have specific information about that..."
2. **Redirect:** "Let me connect you with a human at support@startmit.com"
3. **Capture:** Log the question for future knowledge base updates

---

## Example WhatsApp Conversations

### Example 1: Service Inquiry
**User:** "What services do you offer?"
**RAG hit:** ID 003 (core services)
**Response:** "StartMit offers three main services: UG/GmbH company formation, CRM automation, and monthly business support. We help streamline operations, handle tax compliance, and scale your venture..."

### Example 2: Pricing Question
**User:** "How much does UG formation cost?"
**RAG hit:** ID 012 (content gaps)
**Response:** "I don't see public pricing on our website. Every formation is customized based on your needs. Would you like to book a free consultation at https://app.suitedash.com/frm/2rgqoD8pMhoHDPmBJ to get a personalized quote?"

### Example 3: Process Question
**User:** "How long does UG formation take?"
**RAG hit:** ID 011 (formation process)
**Response:** "UG formation typically takes 1-2 weeks total: 1 day for preparation and notary appointment, 1-3 days for bank account opening, and 2-6 weeks for commercial registration. We guide you through each step."

---

## Technical Notes

**Chunking strategy:**
- Each chunk is self-contained
- ~100-200 tokens per chunk
- Metadata for filtering
- No overlapping content

**Embedding model:**
- Recommended: OpenAI text-embedding-3-small or similar
- Dimension: 1536 (OpenAI) or 768 (HuggingFace)
- Normalize embeddings before storage

**Vector database options:**
- Pinecone (managed)
- Weaviate (open source)
- Chroma (local)
- Simple in-memory (for testing)

---

*Ready for WhatsApp AI integration*
