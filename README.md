# DataTalk CLI

A command-line tool for querying CSV and Parquet files using natural language.

## Overview

DataTalk CLI uses LLMs to interpret natural language queries and converts them to data operations that run locally. This approach keeps your data private while providing accurate, deterministic results.

## How it works

1. Load CSV or Parquet files
2. Ask questions in natural language
3. AI interprets the query and generates appropriate data operations
4. Results are computed locally and returned

## Features

- **Local processing**: Data never leaves your machine
- **Accurate calculations**: No AI hallucinations in numerical results
- **Token efficient**: Only sends schema metadata to LLM
- **Multiple formats**: Supports CSV and Parquet files
- **No coding required**: Query data without pandas or SQL knowledge

## Installation

Install from GitHub:

```bash
pip install git+https://github.com/vtsaplin/datatalk.git@v0.1.16
```

Note: The package will be installed as `datatalk-cli` but the command remains `dtalk`.

Or clone and run locally:

```bash
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk
uv run dtalk --help
```

## Configuration

DataTalk CLI supports Azure OpenAI and OpenAI. Configure credentials using one of these methods:

### Interactive setup

Run without a config file and the tool will prompt for credentials and save them to `~/.config/datatalk/config.json`.

### Environment file

Create a `.env` file:

**Azure OpenAI:**

```bash
AZURE_DEPLOYMENT_TARGET_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview
AZURE_OPENAI_API_KEY=your-api-key-here
```

**OpenAI:**

```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
```

Check configuration: `dtalk --config-info`

## Usage

### Interactive mode

```bash
dtalk data.csv
```

### Direct queries

```bash
dtalk data.csv "your question here"
dtalk data.csv "What are the trends?"
dtalk data.csv "Show me the top categories"
```

## Development

Clone and run:

```bash
git clone https://github.com/vtsaplin/datatalk.git
cd datatalk
uv run dtalk --help
```

### Sample Data

Test with included sample files in interactive mode:

```bash
uv run dtalk sample_data/sales_data.csv
```

Run direct queries on sample data:

```bash
uv run dtalk sample_data/employees.csv -p "Show hiring patterns by year"
```

### Testing

```bash
uv sync --extra test
uv run pytest
```

### Release

```bash
./release.sh
```
