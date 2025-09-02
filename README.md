# Datatalk

> Query CSV and Parquet data with natural language.

## The Problem

Large Language Models are incredibly powerful at understanding natural language, but they're terrible at crunching numbers. When you ask an LLM to analyze data, it often hallucinates statistics, makes calculation errors, or gets overwhelmed by large datasets. You end up with unreliable results and burning through expensive tokens.

## How It Works

Datatalk solves these problems by combining the best of both worlds: AI's natural language understanding with local computation's precision and efficiency. Instead of asking an LLM to crunch numbers, Datatalk uses AI only to interpret your questions while doing all calculations locally on your machine.

The tool works by:

1. **Loading your data** - Supports both CSV and Parquet formats
2. **Understanding your question** - Uses AI to interpret natural language queries
3. **Analyzing the data** - Automatically processes your data to find the answers
4. **Returning results** - Provides clear, formatted answers with the underlying data

Whether you're analyzing marketing campaigns, exploring user behavior, or investigating trends, Datatalk lets you focus on asking the right questions rather than figuring out how to code the answers.

## Why Choose Datatalk

**Privacy & Data Security**: Your raw data never leaves your machine. Only column names and data types are shared with the AI to understand your query structure.

**Deterministic Calculations**: Unlike direct LLM analysis, numerical computations produce consistent, reproducible results. This eliminates the common problem of AI hallucinating statistics or making arithmetic errors when working with data.

**Token Efficiency**: Large datasets can quickly exhaust LLM token limits and become expensive to process. Datatalk sends only schema metadata and query context to the AI, allowing you to analyze gigabyte-sized files for the cost of a few hundred tokens rather than thousands.

**No Code Required**: Traditional data analysis requires knowledge of pandas, SQL, or similar tools. Datatalk translates natural language questions into the appropriate data operations, making exploratory data analysis accessible without programming expertise.

**Multiple Format Support**: Works with both CSV and Parquet files out of the box. Parquet support is particularly useful for large datasets as it provides better compression and faster read times compared to CSV.

## Getting Started

### Installation

You can install Datatalk directly from GitHub:

```bash
pip install git+https://github.com/vtsaplin/datatalk.git@v0.1.14
```

### From Source

```bash
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk
uv run datatalk --help
```

## Setting Up Your Environment

Datatalk requires Azure OpenAI credentials. You can configure them in two ways:

### Option 1: Interactive Configuration (Recommended)

If no `.env` file is found, the tool will prompt you for the two required values and save them to `~/.config/datatalk/config.json`.

### Option 2: Environment File

Create a `.env` file with just these two lines:

```bash
AZURE_DEPLOYMENT_TARGET_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview
AZURE_OPENAI_API_KEY=your-api-key-here
```

**That's it!** The tool automatically extracts the endpoint, deployment name, and API version from the target URL.

To view your current configuration:

```bash
datatalk --config-info
```

## Usage

### Interactive Mode
```bash
# Analyze your data interactively
datatalk data.csv
```

### Direct Query Mode
```bash
# Ask a specific question directly
datatalk data.csv "your question here"

# Examples with placeholders
datatalk data.csv "What are the trends?"
datatalk data.csv "Show me the top categories"
datatalk data.csv "Which items need attention?"
```

## Development

### Development Installation

```bash
# Clone the repository
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk

# Run directly
uv run datatalk --help
```

### Examples with Sample Data

This repository includes sample CSV files in the `sample_data/` folder for testing:

```bash
# Interactive mode with sample data
uv run datatalk sample_data/sales_data.csv
uv run datatalk sample_data/employees.csv

# Direct queries with sample data
uv run datatalk sample_data/employees.csv "Show hiring patterns by year"
uv run datatalk sample_data/inventory.csv "Which products are running low?"
uv run datatalk sample_data/customers.csv "What are the top customer segments?"
```

### Testing

Install test dependencies:

```bash
uv sync --extra test
```

Run all tests:

```bash
uv run pytest
```

### Release

To publish a new version:

```bash
./release.sh
```
