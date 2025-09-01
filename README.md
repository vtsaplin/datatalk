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

### PyPI Installation

```bash
# Using pip
pip install datatalk-cli

# Using uv  
uv add datatalk-cli
```

### Homebrew Installation

```bash
# Will be available when Homebrew tap is created
# brew tap vtsaplin/tools
# brew install datatalk-cli
```

### From Source

```bash
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk
uv run datatalk-cli --help
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
```bash
datatalk-cli --config-info
```

## Usage Examples

### Interactive Mode
```bash
# Analyze sales data interactively
datatalk-cli sample_data/sales_data.csv

# During development
uv run datatalk-cli sample_data/sales_data.csv
```

### Direct Query Mode
```bash
# Ask a specific question directly
datatalk-cli sample_data/employees.csv "Show hiring patterns by year"

# During development  
uv run datatalk-cli sample_data/employees.csv "Show hiring patterns by year"
```

### More Examples
```bash
# Inventory analysis
datatalk-cli sample_data/inventory.csv "Which products are running low?"

# Customer insights
datatalk-cli sample_data/customers.csv "What are the top customer segments?"

# Analyze customer data interactively
datatalk-cli sample_data/customers.csv
```
```

## Usage Examples with Sample Data

This repository includes sample CSV files in the `sample_data/` folder to help you get started quickly:

```bash
# Analyze sales data interactively
uv run datatalk sample_data/sales_data.csv
```

```bash
# Analyze employee data interactively
uv run datatalk sample_data/employees.csv
```

```bash
# Analyze inventory data interactively
uv run datatalk sample_data/inventory.csv
```

```bash
# Analyze customer data interactively
uv run datatalk sample_data/customers.csv
```

## Development

### Development Installation

```bash
# Clone the repository
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk

# Run directly
uv run datatalk-cli --help
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

### Releasing

This project includes automated release scripts for publishing to multiple platforms. See [RELEASE.md](./RELEASE.md) for complete documentation.

**Quick release commands:**
```bash
# Complete release to all platforms
./release_all.sh 0.1.3

# Individual platform releases  
./release_github.sh 0.1.3    # GitHub only
./release_pypi.sh 0.1.3      # PyPI only
./release_homebrew.sh 0.1.3  # Homebrew only

# Test on TestPyPI first
./release_pypi.sh 0.1.3 --test
```

**Available release scripts:**
- `release_all.sh` - Master script for complete releases
- `release_github.sh` - GitHub releases and tags
- `release_pypi.sh` - PyPI package publishing  
- `release_homebrew.sh` - Homebrew formula updates

For detailed setup instructions and troubleshooting, see:
- [RELEASE.md](./RELEASE.md) - Complete release process documentation
- [PYPI_SETUP.md](./PYPI_SETUP.md) - PyPI configuration details
- [HOMEBREW_SETUP.md](./HOMEBREW_SETUP.md) - Homebrew tap setup
