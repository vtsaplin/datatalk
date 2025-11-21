# DataTalk CLI

[![PyPI version](https://badge.fury.io/py/datatalk-cli.svg)](https://badge.fury.io/py/datatalk-cli)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ask questions to your CSV & Parquet files in plain English, right from your terminal.**

DataTalk CLI eliminates the need to remember complex command-line flags or write SQL for quick data checks. Just ask your question in natural language, and get instant answers—all while keeping your data 100% local and private.

![Demo](docs/demo.gif)

## Why DataTalk?

Working with data files on the command line has always involved a trade-off:

- **GUI tools** (Excel, Tableau) are slow for large files and force you to leave your terminal workflow
- **Powerful CLI tools** (qsv, xsv) require memorizing dozens of commands and flags
- **SQL-based tools** (csvcli, DuckDB CLI) demand writing formal queries for simple questions

DataTalk eliminates this friction. It's a **conversational data terminal** that lets you:

- Stay in your terminal workflow without context switching
- Express your intent directly in natural language
- Get accurate, deterministic results computed locally
- Query both CSV and Parquet files with the same interface

Perfect for developers, data engineers, and analysts who value speed and terminal efficiency.

## How It Works & Data Privacy

DataTalk is designed with a **privacy-first, local-first architecture**:

1. **Your data stays on your machine** - Files are loaded into a local DuckDB instance
2. **Only metadata is sent to the LLM** - The AI receives your question and the file schema (column names and types)
3. **AI generates SQL** - The LLM creates a SQL query based on your question
4. **Query runs locally** - DuckDB executes the query on your local data
5. **You see the results** - Clean, formatted output in your terminal

**What is sent to the LLM:**
- Your natural language question
- Column names and data types
- A few sample values for context (optional)

**What is NOT sent:**
- Your actual data rows
- Sensitive information
- Full file contents

This approach gives you the convenience of natural language while maintaining full control over your data privacy.

## Key Features

- **100% Local Processing** - Data never leaves your machine
- **Accurate Calculations** - No AI hallucinations; real SQL on real data
- **Token Efficient** - Only schema metadata sent to LLM, saving costs
- **Multiple Formats** - Seamless support for CSV and Parquet files
- **No Coding Required** - Query data without pandas or SQL knowledge
- **Transparent** - Optional `--show-sql` flag to see generated queries
- **Smart Suggestions** - Context-aware follow-up questions

## Installation

```bash
pip install datatalk-cli
```

That's it! The command-line tool `dtalk` will be available immediately.

**Requirements:**
- Python 3.9 or higher
- An OpenAI or Azure OpenAI API key

**Alternative Installation Methods:**

From GitHub (latest development version):
```bash
pip install git+https://github.com/vtsaplin/datatalk.git@main
```

For local development:
```bash
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk
uv run dtalk --help
```

## Quick Start

Get up and running in 60 seconds:

1. **Install DataTalk:**
   ```bash
   pip install datatalk-cli
   ```

2. **Set your API key:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Download sample data and try it:**
   ```bash
   curl -O https://raw.githubusercontent.com/vtsaplin/datatalk/main/sample_data/sales_data.csv
   dtalk sales_data.csv "What are the top 5 products by revenue?"
   ```

That's it! You just queried data using plain English.

## Configuration

DataTalk supports both **OpenAI** and **Azure OpenAI**. Choose your preferred method:

### Option 1: Environment Variables (Recommended)

**For OpenAI:**
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o"  # Optional, defaults to gpt-4o
```

**For Azure OpenAI:**
```bash
export AZURE_DEPLOYMENT_TARGET_URL="https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview"
export AZURE_OPENAI_API_KEY="your-api-key-here"
```

### Option 2: Configuration File

Create a `.env` file in your project directory with the same variables as above.

### Option 3: Interactive Setup

Simply run `dtalk` with a data file, and the tool will prompt you to enter your credentials. They'll be saved to `~/.config/datatalk/config.json` for future use.

### Configuration Management

```bash
dtalk --config-info      # Show current configuration
dtalk --reset-config     # Clear saved configuration
```

## Usage

DataTalk offers two modes: **interactive** for exploration and **direct query** for scripting.

### Interactive Mode

Launch an interactive session to ask multiple questions:

```bash
dtalk sales_data.csv
```

You'll see:
- Basic dataset statistics (row count, columns)
- AI-generated suggested questions
- An interactive prompt where you can ask anything

Type `quit`, `exit`, or press Ctrl+D to exit.

### Direct Query Mode

Run a single query and exit—perfect for scripts and automation:

```bash
dtalk sales_data.csv "What were total sales in Q4?"
```

### Examples: Basic Queries

Get started with these common questions:

**File Structure & Overview:**
```bash
dtalk employees.csv "How many rows are in this file?"
dtalk inventory.csv "Show me the column names and their data types"
dtalk customers.csv "Display the first 10 rows"
```

**Simple Statistics:**
```bash
dtalk sales_data.csv "What is the average order value?"
dtalk employees.csv "How many employees were hired each year?"
dtalk inventory.csv "Count the number of unique product categories"
```

### Examples: Filtering & Sorting

**Filtering Data:**
```bash
dtalk customers.csv "Show all customers from Canada"
dtalk sales_data.csv "List orders over $1000 from the last month"
dtalk employees.csv "Find all engineers in the San Francisco office"
```

**Sorting & Top N:**
```bash
dtalk sales_data.csv "Top 10 customers by total purchase amount"
dtalk inventory.csv "Show the 5 most expensive products, descending"
dtalk employees.csv "List employees by hire date, newest first"
```

### Examples: Aggregations & Analysis

**Grouping & Aggregation:**
```bash
dtalk sales_data.csv "Total revenue by product category"
dtalk customers.csv "Count customers by country and city"
dtalk employees.csv "Average salary by department and job title"
```

**Time-Series Analysis:**
```bash
dtalk sales_data.csv "Monthly revenue trend for 2024"
dtalk orders.csv "Compare sales between Q3 and Q4"
dtalk events.csv "Daily active users for the past week"
```

**Multi-Column Analysis:**
```bash
dtalk sales_data.csv "Which region has the highest average order value?"
dtalk employees.csv "Show department with the most growth in the last year"
dtalk inventory.csv "What's the profit margin by category and supplier?"
```

### Examples: Working with Different Formats

DataTalk seamlessly handles both CSV and Parquet files:

```bash
# CSV files
dtalk data.csv "your question"

# Parquet files (same syntax!)
dtalk data.parquet "your question"

# Large Parquet files are fast
dtalk large_dataset.parquet "Count distinct users"
```

## Advanced Features

### See the Generated SQL

Want to learn SQL or verify the query? Use the `--show-sql` flag:

```bash
dtalk sales_data.csv "Top 5 products by revenue" --show-sql
```

Output will include:
```
SQL: SELECT product_name, SUM(revenue) as total_revenue 
     FROM events GROUP BY product_name 
     ORDER BY total_revenue DESC LIMIT 5
```

This is perfect for:
- Learning SQL patterns
- Debugging unexpected results
- Auditing what queries are generated
- Reusing queries in other tools

### Track Token Usage

Monitor your API costs with `--show-tokens`:

```bash
dtalk data.csv "your question" --show-tokens
```

Displays:
- Number of API requests made
- Input tokens used
- Output tokens used
- Total tokens consumed

### Control Output Visibility

Fine-tune what information is displayed:

```bash
# Hide detailed dataset schema
dtalk data.csv --hide-schema

# Hide raw query results (useful when scripting)
dtalk data.csv "query" --hide-data

# Hide AI-generated question suggestions
dtalk data.csv --hide-suggestions
```

### Scripting & Automation

DataTalk works great in shell scripts and pipelines:

```bash
#!/bin/bash
# Daily sales report script

REPORT=$(dtalk sales.csv "What was yesterday's total revenue?" --hide-data -q)
echo "Daily Sales Report: $REPORT"

# Email or post to Slack
echo "$REPORT" | mail -s "Daily Sales" team@company.com
```

Combine with other Unix tools:

```bash
# Run queries on multiple files
for file in data_*.csv; do
  echo "Analyzing $file..."
  dtalk "$file" "row count"
done

# Chain with grep to filter results
dtalk sales.csv "show all orders" | grep "Canada"
```

## Use Cases

DataTalk shines in these scenarios:

**Quick Data Checks**
- "How many rows are in this file?" before loading it into a database
- "What's the date range of this dataset?" for validation
- "Show me sample rows" to verify data format

**Ad-Hoc Analysis**
- Exploring unfamiliar datasets without writing code
- Quick statistics during incident response
- Spot-checking data exports from other systems

**Data Engineering Workflows**
- Validating ETL outputs
- Checking data quality after transformations
- Quick profiling of incoming data files

**Learning & Documentation**
- Using `--show-sql` to learn SQL patterns
- Documenting common queries in natural language
- Creating repeatable analysis commands for team members

## Comparison with Other Tools

| Tool | Interface | Query Method | Best For | DataTalk Advantage |
|------|-----------|--------------|----------|-------------------|
| **DataTalk** | CLI | Natural Language | Terminal users who value speed | Zero cognitive overhead; just ask |
| **qsv** | CLI | Commands/Flags | High-performance data wrangling | Easier for ad-hoc questions; no flags to remember |
| **csvcli** | CLI | SQL | Analysts who know SQL | Natural language for those who don't know SQL |
| **DuckDB CLI** | CLI | SQL | Complex analytical queries | Simpler for quick questions |
| **pandas** | Python | Code | Programmers, complex analysis | No coding required; instant results |
| **Excel** | GUI | Point & click | Non-technical users | Works with huge files; stays in terminal |

**When to use DataTalk vs. alternatives:**
- Use **DataTalk** for quick, explorative questions in your terminal workflow
- Use **qsv/DuckDB** for complex transformations or when you need maximum performance
- Use **pandas** when you need programmatic control or complex custom logic
- Use **Excel/Tableau** for visualization and interactive dashboards

## Roadmap

Planned features and improvements:

**Local LLM Support** (High Priority)
- Integration with Ollama for 100% offline, private querying
- Zero API costs for sensitive data analysis

**Query Transparency**
- `--dry-run` mode to see generated query without execution
- Query history and replay functionality

**Enhanced Output**
- `--output json|csv|markdown` for better scriptability
- Basic visualization generation ("plot sales by month")

**Advanced Capabilities**
- Multi-file queries ("compare revenue between sales_2023.csv and sales_2024.csv")
- Saved query templates for common patterns
- Integration with other CLI tools via pipes

## Development

Clone and run locally:

```bash
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk
uv run dtalk --help
```

### Testing with Sample Data

Test with included sample files in interactive mode:

```bash
uv run dtalk sample_data/sales_data.csv
uv run dtalk sample_data/employees.csv
uv run dtalk sample_data/inventory.csv
```

Run direct queries:

```bash
uv run dtalk sample_data/employees.csv -p "Show hiring patterns by year"
uv run dtalk sample_data/sales_data.csv -p "What are the top categories?" --show-sql
```

### Running Tests

```bash
uv sync --extra test
uv run pytest
```

### Building & Releasing

Generate demo recording:
```bash
vhs demo.tape
```

Build package:
```bash
python -m build
```

Release (maintainers only):
```bash
./release.sh
```

## FAQ

**Q: Is my data sent to OpenAI/Azure?**  
A: No. Only the schema (column names and types) and your question are sent. Your actual data rows stay completely local.

**Q: How much does it cost to use?**  
A: You need an OpenAI or Azure OpenAI API key. Each query typically uses 200-500 tokens (~$0.001-0.005 per query with GPT-4). Use `--show-tokens` to monitor usage.

**Q: Can I use this offline or with local LLMs?**  
A: Local LLM support (via Ollama) is on our roadmap and will be released soon. This will enable 100% offline, private querying.

**Q: What's the difference between DataTalk and pandas-ai?**  
A: pandas-ai is a Python library for use in code/notebooks. DataTalk is a standalone CLI tool for terminal users who want instant results without writing code.

**Q: Does this work with databases like PostgreSQL or MySQL?**  
A: Currently, DataTalk only supports CSV and Parquet files. Database support may be added in future versions.

**Q: Can I see what SQL queries are being generated?**  
A: Yes! Use the `--show-sql` flag to see the exact SQL query generated by the LLM before it executes.

**Q: How large of files can I query?**  
A: DataTalk uses DuckDB under the hood, which efficiently handles multi-gigabyte files. Parquet files are particularly fast. The limiting factor is your local disk space and RAM.

**Q: Can I use this in production scripts?**  
A: Yes! Use direct query mode (`dtalk file.csv "query" --hide-data`) in scripts. However, be aware of API rate limits and costs for high-frequency usage.

## Troubleshooting

**Problem: "Command not found: dtalk"**  
Solution: Make sure you've installed the package (`pip install datatalk-cli`) and that your Python scripts directory is in your PATH.

**Problem: "No API key found"**  
Solution: Set your API key with `export OPENAI_API_KEY="your-key"` or run `dtalk --config-info` to check your configuration.

**Problem: "Query returns unexpected results"**  
Solution: Use `--show-sql` to see the generated query. The LLM might be interpreting your question differently than expected. Try rephrasing your question more explicitly.

**Problem: "File format not supported"**  
Solution: DataTalk currently supports only `.csv` and `.parquet` files. For Excel files, export to CSV first, or try `csvcli` which supports Excel natively.

**Problem: "Queries are slow"**  
Solution: 
- Large files: Parquet format is faster than CSV for big datasets
- API latency: Most time is spent waiting for the LLM response (1-3 seconds)
- Complex queries: Consider breaking them into smaller questions

**Problem: "Rate limit exceeded"**  
Solution: You've hit your OpenAI API rate limit. Wait a few moments or upgrade your API plan.

## Contributing

Contributions are welcome! Here's how you can help:

**Report Bugs**  
Open an issue on GitHub with:
- The command you ran
- Expected vs. actual behavior
- Your Python version and OS

**Suggest Features**  
Check the [Roadmap](#roadmap) section first, then open an issue describing:
- The use case
- How it would work
- Why it's valuable

**Submit Pull Requests**  
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`uv run pytest`)
5. Submit a PR with a clear description

**Areas Where We'd Love Help:**
- Local LLM integration (Ollama, llama.cpp)
- Additional output formats (JSON, CSV, Markdown)
- Performance optimizations
- Documentation improvements
- Additional example queries

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [DuckDB](https://duckdb.org/) - Fast in-process analytical database
- [OpenAI API](https://openai.com/) - Natural language understanding
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Pandas](https://pandas.pydata.org/) - Data manipulation

Inspired by the growing ecosystem of AI-powered developer tools and the enduring power of the command line.

## Support

- [Documentation](https://github.com/vtsaplin/datatalk)
- [Issue Tracker](https://github.com/vtsaplin/datatalk/issues)
- [Discussions](https://github.com/vtsaplin/datatalk/discussions)
- Star this repo if you find it useful!

---

**Made for terminal users who love data**
