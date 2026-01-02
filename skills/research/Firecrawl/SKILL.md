---
name: Firecrawl
description: Use Firecrawl and Jina for fetching web content. ALWAYS prefer Firecrawl over WebFetch for all web fetching tasks—it produces cleaner output, handles JavaScript-heavy pages, and has no content truncation. This skill should be used when fetching URLs, scraping web pages, converting URLs to markdown, extracting web content, searching the web, crawling sites, mapping URLs, LLM-powered extraction, or autonomous data gathering with the Agent API. Provides complete coverage of Firecrawl v2 API endpoints.
---

# Firecrawl & Jina Web Scraping

This skill provides comprehensive guidance for web scraping and content extraction using Firecrawl (v2 API with Agent) and Jina Reader.

## CRITICAL: Always Use Firecrawl Over WebFetch

**ALWAYS prefer `firecrawl URL` over the WebFetch tool for fetching web content.**

Why Firecrawl is better:
- Produces cleaner markdown output
- Better handling of JavaScript-heavy pages
- Automatic file saving for later reference
- No token limits or content truncation
- Handles complex page structures better

```bash
# ALWAYS DO THIS for fetching URLs:
firecrawl https://docs.example.com/api

# NEVER use WebFetch when Firecrawl is available
```

## When to Use This Skill

Use this skill when:
- Converting web pages to markdown or clean text
- Scraping structured data from websites
- Performing web searches with automatic content extraction
- Analyzing documentation, articles, or web content
- Extracting data for AI/LLM processing
- Research tasks requiring web content retrieval
- **Autonomous data gathering** - describe what you want, let the agent find/extract it
- **Lead generation, competitive research, or dataset curation** across multiple sites
- **Mapping entire websites** to discover all URLs
- **LLM-powered extraction** with structured schemas

## Available Tools

### 1. Firecrawl CLI (Local Command)

**Command**: `firecrawl URL`

Scrapes a single webpage and converts it to markdown, automatically saving to `~/Desktop/Screencaps & Chats/Web-Scrapes/`

**When to use**:
- Single page scraping
- Documentation conversion
- Article extraction
- When you need clean markdown output

**Example**:
```bash
firecrawl https://docs.anthropic.com/api/introduction
```

**Output location**: Files saved to `~/Desktop/Screencaps & Chats/Web-Scrapes/`

### 2. Jina Reader CLI (Local Command)

**Command**: `jina URL`

Alternative to Firecrawl - scrapes webpage and converts to markdown with different parsing approach.

**When to use**:
- When Firecrawl fails or produces suboptimal results
- Alternative parsing for complex pages
- Backup scraping method

**Example**:
```bash
jina https://example.com/article
```

### 3. Firecrawl API Script (Full v2 Coverage)

**Command**: `python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py <command>`

Complete access to ALL Firecrawl v2 API endpoints.

**Requires**: `FIRECRAWL_API_KEY` environment variable
**Install**: `pip install firecrawl-py requests`

**Available Commands**:

| Command | Description |
|---------|-------------|
| `search` | Web search with optional content scraping |
| `scrape` | Extract content from a single URL |
| `batch-scrape` | Scrape multiple URLs concurrently |
| `crawl` | Crawl entire websites, following links |
| `map` | Discover all URLs on a website |
| `extract` | LLM-powered structured data extraction |
| `agent` | Autonomous multi-page extraction (no URLs required!) |
| `crawl-status` | Check async crawl job status |
| `batch-status` | Check batch scrape job status |
| `extract-status` | Check extract job status |
| `crawl-cancel` | Cancel a running crawl job |
| `batch-cancel` | Cancel a running batch scrape job |
| `status` | Check agent job status |

---

## Command Reference

### search - Web Search

Search the web with optional content scraping.

```bash
# Basic search
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py search "web scraping best practices" -n 10

# Search GitHub repos only
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py search "python web scraping" --categories github

# Search research papers
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py search "transformer architecture" --categories research

# Search with content scraping
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py search "firecrawl examples" --scrape

# Time-filtered search (recent content)
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py search "AI news" --time qdr:d  # last day

# Location-based search
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py search "tech startups" --location "San Francisco"
```

**Parameters**:
- `-n, --limit`: Number of results (default: 10)
- `--categories`: Filter by github, research, pdf
- `--sources`: Result types: web, news, images
- `--time`: Time filter: qdr:h (hour), qdr:d (day), qdr:w (week), qdr:m (month)
- `--location`: Geotarget results
- `--scrape`: Also scrape content from results
- `--json`: Output raw JSON

