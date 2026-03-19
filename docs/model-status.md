# Model Configuration Status

**Last checked:** 2026-03-16 12:00 CET

## Ollama Server
- **Status:** ✅ Running
- **Endpoint:** http://127.0.0.1:11434
- **Version:** (check with `ollama --version`)

## Available Models (Local)

| Model | Size | Pulled | Status |
|-------|------|--------|--------|
| `qwen3:8b` | 4.87 GB | 2026-03-16 | ✅ Ready |
| `llama3.1:latest` | 4.58 GB | 2026-03-16 | ✅ Ready |

## Configured but NOT Pulled

| Model | Context | Action Needed |
|-------|---------|---------------|
| `kimi-k2.5:cloud` | 128k | Verify if remote/cloud or pull locally |
| `glm-5:cloud` | 128k | `ollama pull glm-5:cloud` |
| `minimax-m2.5:cloud` | 128k | `ollama pull minimax-m2.5:cloud` |

## Fallback Chain (Config)

1. `ollama/kimi-k2.5:cloud` (primary)
2. `ollama/glm-5:cloud`
3. `ollama/qwen3:8b`
4. `ollama/llama3.1:latest`
5. `ollama/minimax-m2.5:cloud`

## Production Readiness

- [x] Ollama server running
- [x] At least 1 model available
- [ ] Pull missing models OR verify cloud access
- [ ] Test fallback behavior
- [ ] Document model selection criteria per task type

## Commands

```powershell
# Check Ollama status
ollama list

# Pull missing models
ollama pull glm-5:cloud
ollama pull minimax-m2.5:cloud
ollama pull kimi-k2.5:cloud

# Test a model
ollama run qwen3:8b "Hello"
```
