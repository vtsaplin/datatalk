"""Core geospatial query processing logic."""

from typing import Any, Dict, List, Optional

from geodatatalk.geodatabase import GeoDataSource
from geodatatalk.geollm import GeoLLMProvider
from geodatatalk.geoprinter import GeoPrinter


def process_query(
    provider: GeoLLMProvider,
    question: str,
    geo_source: GeoDataSource,
    data_info: dict,
    printer: GeoPrinter,
) -> Dict[str, Any]:
    """Process a natural language query about geospatial data."""
    try:
        printer.decorative("[dim]Analyzing your question...[/dim]")
        operation = provider.to_geo_operation(question, data_info)

        printer.decorative("[dim]Executing geospatial operation...[/dim]")

        if data_info['data_type'] == 'vector':
            result = _execute_vector_operation(geo_source, operation, data_info)
        else:
            result = _execute_raster_operation(geo_source, operation, data_info)

        return {
            "operation": operation,
            "result": result,
            "error": None,
        }
    except Exception as e:
        return {
            "operation": None,
            "result": None,
            "error": str(e),
        }


def _execute_vector_operation(
    geo_source: GeoDataSource,
    operation: dict,
    data_info: dict
) -> Dict[str, Any]:
    """Execute vector data operation."""
    op_type = operation.get('operation', 'describe')

    if op_type == 'describe':
        return {
            'type': 'description',
            'data': data_info
        }

    elif op_type == 'list_features':
        limit = operation.get('limit', 10)
        sql = operation.get('sql')
        bbox = operation.get('bbox')

        features = geo_source.query_features(sql=sql, bbox=bbox, limit=limit)

        return {
            'type': 'features',
            'count': len(features),
            'features': features,
            'total': data_info.get('feature_count', 0)
        }

    elif op_type == 'count_features':
        sql = operation.get('sql')
        bbox = operation.get('bbox')

        features = geo_source.query_features(sql=sql, bbox=bbox)

        return {
            'type': 'count',
            'count': len(features),
            'total': data_info.get('feature_count', 0)
        }

    elif op_type == 'filter_features':
        sql = operation.get('sql')
        limit = operation.get('limit', 10)
        bbox = operation.get('bbox')

        features = geo_source.query_features(sql=sql, bbox=bbox, limit=limit)

        return {
            'type': 'features',
            'count': len(features),
            'features': features,
            'filter': sql or 'spatial filter'
        }

    elif op_type == 'spatial_filter':
        bbox = operation.get('bbox')
        if not bbox:
            raise ValueError("Bounding box required for spatial filter")

        limit = operation.get('limit', 10)
        features = geo_source.query_features(bbox=bbox, limit=limit)

        return {
            'type': 'features',
            'count': len(features),
            'features': features,
            'bbox': bbox
        }

    elif op_type == 'statistics':
        field = operation.get('field')
        if not field:
            raise ValueError("Field name required for statistics")

        sql = operation.get('sql')
        features = geo_source.query_features(sql=sql)

        # Calculate basic statistics
        values = []
        for feature in features:
            value = feature.get(field)
            if value is not None and isinstance(value, (int, float)):
                values.append(value)

        if not values:
            return {
                'type': 'statistics',
                'field': field,
                'error': 'No numeric values found'
            }

        values.sort()
        n = len(values)
        stats = {
            'field': field,
            'count': n,
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / n,
            'median': values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2
        }

        return {
            'type': 'statistics',
            'data': stats
        }

    else:
        raise ValueError(f"Unknown vector operation: {op_type}")


def _execute_raster_operation(
    geo_source: GeoDataSource,
    operation: dict,
    data_info: dict
) -> Dict[str, Any]:
    """Execute raster data operation."""
    op_type = operation.get('operation', 'describe')

    if op_type == 'describe':
        return {
            'type': 'description',
            'data': data_info
        }

    elif op_type == 'metadata':
        return {
            'type': 'metadata',
            'data': data_info
        }

    elif op_type == 'band_statistics':
        band = operation.get('band', 1)
        stats = geo_source.get_band_statistics(band)

        return {
            'type': 'band_statistics',
            'band': band,
            'data': stats
        }

    elif op_type == 'pixel_value':
        x = operation.get('x')
        y = operation.get('y')
        band = operation.get('band', 1)

        if x is None or y is None:
            raise ValueError("X and Y coordinates required for pixel value query")

        value = geo_source.get_pixel_value(x, y, band)

        return {
            'type': 'pixel_value',
            'x': x,
            'y': y,
            'band': band,
            'value': value
        }

    else:
        raise ValueError(f"Unknown raster operation: {op_type}")