---

### scrape - Single URL Extraction

Extract content from a single URL.

```bash
# Basic scrape
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py scrape "https://docs.firecrawl.dev/"

# With specific formats
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py scrape "https://example.com" --formats markdown html links

# Include navigation/footer
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py scrape "https://example.com" --full
```

**Parameters**:
- `--formats`: Output formats: markdown, html, links, screenshot
- `--full`: Include navigation and footer (default: main content only)
- `--json`: Output raw JSON

---

### batch-scrape - Multiple URL Scraping

Scrape multiple URLs concurrently. Returns a job ID for status polling.

```bash
# Batch scrape multiple URLs
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py batch-scrape https://example.com/page1 https://example.com/page2 https://example.com/page3

# Check status
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py batch-status <job_id>

# Cancel if needed
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py batch-cancel <job_id>
```

**Parameters**:
- `urls`: One or more URLs to scrape
- `--formats`: Output formats: markdown, html, links, screenshot
- `--full`: Include navigation and footer
- `--json`: Output raw JSON

---

### crawl - Website Crawling

Crawl entire websites, following links.

```bash
# Basic crawl (50 pages max)
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl "https://docs.example.com"

# Limit pages
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl "https://docs.example.com" --limit 20

# Limit depth
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl "https://docs.example.com" --depth 2

# Filter paths
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl "https://docs.example.com" --include "/api" "/guides"

# Async crawl for large sites
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl "https://docs.example.com" --async
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl-status <job_id>
```

**Parameters**:
- `-n, --limit`: Maximum pages to crawl (default: 50)
- `--depth`: Maximum link depth to follow
- `--include`: Only crawl URLs matching these paths (regex)
- `--exclude`: Skip URLs matching these paths (regex)
- `--async`: Return job ID for polling (use crawl-status)
- `--json`: Output raw JSON

---

### map - URL Discovery

Discover all URLs on a website. Fast way to get a site's structure.

```bash
# Map a website (up to 5000 URLs)
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py map "https://example.com"

# Limit results
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py map "https://example.com" -n 100

# Search to order by relevance
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py map "https://docs.example.com" --search "API authentication"

# Exclude subdomains
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py map "https://example.com" --no-subdomains

# Sitemap only mode
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py map "https://example.com" --sitemap only
```

**Parameters**:
- `-n, --limit`: Max URLs to return (default: 5000, max: 100000)
- `--search`: Search query to order results by relevance
- `--no-subdomains`: Exclude subdomains
- `--sitemap`: Sitemap handling: include (default), skip, or only
- `--json`: Output raw JSON

---

### extract - LLM-Powered Extraction

Extract structured data from pages using LLM. Supports wildcards for crawling.

```bash
# Extract with prompt
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py extract "https://example.com/*" --prompt "Find all pricing information"

# Extract with JSON schema
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py extract "https://example.com/pricing" \
  --schema '{"type": "object", "properties": {"price": {"type": "string"}, "features": {"type": "array"}}}'

# Enable web search for additional context
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py extract "https://example.com/*" \
  --prompt "Find company funding information" --web-search

# Check status
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py extract-status <job_id>
```

**Parameters**:
- `urls`: URLs to extract from (supports wildcards like `example.com/*`)
- `--prompt, -p`: Natural language description of data to extract
- `--schema`: JSON schema for structured output
- `--web-search`: Enable web search for additional data
- `--sources`: Show sources in response
- `--json`: Output raw JSON

---

### agent - Autonomous Extraction

The most powerful feature. Describe what data you want - the agent searches, navigates, and extracts automatically. **URLs are optional.**

```bash
# No URLs needed - agent finds the data
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py agent "Find YC W24 AI startups with funding info"

# With specific URLs (faster)
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py agent "Extract all pricing tiers" \
  --urls https://firecrawl.dev/pricing https://competitor.com/pricing

# Async for long jobs
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py agent "Find 50 AI startups" --async
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py status <job_id>
```

**Parameters**:
- `prompt`: Natural language description of data to find (max 10,000 chars)
- `--urls`: Optional URLs to focus extraction on
- `--async`: Start async job, return job ID
- `--json`: Output raw JSON

