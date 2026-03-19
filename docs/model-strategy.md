# Model Strategy for StartMit

**Adopted:** 2026-03-16

## Overview

Mixed model allocation optimized for founder workflow:
- **Main session:** Fast, interactive responses
- **Subagents:** Quality document generation without blocking

## Model Allocation

| Use Case | Model | Why |
|----------|-------|-----|
| **Main session** | `kimi-k2.5:cloud` | 4s response, best for interactive work |
| **Subagents** | `glm-5:cloud` | 10-28s, good quality, runs async |
| **Fallbacks** | `minimax-m2.5:cloud`, `qwen3:8b`, `llama3.1:latest` | Emergency only |

## When to Use Which

### Use Main Session (kimi-k2.5) for:
- Quick questions and clarifications
- Planning and decision-making
- Reviewing subagent outputs
- Interactive brainstorming

### Use Subagents (glm-5) for:
- Document generation (checklists, templates, SOPs)
- Research tasks (web search, content gathering)
- Batch processing (multiple clients, multiple outputs)
- Long-form content (landing pages, email sequences)

## Performance Benchmarks

| Model | Avg Time | Best For | Avoid For |
|-------|----------|----------|-----------|
| kimi-k2.5:cloud | 4s | Everything interactive | — |
| glm-5:cloud | 10-30s | Documents, async work | Real-time chat |
| minimax-m2.5:cloud | 11s | Fallback documents | — |
| qwen3:8b (local) | 57s+ | Emergency only | Production |
| llama3.1:latest (local) | 58s+ | Emergency only | Production |

## Commands

```powershell
# Check current model
openclaw status

# Override per-task (if needed)
# In subagent spawn: model="ollama/kimi-k2.5:cloud"
```

## Files

- `docs/model-status.md` — Current model availability
- `docs/model-strategy.md` — This file

---

*Strategy: Optimize for founder leverage — fast interactions, quality async outputs.*
