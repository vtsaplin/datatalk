# Datatalk

```text
██████   █████  ████████  █████  ████████  █████  ██      ██   ██ 
██   ██ ██   ██    ██    ██   ██    ██    ██   ██ ██      ██  ██  
██   ██ ███████    ██    ███████    ██    ███████ ██      █████   
██   ██ ██   ██    ██    ██   ██    ██    ██   ██ ██      ██  ██  
██████  ██   ██    ██    ██   ██    ██    ██   ██ ███████ ██   ██ 
```

Query CSV and Parquet data with natural language.

## The Idea

Datatalk bridges the gap between data analysis and everyday language. Instead of writing complex SQL queries or learning pandas syntax, you simply ask questions in plain English about your data files.

The tool works by:

1. **Loading your data** - Supports both CSV and Parquet formats
2. **Understanding your question** - Uses AI to interpret natural language queries
3. **Analyzing the data** - Automatically processes your data to find the answers
4. **Returning results** - Provides clear, formatted answers with the underlying data

Whether you're analyzing marketing campaigns, exploring user behavior, or investigating trends, Datatalk lets you focus on asking the right questions rather than figuring out how to code the answers.

## Configuration

Datatalk requires Azure OpenAI credentials. You can configure them in two ways:

### Option 1: Environment File (Recommended)

Create a `.env` file with just these two lines:

```bash
AZURE_DEPLOYMENT_TARGET_URL=https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview
AZURE_OPENAI_API_KEY=your-api-key-here
```

**That's it!** The tool automatically extracts the endpoint, deployment name, and API version from the target URL.

### Option 2: Interactive Configuration

If no `.env` file is found, the tool will prompt you for the two required values and save them to `~/.config/datatalk/config.json`.

To view your current configuration:

```bash
datatalk --config-info
```

## Usage

```bash
uv run datatalk sample_data.csv
```

Or with Parquet files:

```bash
uv run datatalk sample_data.parquet
```

## Common Marketing Queries

Campaign performance:

```bash
uv run datatalk sample_data.csv --prompt "Which campaigns have the highest click-through rates?"
```

Device analysis:

```bash
uv run datatalk sample_data.csv --prompt "Compare mobile vs desktop performance"
```

Traffic quality:

```bash
uv run datatalk sample_data.csv --prompt "Show top 10 URLs by total pageviews"
```

Bounce rate insights:

```bash
uv run datatalk sample_data.csv --prompt "Show campaigns with bounce rates under 50% and their actual rates"
```

Click efficiency:

```bash
uv run datatalk sample_data.csv --prompt "Find URLs with highest clicks per session"
```

Regional performance:

```bash
uv run datatalk sample_data.csv --prompt "Compare performance by country based on URL patterns"
```

> **Note:** All examples above work with both CSV and Parquet files. Simply replace `sample_data.csv` with `sample_data.parquet` or any other supported file.