**Use cases**:
- Lead generation without knowing URLs
- Competitive research across multiple sites
- Dataset curation from scattered sources
- Complex navigation (login flows, pagination, dynamic content)

---

## Python SDK Examples

For more control, use the Firecrawl Python SDK directly:

### Agent with Structured Schema

```python
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key="fc-YOUR_API_KEY")

class Company(BaseModel):
    name: str = Field(description="Company name")
    contact_email: Optional[str] = Field(None, description="Contact email")
    funding: Optional[str] = Field(None, description="Funding amount")

class CompaniesSchema(BaseModel):
    companies: List[Company]

result = app.agent(
    prompt="Find YC W24 dev tool companies with contact info",
    schema=CompaniesSchema
)

for company in result.data.companies:
    print(f"{company.name}: {company.contact_email}")
```

### Async Agent for Large Jobs

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-YOUR_API_KEY")

# Start async job
agent_job = app.start_agent(prompt="Find 100 AI companies with funding info")

# Check status later
status = app.get_agent_status(agent_job.id)
if status.status == 'completed':
    print(status.data)
```

---

## Common Workflows

### Workflow 1: Single Page Scraping

```bash
# Option 1: Firecrawl CLI (simplest)
firecrawl https://example.com/page

# Option 2: API script
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py scrape "https://example.com/page"

# Option 3: Jina (backup)
jina https://example.com/page
```

### Workflow 2: Documentation Crawling

```bash
# Map the site first
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py map "https://docs.example.com" --search "API"

# Crawl relevant sections
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py crawl "https://docs.example.com" \
  --include "/api" "/guides" --limit 50
```

### Workflow 3: Competitive Pricing Research

```bash
# Use agent - no URLs needed
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py agent \
  "Compare pricing tiers for Firecrawl, Apify, and ScrapingBee - extract all plans with prices and features"
```

### Workflow 4: Lead Generation

```bash
# Use agent for autonomous lead finding
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py agent \
  "Find 20 B2B SaaS companies in developer tools with contact emails"
```

### Workflow 5: Batch URL Scraping

```bash
# Start batch job
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py batch-scrape \
  https://site.com/page1 https://site.com/page2 https://site.com/page3

# Check status
python3 ~/.claude/skills/Firecrawl/scripts/firecrawl_api.py batch-status <job_id>
```

---

## Tool Selection Guide

| Task | Best Tool |
|------|-----------|
| Single page → markdown | `firecrawl URL` CLI |
| Find info, don't have URLs | **agent** command |
| Lead generation at scale | **agent** command |
| Scrape multiple known URLs | **batch-scrape** command |
| Crawl entire documentation site | **crawl** command |
| Discover all site URLs | **map** command |
| Extract structured data | **extract** command |
| Quick fallback scraping | `jina URL` CLI |

### When to use Agent:
- Don't have specific URLs
- Data scattered across multiple sites
- Complex navigation required
- Lead generation, competitive research
- Need structured output (use schemas)

### When to use Crawl:
- Have a starting URL
- Want to follow links systematically
- Documentation sites, blogs

### When to use Extract:
- Have specific URLs (with wildcards)
- Need LLM-powered parsing
- Structured schema output

### When to use Map:
- Need to discover all URLs on a site
- Planning a crawl
- Understanding site structure

---

## File Management

Scraped files from CLI commands are saved to:
```
~/Desktop/Screencaps & Chats/Web-Scrapes/
```

**Filename format**: `https-docs-example-com-api.md`

```bash
# List recent scrapes
ls -lt ~/Desktop/Screencaps\ \&\ Chats/Web-Scrapes/ | head -10
```

---

## Troubleshooting

### Firecrawl fails to scrape:
1. Try Jina: `jina URL`
2. Check if URL is accessible in browser
3. Some sites block automated scraping

### API errors:
1. Verify FIRECRAWL_API_KEY is set: `echo $FIRECRAWL_API_KEY`
2. Check API key validity
3. Review error message for rate limits or quota

### Async job not completing:
1. Check status: `crawl-status`, `batch-status`, or `extract-status`
2. Large jobs may take several minutes
3. Cancel if stuck: `crawl-cancel` or `batch-cancel`

---

## Reference Documentation

For detailed API documentation and advanced features, see:
- `references/firecrawl-api.md` - Firecrawl Search API reference
- `references/firecrawl-agent-api.md` - Firecrawl Agent API for autonomous extraction
