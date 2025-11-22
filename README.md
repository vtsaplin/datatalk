# DataTalk CLI

[![PyPI version](https://badge.fury.io/py/datatalk-cli.svg)](https://badge.fury.io/py/datatalk-cli)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ask questions to your CSV, Excel & Parquet files in plain English right from your terminal.**

Stop writing SQL or memorizing command flags for quick data checks. Just ask your question naturally and get instant answers while keeping your data completely local and private.

![Demo](docs/demo.gif)

## Why DataTalk?

Working with data files in the terminal usually means choosing between:
- **GUI tools** (Excel) - slow for large files, breaks your workflow
- **CLI tools** (qsv, csvkit) - powerful but require memorizing many commands
- **SQL tools** (DuckDB) - need formal query syntax for simple questions

DataTalk gives you the best of both: natural language questions + local processing + terminal speed.

## Features

- **100% Local Processing** - Data never leaves your machine, only schema is sent to LLM
- **Natural Language** - Ask questions in plain English, no SQL required
- **Multiple Formats** - Supports CSV, Excel (.xlsx, .xls), and Parquet files
- **Transparent** - Use `--show-sql` to see generated queries

## Installation

```bash
pip install datatalk-cli
```

**Requirements:** Python 3.9+ and OpenAI or Azure OpenAI API key

## Quick Start

```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Query a file
dtalk sales_data.csv "What are the top 5 products by revenue?"
```

## Configuration

### OpenAI
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4o"  # Optional
```

### Azure OpenAI
```bash
export AZURE_DEPLOYMENT_TARGET_URL="https://your-resource.openai.azure.com/..."
export AZURE_OPENAI_API_KEY="your-api-key"
```

Or create a `.env` file, or run `dtalk` and follow the interactive setup.

**Commands:**
```bash
dtalk --config-info      # Show configuration
dtalk --reset-config     # Clear configuration
```

## Usage

**Interactive mode** - ask multiple questions:
```bash
dtalk sales_data.csv
```

**Direct query** - single question and exit:
```bash
dtalk sales_data.csv "What were total sales in Q4?"
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

## Advanced Options

```bash
dtalk data.csv "query" --show-sql       # Show generated SQL
dtalk data.csv "query" --show-tokens    # Show API token usage
dtalk data.csv --hide-schema            # Hide dataset schema
dtalk data.csv "query" --hide-data      # Hide query results
```

### Scripting

```bash
# Use in scripts
REPORT=$(dtalk sales.csv "yesterday's revenue" --hide-data)
echo "$REPORT" | mail -s "Report" team@company.com

# Process multiple files
for file in data_*.csv; do
  dtalk "$file" "row count"
done
```


## Development

```bash
git clone https://github.com/vtsaplin/datatalk-cli.git
cd datatalk-cli
uv run dtalk sample_data/sales_data.csv

# Run tests
uv sync
uv run python -m pytest

# Build package
python -m build
```

## FAQ

**Q: Is my data sent to OpenAI/Azure?**  
A: No. Only schema (column names and types) is sent. Your data stays local.

**Q: How much does it cost?**  
A: 200-500 tokens per query ($0.001-0.005 with GPT-4). Use `--show-tokens` to monitor.

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

Built with [DuckDB](https://duckdb.org/), [OpenAI API](https://openai.com/), and [Rich](https://rich.readthedocs.io/).
