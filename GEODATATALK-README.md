# GeoDataTalk CLI

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GDAL](https://img.shields.io/badge/GDAL-3.0+-green.svg)](https://gdal.org/)

## Chat with your geospatial data in plain English. Right from your terminal.

> A **natural language interface** for your **vector** and **raster** geospatial data. Powered by **GDAL/OGR** and **LLMs**. **Fast**, **local**, and **private**.

Skip complex GIS software and command-line syntax. Just ask **"How many buildings are in this dataset?"** or **"What's the elevation range?"**<br>
Get instant answers from your **local geospatial files**.

**Privacy First:** Your data never leaves your machine. Only schema/metadata is sent to LLM.
**Formats:** Shapefile, GeoJSON, GeoPackage, KML, GeoTIFF, and 80+ more via GDAL/OGR
**Performance:** Direct GDAL/OGR access for **instant results**.

**⭐ If you find this useful, please star the repo. It helps a lot!**

## Why GeoDataTalk?

**The Problem:** You have a geospatial file and a simple question. What do you do?
- Open QGIS? Slow startup, and you have to leave the terminal
- Use ogr2ogr or gdalinfo? Complex syntax and flags to remember
- Write Python with GeoPandas? Overkill for "how many features in this shapefile?"

**The Solution:** Just ask your question naturally.

```bash
gdtalk roads.shp
> How many road features are there?
> Show me the 5 longest roads
> What is the total length of all roads?

gdtalk elevation.tif
> What is the elevation range?
> What is the pixel size?
> What is the value at coordinates 12.5, 41.9?
```

## Features

- **Natural Language** - Ask questions in plain English, no complex GIS tools required
- **Interactive Mode** - Ask multiple questions without restarting the command
- **100% Local Processing** - Data never leaves your machine, only schema/metadata is sent to LLM
- **100% Offline Option** - Use local Ollama models for complete offline operation
- **Fast** - Direct GDAL/OGR access processes data instantly
- **Vector & Raster Support** - Query both vector features and raster pixels
- **100+ LLM Models** - Powered by [LiteLLM](https://docs.litellm.ai) - OpenAI, Anthropic, Google, Ollama (local), and more
- **80+ Geospatial Formats** - Supports all GDAL/OGR formats: Shapefile, GeoJSON, GeoPackage, KML, GeoTIFF, and more
- **Scriptable** - JSON output format for automation and pipelines
- **Simple Configuration** - Just set `LLM_MODEL` and API key environment variables
- **Transparent** - Use `--operation` to see generated operations

## Installation

```bash
pip install geodatatalk-cli
```

**Requirements:**
- Python 3.9+
- GDAL 3.0+ (system installation)
- Either an API key for cloud models (OpenAI, Anthropic, etc.) OR local Ollama for offline use

### Installing GDAL

**Ubuntu/Debian:**
```bash
sudo apt-get install gdal-bin libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
```

**macOS:**
```bash
brew install gdal
```

**Windows:**
Download from https://gdal.org/ or use OSGeo4W

## Quick Start

```bash
# Option 1: Use cloud models (OpenAI, Anthropic, Google, etc.)
export LLM_MODEL="gpt-4o"
export OPENAI_API_KEY="your-key-here"

# Option 2: Use local Ollama (100% offline, fully private, no API key needed!)
export LLM_MODEL="ollama/llama3.1"
# No API key needed - works completely offline!

# Start interactive mode - ask multiple questions about vector data
gdtalk roads.shp

# You'll get a prompt where you can ask questions naturally:
# > How many roads are there?
# > Show me roads with length > 1000
# > What is the average road length?

# Or analyze raster data
gdtalk elevation.tif
# > What is the elevation range?
# > What's the value at coordinates 12.5, 41.9?
# > Show me band statistics

# Or use single query mode for quick answers
gdtalk buildings.geojson -p "How many buildings are there?"
gdtalk parcels.shp -p "Show me the 10 largest parcels"
```

## Configuration

GeoDataTalk uses [LiteLLM](https://docs.litellm.ai) to support 100+ models from various providers through a unified interface.

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

**Ollama (100% Offline - fully private, no internet required!):**
```bash
# Install Ollama from https://ollama.ai
# Start Ollama: ollama serve
# Pull a model: ollama pull llama3.1

export LLM_MODEL="ollama/llama3.1"  # or ollama/mistral, ollama/codellama
# No API key needed! Works completely offline.
```

**Azure OpenAI:**
```bash
export LLM_MODEL="azure/gpt-4o"  # Use your deployment name
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"
export AZURE_API_VERSION="2024-02-01"
```

**And 100+ more models!** See [LiteLLM Providers](https://docs.litellm.ai/docs/providers) for the complete list.

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
gdtalk roads.shp
gdtalk elevation.tif
```

**Direct query** - single question and exit:
```bash
gdtalk buildings.geojson -p "How many buildings?"
# or using long form:
gdtalk parcels.shp --prompt "Show me parcels larger than 1000 sqm"
```

### Vector Data Examples

```bash
# Feature counts
gdtalk buildings.geojson -p "How many buildings?"
gdtalk roads.shp -p "Count the road features"

# Filtering & listing
gdtalk roads.shp -p "Show me roads with NAME like 'Main%'"
gdtalk buildings.geojson -p "List buildings with height > 50"

# Statistics
gdtalk parcels.shp -p "What is the average area?"
gdtalk roads.shp -p "Show statistics for the LENGTH field"

# Spatial queries
gdtalk points.geojson -p "Show features within bbox -122.5, 37.7, -122.3, 37.8"

# Supported vector formats:
# - Shapefile (.shp)
# - GeoJSON (.geojson, .json)
# - GeoPackage (.gpkg)
# - KML/KMZ (.kml, .kmz)
# - GML (.gml)
# - And many more...
```

### Raster Data Examples

```bash
# Dataset information
gdtalk elevation.tif -p "Describe this raster"
gdtalk landsat.tif -p "How many bands?"

# Statistics
gdtalk elevation.tif -p "What is the elevation range?"
gdtalk temperature.tif -p "Show band 1 statistics"

# Pixel values
gdtalk elevation.tif -p "What's the value at coordinates 12.5, 41.9?"
gdtalk landsat.tif -p "Get pixel value at 500000, 4500000 for band 3"

# Supported raster formats:
# - GeoTIFF (.tif, .tiff)
# - NetCDF (.nc)
# - HDF (.hdf, .h5)
# - ERDAS Imagine (.img)
# - And many more...
```

## Options

### Query Modes

```bash
# Interactive mode (default) - ask multiple questions
gdtalk roads.shp

# Non-interactive mode - single query and exit
gdtalk roads.shp -p "How many roads?"
gdtalk roads.shp --prompt "Show me the 5 longest roads"
```

### Output Formats (with `-p` only)

GeoDataTalk supports multiple output formats:

```bash
# Human-readable table (default)
gdtalk roads.shp -p "Show me 5 roads"

# JSON format - for scripting and automation
gdtalk roads.shp -p "Count roads" --json
# Output: {"operation": {...}, "result": {...}, "error": null}
```

### Debug & Display Options

```bash
# Show generated operation details along with results
gdtalk roads.shp -p "query" --operation

# Hide field/band details table when loading data
gdtalk roads.shp --no-schema

# Combine options
gdtalk roads.shp -p "query" --operation --no-schema
```

### Scripting

GeoDataTalk supports structured output formats for integration with scripts and pipelines:

```bash
# JSON output for scripting
COUNT=$(gdtalk roads.shp -p "count roads" --json | jq -r '.result.count')
echo "Total Roads: $COUNT"

# Process multiple files
for file in *.shp; do
  COUNT=$(gdtalk "$file" -p "count features" --json | jq -r '.result.count')
  echo "$file: $COUNT features"
done

# Check raster statistics
MIN=$(gdtalk elevation.tif -p "band 1 min value" --json | jq -r '.result.data.min')
MAX=$(gdtalk elevation.tif -p "band 1 max value" --json | jq -r '.result.data.max')
echo "Elevation range: $MIN to $MAX"

# Combine with other geospatial tools
gdtalk input.shp -p "features with area > 1000" --json | \
  jq '.result.features[]' | \
  ogr2ogr -f GeoJSON output.geojson /vsistdin/
```

## Supported Geospatial Formats

GeoDataTalk supports all formats that GDAL/OGR can read:

**Vector formats (80+):**
- Shapefile, GeoJSON, GeoPackage, KML/KMZ, GML, CSV with geometries
- PostGIS, SpatiaLite, Oracle Spatial, MySQL Spatial
- DXF, DWG, DGN, MapInfo, OpenStreetMap PBF
- And many more...

**Raster formats (140+):**
- GeoTIFF, NetCDF, HDF4/HDF5, ERDAS Imagine
- JPEG, PNG, BMP (with world files)
- GRIB, NITF, MrSID, ECW
- And many more...

See the full list at https://gdal.org/drivers/

## Exit Codes

GeoDataTalk returns standard exit codes for use in scripts and automation:

| Exit Code | Meaning | Example |
|-----------|---------|---------|
| `0` | Success | Query completed successfully |
| `1` | Runtime error | Missing API key, query failed, file not found |
| `2` | Invalid arguments | `--json` without `-p`, invalid option combination |

**Example usage in scripts:**
```bash
if gdtalk roads.shp -p "count roads" --json > result.json; then
    echo "Success!"
else
    echo "Failed with exit code $?"
fi
```

## FAQ

**Q: Can I use this completely offline?**
A: Yes! Use local Ollama models and GeoDataTalk works 100% offline with no internet connection required. Your data and queries never leave your machine.

**Q: Is my geospatial data sent to the LLM provider?**
A: With cloud models, only schema/metadata (field names, types, projection info) is sent - your actual feature data stays local. With local Ollama models, nothing leaves your machine at all.

**Q: What geospatial formats are supported?**
A: All formats supported by GDAL/OGR - 80+ vector formats (Shapefile, GeoJSON, GeoPackage, etc.) and 140+ raster formats (GeoTIFF, NetCDF, HDF, etc.).

**Q: How large datasets can I query?**
A: GDAL/OGR can handle very large files efficiently. For huge datasets, filtering and limiting results is recommended for performance.

**Q: Does this replace QGIS or ArcGIS?**
A: No, GeoDataTalk is designed for quick data exploration and simple queries from the command line. For complex spatial analysis and visualization, traditional GIS software is still recommended.

**Q: Can I do spatial operations like buffers, intersections, etc?**
A: Currently, GeoDataTalk focuses on data exploration (querying, filtering, statistics). Complex spatial operations are best done with dedicated GIS tools or libraries.

## Architecture

GeoDataTalk is built on top of:
- **GDAL/OGR** - Industry-standard geospatial data abstraction library
- **LiteLLM** - Unified interface to 100+ LLM providers
- **Rich** - Beautiful terminal output

The architecture is similar to DataTalk CLI but adapted for geospatial data:
1. Load geospatial data using GDAL/OGR
2. Extract schema/metadata (fields, projection, extent, etc.)
3. Use LLM to convert natural language to structured geospatial operations
4. Execute operations using GDAL/OGR APIs
5. Display results in human-readable format

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file.

Built with [GDAL/OGR](https://gdal.org/), [LiteLLM](https://docs.litellm.ai), and [Rich](https://rich.readthedocs.io/).

## Related Projects

- [DataTalk CLI](https://github.com/vtsaplin/datatalk-cli) - Natural language interface for CSV, Excel, and Parquet files
- [GDAL](https://gdal.org/) - Geospatial Data Abstraction Library
- [OGR](https://gdal.org/programs/ogr2ogr.html) - Vector data conversion utility
