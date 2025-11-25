"""LLM provider for geospatial query generation using LiteLLM."""

import os
import re
import json
import litellm

# Suppress litellm debug messages
litellm.suppress_debug_info = True


class GeoLLMProvider:
    """LLM provider for converting natural language to geospatial queries."""

    def __init__(self, model: str):
        self.model = model

    def to_geo_operation(self, question: str, data_info: dict) -> dict:
        """Convert natural language question to geospatial operation."""
        data_type = data_info.get('data_type', 'unknown')

        if data_type == 'vector':
            return self._to_vector_operation(question, data_info)
        elif data_type == 'raster':
            return self._to_raster_operation(question, data_info)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    def _to_vector_operation(self, question: str, data_info: dict) -> dict:
        """Convert question to vector data operation."""
        # Prepare schema information
        fields_info = []
        for field in data_info.get('fields', []):
            samples_str = ', '.join([str(s) for s in field['samples'][:3]])
            fields_info.append(f"{field['name']} ({field['type']}) - samples: {samples_str}")

        schema_str = '\n'.join(fields_info)

        prompt = f"""You are a geospatial analyst assistant. Convert the user's question into a structured operation for vector geospatial data.

Dataset Information:
- Type: Vector ({data_info.get('geometry_type', 'Unknown')} geometry)
- Feature Count: {data_info.get('feature_count', 0):,}
- Projection: {data_info.get('projection', 'Unknown')} (EPSG:{data_info.get('epsg', 'Unknown')})
- Extent: {data_info.get('extent', {{}})}
- Fields:
{schema_str}

Your task is to analyze the question and return a JSON object with the operation details.

Available operations:
1. "list_features" - List features with optional filters
2. "count_features" - Count features
3. "filter_features" - Filter features by attributes
4. "spatial_filter" - Filter by bounding box
5. "statistics" - Calculate statistics on a field
6. "describe" - Describe the dataset

Return JSON in this format:
{{
  "operation": "operation_name",
  "sql": "OGR SQL query if needed (optional)",
  "limit": number (optional, default 10 for list operations),
  "field": "field_name for statistics (optional)",
  "bbox": [min_x, min_y, max_x, max_y] (optional, for spatial filter)
}}

CRITICAL RULES:
- Output ONLY valid JSON, nothing else
- No explanations, no markdown, no code blocks
- If unsure, use "describe" operation
- SQL should be valid OGR SQL syntax
- Use proper field names from the schema above

User question: {question}

JSON response:"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
                max_tokens=500,
            )
        except Exception as e:
            cleaned_message = self._clean_litellm_error(str(e))
            raise ValueError(cleaned_message) from None

        content = response.choices[0].message.content
        if content is None:
            raise ValueError(f"No content returned from {self.model}")

        return self._parse_json_response(content)

    def _to_raster_operation(self, question: str, data_info: dict) -> dict:
        """Convert question to raster data operation."""
        # Prepare bands information
        bands_info = []
        for band in data_info.get('bands', []):
            bands_info.append(
                f"Band {band['number']}: {band['data_type']}, "
                f"range: {band.get('min', 'N/A')} to {band.get('max', 'N/A')}, "
                f"interpretation: {band.get('color_interpretation', 'Unknown')}"
            )

        bands_str = '\n'.join(bands_info)

        prompt = f"""You are a geospatial analyst assistant. Convert the user's question into a structured operation for raster geospatial data.

Dataset Information:
- Type: Raster
- Dimensions: {data_info.get('width', 0)} x {data_info.get('height', 0)} pixels
- Bands: {data_info.get('band_count', 0)}
- Projection: {data_info.get('projection', 'Unknown')} (EPSG:{data_info.get('epsg', 'Unknown')})
- Pixel Size: {data_info.get('pixel_size', {{}}).get('x', 'N/A')} x {data_info.get('pixel_size', {{}}).get('y', 'N/A')}
- Extent: {data_info.get('extent', {{}})}
- Bands Details:
{bands_str}

Your task is to analyze the question and return a JSON object with the operation details.

Available operations:
1. "band_statistics" - Get statistics for a band
2. "pixel_value" - Get value at coordinates
3. "describe" - Describe the raster dataset
4. "metadata" - Show raster metadata

Return JSON in this format:
{{
  "operation": "operation_name",
  "band": band_number (optional, default 1),
  "x": x_coordinate (for pixel_value),
  "y": y_coordinate (for pixel_value)
}}

CRITICAL RULES:
- Output ONLY valid JSON, nothing else
- No explanations, no markdown, no code blocks
- If unsure, use "describe" operation
- Band numbers start at 1
- Coordinates should be in the dataset's projection system

User question: {question}

JSON response:"""

        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
                max_tokens=500,
            )
        except Exception as e:
            cleaned_message = self._clean_litellm_error(str(e))
            raise ValueError(cleaned_message) from None

        content = response.choices[0].message.content
        if content is None:
            raise ValueError(f"No content returned from {self.model}")

        return self._parse_json_response(content)

    def _parse_json_response(self, content: str) -> dict:
        """Parse and clean JSON response from LLM."""
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM: {e}") from None

    def _clean_litellm_error(self, error_message: str) -> str:
        """Clean up litellm error message for user-friendly display."""
        cleaned = error_message

        # Remove common technical prefixes
        prefixes_to_remove = [
            r"litellm\.\w+Error:\s*",
            r"\w+Error:\s*",
            r"\w+Exception\s*-\s*",
        ]

        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, "", cleaned, flags=re.IGNORECASE)

        cleaned = cleaned.strip()

        if not cleaned:
            cleaned = error_message

        return cleaned
