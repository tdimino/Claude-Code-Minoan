# ArXiv MCP Server Tools Reference

Comprehensive reference for the arxiv-mcp-server (blazickjp/arxiv-mcp-server).

## Installation

```bash
# Via uv (recommended)
uv tool install arxiv-mcp-server

# Via Smithery
npx -y @smithery/cli install arxiv-mcp-server --client claude
```

## Configuration

In `.mcp.json` or Claude MCP settings:
```json
{
  "arxiv": {
    "command": "uv",
    "args": ["tool", "run", "arxiv-mcp-server", "--storage-path", "~/.arxiv-papers"]
  }
}
```

Papers are stored locally at the specified storage path for faster subsequent access.

## Available Tools

### search_papers

Search arXiv for papers matching query criteria.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `max_results` | number | No | Maximum papers to return (default: 10) |
| `sort_by` | string | No | Sort order: "relevance" or "submitted_date" |
| `sort_order` | string | No | "ascending" or "descending" |
| `categories` | string[] | No | ArXiv categories to filter |

**Examples**:

Basic search:
```javascript
search_papers({
  query: "large language models",
  max_results: 20
})
```

Category-filtered search:
```javascript
search_papers({
  query: "attention mechanism",
  categories: ["cs.CL", "cs.LG"],
  max_results: 30
})
```

Recent papers first:
```javascript
search_papers({
  query: "multimodal learning",
  sort_by: "submitted_date",
  sort_order: "descending",
  max_results: 25
})
```

### download_paper

Download a paper by its arXiv ID for local storage.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `arxiv_id` | string | Yes | ArXiv paper ID (e.g., "2301.00234") |

**Example**:
```javascript
download_paper({
  arxiv_id: "2301.00234"
})
```

**Notes**:
- Papers stored at configured storage path (~/.arxiv-papers by default)
- Downloaded papers can be read faster with read_paper
- PDF and metadata both stored

### list_papers

List all downloaded papers in local storage.

**Parameters**: None

**Example**:
```javascript
list_papers()
```

**Returns**: List of locally stored papers with IDs and metadata.

### read_paper

Read the content of a downloaded paper.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `arxiv_id` | string | Yes | ArXiv paper ID |

**Example**:
```javascript
read_paper({
  arxiv_id: "2301.00234"
})
```

**Notes**:
- Paper must be downloaded first
- Returns extracted text content
- Useful for detailed analysis

## ArXiv Categories

### Computer Science
| Category | Description |
|----------|-------------|
| cs.AI | Artificial Intelligence |
| cs.CL | Computation and Language (NLP) |
| cs.CV | Computer Vision and Pattern Recognition |
| cs.LG | Machine Learning |
| cs.NE | Neural and Evolutionary Computing |
| cs.RO | Robotics |
| cs.HC | Human-Computer Interaction |
| cs.IR | Information Retrieval |
| cs.SE | Software Engineering |
| cs.DB | Databases |
| cs.DC | Distributed Computing |
| cs.CR | Cryptography and Security |

### Statistics
| Category | Description |
|----------|-------------|
| stat.ML | Machine Learning |
| stat.ME | Methodology |
| stat.TH | Statistics Theory |

### Mathematics
| Category | Description |
|----------|-------------|
| math.OC | Optimization and Control |
| math.ST | Statistics Theory |
| math.NA | Numerical Analysis |

### Physics (Relevant to ML)
| Category | Description |
|----------|-------------|
| physics.comp-ph | Computational Physics |
| quant-ph | Quantum Physics |

### Electrical Engineering
| Category | Description |
|----------|-------------|
| eess.SP | Signal Processing |
| eess.IV | Image and Video Processing |
| eess.AS | Audio and Speech Processing |

## ArXiv ID Format

ArXiv IDs follow the format: `YYMM.NNNNN` or `YYMM.NNNNNvN`

**Examples**:
- `2301.00234` - January 2023, paper #234
- `2301.00234v2` - Version 2 of the paper
- `1706.03762` - "Attention Is All You Need" (June 2017)

**Extracting from URLs**:
```
https://arxiv.org/abs/2301.00234 → 2301.00234
https://arxiv.org/pdf/2301.00234.pdf → 2301.00234
```

## Search Query Syntax

### Basic Queries
```
"transformer architecture"     # Phrase search
transformer AND attention      # Both terms required
transformer OR attention       # Either term
-BERT                         # Exclude term
```

### Field-Specific Queries
```
au:Vaswani                    # Author search
ti:attention                  # Title search
abs:language model            # Abstract search
cat:cs.CL                     # Category search
```

### Combined Queries
```
au:Bengio AND ti:attention
cat:cs.LG AND ti:reinforcement learning
```

## Common Workflows

### Find and Download Key Papers
```javascript
// Step 1: Search
const results = search_papers({
  query: "GPT language model",
  sort_by: "relevance",
  max_results: 10
});

// Step 2: Download promising papers
download_paper({ arxiv_id: "2005.14165" }); // GPT-3

// Step 3: Read for analysis
read_paper({ arxiv_id: "2005.14165" });
```

### Track Recent Research
```javascript
search_papers({
  query: "large language models",
  categories: ["cs.CL", "cs.AI"],
  sort_by: "submitted_date",
  sort_order: "descending",
  max_results: 50
})
```

### Author Bibliography
```javascript
search_papers({
  query: "au:Hinton",
  sort_by: "submitted_date",
  max_results: 100
})
```

### Literature Review Pipeline
```javascript
// 1. Broad search
search_papers({ query: "federated learning privacy", max_results: 50 })

// 2. Download seminal papers
download_paper({ arxiv_id: "1602.05629" }) // Original FL paper

// 3. Read and analyze
read_paper({ arxiv_id: "1602.05629" })

// 4. Check local collection
list_papers()
```

## Deep Paper Analysis Prompt

The arxiv-mcp-server includes a built-in prompt for comprehensive paper analysis. Access via:

```javascript
// Use the deep-paper-analysis prompt after reading a paper
```

This prompt guides analysis of:
- Research problem and motivation
- Methodology and approach
- Key contributions
- Experimental results
- Limitations and future work
- Connections to related work

## Troubleshooting

### Paper Not Found
- Verify arXiv ID format (YYMM.NNNNN)
- Check paper exists: visit `https://arxiv.org/abs/{id}`
- Some papers may be withdrawn

### Search Returns No Results
- Broaden query terms
- Remove category filters
- Check for typos in author names

### Download Fails
- Check network connectivity
- Verify storage path is writable
- Try again (temporary arXiv issues)

### Read Returns Empty
- Ensure paper was downloaded first
- Some PDFs may have extraction issues
- Try re-downloading the paper
