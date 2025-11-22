# DataTalk CLI

[![PyPI version](https://badge.fury.io/py/datatalk-cli.svg)](https://badge.fury.io/py/datatalk-cli)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Chat with your data files in plain English. Right from your terminal.**

No SQL. No command flags. Just ask "What are the top 5 products?" and get instant answers. All processing happens locally, your data never leaves your machine.

![Demo](docs/demo.gif)

## Why DataTalk?

**The Problem:** You have a CSV file and a simple question. What do you do?
- Open Excel? Slow for large files, and you have to leave the terminal
- Use command-line tools (awk, csvkit)? Need to remember complex flags and syntax
- Write SQL? Overkill for "show me the top 5 products"

**The Solution:** Just ask your question naturally.

```bash
dtalk sales.csv
> What are the top 5 products by revenue?
> Show me sales by region for Q4
> Which customers made orders over $1000?
```

**The Best of All Worlds:**
- 🗣️ **Natural language** - no SQL or command flags to memorize
- 💬 **Interactive** - ask follow-up questions conversationally
- ⚡ **Fast** - DuckDB processes gigabytes locally in seconds
- 🔒 **Private** - your data never leaves your machine
- 🤖 **Scriptable** - JSON/CSV output for automation
- 🌐 **Flexible** - use any LLM provider or fully local models (Ollama)

## Features

- **100% Local Processing** - Data never leaves your machine, only schema is sent to LLM
- **100+ LLM Models** - Powered by [LiteLLM](https://docs.litellm.ai) - OpenAI, Anthropic, Google, Ollama (local), and more
- **Natural Language** - Ask questions in plain English, no SQL required
- **Multiple File Formats** - Supports CSV, Excel (.xlsx, .xls), and Parquet files
- **Scriptable** - JSON and CSV output formats for automation and pipelines
- **Simple Configuration** - Just set `LLM_MODEL` and API key environment variables
- **Transparent** - Use `--sql` to see generated queries

## Installation

```bash
pip install datatalk-cli
```

**Requirements:** Python 3.9+ and API key for a supported LLM provider (or local Ollama)

## Quick Start

```bash
# Set your model and API key
export LLM_MODEL="gpt-4o"
export OPENAI_API_KEY="your-key-here"

# Start interactive mode - ask multiple questions
dtalk sales_data.csv

# You'll get a prompt where you can ask questions naturally:
# > What are the top 5 products by revenue?
# > Show me monthly sales trends
# > Which customers made purchases over $1000?

# Or use single query mode for quick answers
dtalk sales_data.csv -p "What are the top 5 products by revenue?"

# Or use local Ollama (fully private, no API key needed!)
export LLM_MODEL="ollama/llama3.1"
dtalk sales_data.csv  # Interactive mode works with any model
```

## Configuration

DataTalk uses [LiteLLM](https://docs.litellm.ai) to support 100+ models from various providers through a unified interface.

### Required Environment Variables

Set two environment variables:

```bash
# 1. Choose your model
export LLM_MODEL="gpt-4o"

# 2. Set the API key for your provider
export OPENAI_API_KEY="your-key"
```

### Supported Models

**OpenAI:**
```bash
export LLM_MODEL="gpt-4o"  # or gpt-4o-mini, gpt-3.5-turbo
export OPENAI_API_KEY="sk-..."
```

**Anthropic Claude:**
```bash
export LLM_MODEL="claude-3-5-sonnet-20241022"
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Google Gemini:**
```bash
export LLM_MODEL="gemini-1.5-flash"  # or gemini-1.5-pro
export GEMINI_API_KEY="..."
```

**Ollama (Local - fully private!):**
```bash
# Start Ollama: ollama serve
# Pull a model: ollama pull llama3.1

export LLM_MODEL="ollama/llama3.1"  # or ollama/mistral, ollama/codellama
# No API key needed for local models!
```

**Azure OpenAI:**
```bash
export LLM_MODEL="azure/gpt-4o"  # Use your deployment name
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"
export AZURE_API_VERSION="2024-02-01"
```
*Note: Replace `gpt-4o` with your actual Azure deployment name*

**And 100+ more models!** See [LiteLLM Providers](https://docs.litellm.ai/docs/providers) for the complete list including Cohere, Replicate, Hugging Face, AWS Bedrock, and more.

### Optional Configuration

**MODEL_TEMPERATURE** - Control LLM response randomness (default: 0.1)
```bash
export MODEL_TEMPERATURE="0.5"  # Range: 0.0-2.0. Lower = more deterministic, Higher = more creative
```

### Using .env file

Create a `.env` file in your project directory:

```bash
LLM_MODEL=gpt-4o
OPENAI_API_KEY=your-key
```

## Usage

**Interactive mode** - ask multiple questions:
```bash
dtalk sales_data.csv
```

**Direct query** - single question and exit:
```bash
dtalk sales_data.csv -p "What were total sales in Q4?"
# or using long form:
dtalk sales_data.csv --prompt "What were total sales in Q4?"
```

### Examples

```bash
# Basic queries
dtalk data.csv "How many rows?"
dtalk data.csv "Show first 10 rows"
dtalk data.csv "What is the average order value?"

# Filtering & sorting
dtalk data.csv "Show customers from Canada"
dtalk data.csv "Top 10 products by revenue"

# Aggregations
dtalk data.csv "Total revenue by category"
dtalk data.csv "Monthly revenue trend for 2024"

# Excel files work the same way
dtalk report.xlsx "What is the average salary?"
dtalk budget.xls "Show expenses by department"

# Parquet files work the same way
dtalk data.parquet "Count distinct users"
```

## Options

### Query Modes

```bash
# Interactive mode (default) - ask multiple questions
dtalk data.csv

# Non-interactive mode - single query and exit
dtalk data.csv -p "What are the top 5 products?"
dtalk data.csv --prompt "What are the top 5 products?"
```

### Output Formats (with `-p` only)

DataTalk supports multiple output formats for different use cases:

```bash
# Human-readable table (default)
dtalk data.csv -p "Top 5 products"

# JSON format - for scripting and automation
dtalk data.csv -p "Top 5 products" --json
# Output: {"sql": "SELECT ...", "data": [...], "error": null}

# CSV format - for export and further processing
dtalk data.csv -p "Top 5 products" --csv
# Output: product_name,revenue
#         Apple,1000
#         Orange,500
```

### Debug & Display Options

```bash
# Show generated SQL along with results
dtalk data.csv -p "query" -s
dtalk data.csv -p "query" --sql

# Show only SQL without executing (for debugging/validation)
dtalk data.csv -p "query" --sql-only

# Hide column details table when loading data
dtalk data.csv --no-schema

# Combine options
dtalk data.csv -p "query" -s --no-schema    # Show SQL, hide schema
```

### Scripting

DataTalk supports structured output formats for integration with scripts and pipelines:

```bash
# JSON output for scripting
REVENUE=$(dtalk sales.csv -p "total revenue" --json | jq -r '.data[0].total_revenue')
echo "Total Revenue: $REVENUE"

# CSV output for further processing
dtalk sales.csv -p "sales by region" --csv | \
  awk -F',' '{sum+=$2} END {print "Grand Total:", sum}'

# Process multiple files
for file in data_*.csv; do
  COUNT=$(dtalk "$file" -p "row count" --json | jq -r '.data[0].count')
  echo "$file: $COUNT rows"
done

# Generate SQL for external tools
SQL=$(dtalk sales.csv -p "top 10 products" --sql-only)
echo "$SQL" | duckdb production.db

# Export filtered data
dtalk sales.csv -p "sales from Q4 2024" --csv > q4_sales.csv

# Combine with other tools
dtalk sales.csv -p "top products" --json | \
  jq '.data[] | select(.revenue > 1000)'
```


## Development

```bash
git clone https://github.com/vtsaplin/datatalk-cli.git
cd datatalk-cli

# Install dependencies (first time setup)
uv sync

# Option 1: Run from source (recommended, no installation needed)
uv run python -m datatalk.main sample_data/sales_data.csv

# Option 2: Install in editable mode (changes reflected immediately)
uv pip install -e .
dtalk sample_data/sales_data.csv

# Uninstall editable install (if needed)
uv pip uninstall datatalk-cli

# Run tests
uv run python -m pytest

# Build package
python -m build
```

## Exit Codes

DataTalk returns standard exit codes for use in scripts and automation:

| Exit Code | Meaning | Example |
|-----------|---------|---------|
| `0` | Success | Query completed successfully |
| `1` | Runtime error | Missing API key, query failed, file not found |
| `2` | Invalid arguments | `--json` without `-p`, invalid option combination |

**Example usage in scripts:**
```bash
if dtalk sales.csv -p "total revenue" --json > result.json; then
    echo "Success!"
else
    echo "Failed with exit code $?"
fi
```

## FAQ

**Q: Is my data sent to the LLM provider?**  
A: No. Only schema (column names and types) is sent. Your data stays local.

**Q: What file formats are supported?**  
A: CSV, Excel (.xlsx, .xls), and Parquet files.

**Q: How large files can I query?**  
A: DuckDB handles multi-gigabyte files. Parquet is faster for large datasets.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests (`uv run python -m pytest`)
4. Submit a PR

[Issue Tracker](https://github.com/vtsaplin/datatalk-cli/issues) | [Discussions](https://github.com/vtsaplin/datatalk-cli/discussions)

## License

MIT License - see [LICENSE](LICENSE) file.

Built with [DuckDB](https://duckdb.org/), [LiteLLM](https://docs.litellm.ai), and [Rich](https://rich.readthedocs.io/).
