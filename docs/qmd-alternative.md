# QMD Alternative: Local Document Search

Since QMD CLI has Windows compatibility issues, here's an alternative using existing tools.

## Option 1: PowerShell + ripgrep (Fast)

```powershell
# Search all markdown files
rg -i "UG formation" --type md

# Search with context
rg -i "UG formation" --type md -C 3

# Fuzzy search
rg -i "form.*gmbh" --type md
```

## Option 2: Node.js Script (Custom)

Create `scripts/search-docs.js`:

```javascript
const fs = require('fs');
const path = require('path');
const glob = require('glob');

function searchDocs(query, dir = '.') {
  const files = glob.sync('**/*.md', { cwd: dir });
  const results = [];
  
  for (const file of files) {
    const content = fs.readFileSync(path.join(dir, file), 'utf8');
    const lines = content.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().includes(query.toLowerCase())) {
        results.push({
          file,
          line: i + 1,
          text: lines[i].trim()
        });
      }
    }
  }
  
  return results;
}

// Usage
const query = process.argv[2] || 'StartMit';
const results = searchDocs(query);
console.log(`Found ${results.length} matches for "${query}":`);
results.forEach(r => console.log(`  ${r.file}:${r.line}: ${r.text}`));
```

## Option 3: Use Tavily MCP (Already Working)

```bash
mcporter call tavily.tavily_search query="site:startmit.com UG formation"
```

## Option 4: Simple VS Code Search

Use VS Code's built-in search (Ctrl+Shift+F) across the workspace.

---

## Recommendation

For now, use **Option 1 (ripgrep)** for fast local search, or **Tavily MCP** for web+local hybrid search.

QMD can be revisited when Windows support improves.
