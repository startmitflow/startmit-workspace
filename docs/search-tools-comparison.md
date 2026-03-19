# Search Tools Comparison for StartMit

**Date:** 2026-03-16  
**Tools Tested:** Brave Search, Tavily MCP

---

## Quick Comparison

| Feature | Brave Search | Tavily MCP |
|---------|--------------|------------|
| **Setup** | Built-in | Requires MCP config |
| **Result Quality** | Basic links | Pre-extracted content |
| **AI-Optimized** | ❌ | ✅ Built for RAG |
| **Max Results** | 10 | 20 |
| **Content Extraction** | ❌ | ✅ Automatic |
| **Relevance Scoring** | ❌ | ✅ 0-1 scores |
| **Domain Filtering** | Basic (country/lang) | Advanced include/exclude |
| **Crawl Capability** | ❌ | ✅ Full site crawling |
| **Deep Research** | ❌ | ✅ Multi-source synthesis |
| **Cost** | Free | 1000 calls/mo free |

---

## When to Use Which

### Use Brave Search For:
- ✅ Quick facts and current news
- ✅ Simple link discovery
- ✅ Fast, lightweight queries
- ✅ No setup required

### Use Tavily MCP For:
- ✅ Deep research projects
- ✅ Content extraction from URLs
- ✅ Site crawling and mapping
- ✅ Building knowledge bases
- ✅ RAG pipeline integration
- ✅ Domain-specific searches

---

## Example Use Cases

| Task | Best Tool | Why |
|------|-----------|-----|
| "What's the weather?" | Brave | Quick, simple |
| "UG formation steps 2025" | Tavily | Needs comprehensive sources |
| "Crawl competitor website" | Tavily | Only tool with crawl |
| "Latest startup news" | Brave | Current, fast |
| "Create content brief" | Tavily | Multi-source synthesis |
| "Check if site is up" | Brave | Simple status check |

---

## Tavily MCP Configuration

**Installed:** `config/mcporter.json`

**Available Tools:**
1. `tavily_search` - Smart web search
2. `tavily_extract` - Extract content from URLs
3. `tavily_crawl` - Crawl entire websites
4. `tavily_map` - Map site structure
5. `tavily_research` - Deep research (rate limited: 20/min)

**Usage:**
```bash
mcporter call tavily.tavily_search query="..." max_results=10
mcporter call tavily.tavily_crawl url="https://example.com" max_depth=3
```

---

## StartMit Use Case

**Current workflow:**
1. **Tavily** for deep research (competitors, content gaps, market research)
2. **Brave** for quick fact-checking and news
3. **Tavily crawl** for building knowledge bases (e.g., startmit.com analysis)

**Recommended:**
- Use Tavily for 80% of research tasks
- Keep Brave for quick lookups and when Tavily is slow
- Document findings in `memory/` for RAG

---

## Cost Considerations

**Tavily Free Tier:**
- 1,000 API calls/month
- Sufficient for light usage
- Monitor usage with `mcporter` logs

**Upgrade when:**
- Hitting 1,000 calls consistently
- Need higher rate limits (research tool: 20/min)
- Require dedicated support

**Brave Search:**
- Free (no API key needed)
- No rate limits known
- Always available fallback

---

## Performance Notes

**Tavily:**
- Initial connection: ~1-2s
- Search results: ~2-5s
- Crawl large sites: 30-60s (can timeout)
- Research mode: 60s+ (heavy processing)

**Brave:**
- Typically <1s response
- No warmup needed
- Reliable for quick queries

---

## Recommendation for StartMit

**Primary:** Tavily MCP
- Better for content research
- Crawl competitor sites
- Build knowledge bases
- Generate comprehensive briefs

**Fallback:** Brave Search
- Quick lookups
- When Tavily times out
- Simple fact verification

**Integration:**
- Document all research in `memory/`
- Use for content generation
- Build competitor intelligence
- Track market trends

---

*Last updated: 2026-03-16*
