"""Geospatial database operations with GDAL/OGR."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

try:
    from osgeo import gdal, ogr, osr
except ImportError:
    import gdal
    import ogr
    import osr

# Enable GDAL exceptions
gdal.UseExceptions()


class GeoDataSource:
    """Wrapper for geospatial data sources (vector or raster)."""

    def __init__(self, path: str):
        self.path = path
        self.file_path = Path(path)
        self.data_type = None  # 'vector' or 'raster'
        self.dataset = None
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load the geospatial dataset and determine its type."""
        # Try opening as vector first
        vector_ds = ogr.Open(self.path)
        if vector_ds is not None:
            self.data_type = 'vector'
            self.dataset = vector_ds
            return

        # Try opening as raster
        raster_ds = gdal.Open(self.path)
        if raster_ds is not None:
            self.data_type = 'raster'
            self.dataset = raster_ds
            return

        raise ValueError(f"Could not open {self.path} as vector or raster data")

    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the dataset."""
        if self.data_type == 'vector':
            return self._get_vector_info()
        else:
            return self._get_raster_info()

    def _get_vector_info(self) -> Dict[str, Any]:
        """Get information about vector data."""
        layer = self.dataset.GetLayer(0)
        layer_defn = layer.GetLayerDefn()

        # Get geometry type
        geom_type = ogr.GeometryTypeToName(layer.GetGeomType())

        # Get spatial reference
        srs = layer.GetSpatialRef()
        proj_name = srs.GetAttrValue('PROJCS') if srs else 'Unknown'
        if not proj_name:
            proj_name = srs.GetAttrValue('GEOGCS') if srs else 'Unknown'
        epsg_code = srs.GetAttrValue('AUTHORITY', 1) if srs else None

        # Get extent
        extent = layer.GetExtent()

        # Get feature count
        feature_count = layer.GetFeatureCount()

        # Get field information
        fields = []
        for i in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(i)
            field_type = field_defn.GetFieldTypeName(field_defn.GetType())

            # Get sample values
            samples = []
            layer.ResetReading()
            for feature in layer:
                value = feature.GetField(i)
                if value is not None and value not in samples:
                    samples.append(value)
                if len(samples) >= 3:
                    break

            fields.append({
                'name': field_defn.GetName(),
                'type': field_type,
                'samples': samples
            })

        layer.ResetReading()

        return {
            'data_type': 'vector',
            'geometry_type': geom_type,
            'feature_count': feature_count,
            'fields': fields,
            'projection': proj_name,
            'epsg': epsg_code,
            'extent': {
                'min_x': extent[0],
                'max_x': extent[1],
                'min_y': extent[2],
                'max_y': extent[3]
            }
        }

    def _get_raster_info(self) -> Dict[str, Any]:
        """Get information about raster data."""
        # Get raster dimensions
        width = self.dataset.RasterXSize
        height = self.dataset.RasterYSize
        band_count = self.dataset.RasterCount

        # Get geotransform
        geotransform = self.dataset.GetGeoTransform()

        # Get projection
        projection = self.dataset.GetProjection()
        srs = osr.SpatialReference(wkt=projection)
        proj_name = srs.GetAttrValue('PROJCS') if srs else 'Unknown'
        if not proj_name:
            proj_name = srs.GetAttrValue('GEOGCS') if srs else 'Unknown'
        epsg_code = srs.GetAttrValue('AUTHORITY', 1) if srs else None

        # Get bands information
        bands = []
        for i in range(1, band_count + 1):
            band = self.dataset.GetRasterBand(i)
            band_info = {
                'number': i,
                'data_type': gdal.GetDataTypeName(band.DataType),
                'color_interpretation': gdal.GetColorInterpretationName(band.GetColorInterpretation()),
                'min': band.GetMinimum(),
                'max': band.GetMaximum(),
                'nodata': band.GetNoDataValue()
            }

            # Calculate statistics if not available
            if band_info['min'] is None or band_info['max'] is None:
                stats = band.ComputeStatistics(False)
                band_info['min'] = stats[0]
                band_info['max'] = stats[1]
                band_info['mean'] = stats[2]
                band_info['stddev'] = stats[3]

            bands.append(band_info)

        # Calculate extent
        min_x = geotransform[0]
        max_y = geotransform[3]
        max_x = min_x + geotransform[1] * width
        min_y = max_y + geotransform[5] * height

        return {
            'data_type': 'raster',
            'width': width,
            'height': height,
            'band_count': band_count,
            'bands': bands,
            'projection': proj_name,
            'epsg': epsg_code,
            'pixel_size': {
                'x': geotransform[1],
                'y': abs(geotransform[5])
            },
            'extent': {
                'min_x': min_x,
                'max_x': max_x,
                'min_y': min_y,
                'max_y': max_y
            }
        }

    def query_features(self, sql: Optional[str] = None,
                      bbox: Optional[Tuple[float, float, float, float]] = None,
                      limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query vector features with optional SQL, bounding box, or limit."""
        if self.data_type != 'vector':
            raise ValueError("Query features only works with vector data")

        layer = self.dataset.GetLayer(0)

        # Apply spatial filter if bbox provided
        if bbox:
            layer.SetSpatialFilterRect(*bbox)

        # Apply SQL filter if provided
        if sql:
            result_layer = self.dataset.ExecuteSQL(sql)
            if result_layer:
                layer = result_layer

        # Collect features
        features = []
        layer.ResetReading()
        count = 0

        for feature in layer:
            if limit and count >= limit:
                break

            # Get feature attributes
            feature_dict = {'id': feature.GetFID()}

            # Get geometry
            geom = feature.GetGeometryRef()
            if geom:
                feature_dict['geometry_type'] = geom.GetGeometryName()
                feature_dict['geometry'] = geom.ExportToJson()

            # Get attributes
            for i in range(feature.GetFieldCount()):
                field_name = feature.GetFieldDefnRef(i).GetName()
                feature_dict[field_name] = feature.GetField(i)

            features.append(feature_dict)
            count += 1

        # Clean up SQL result layer
        if sql and result_layer:
            self.dataset.ReleaseResultSet(result_layer)

        layer.ResetReading()
        return features

    def get_band_statistics(self, band_number: int = 1) -> Dict[str, float]:
        """Get statistics for a raster band."""
        if self.data_type != 'raster':
            raise ValueError("Band statistics only work with raster data")

        band = self.dataset.GetRasterBand(band_number)
        stats = band.ComputeStatistics(False)

        return {
            'min': stats[0],
            'max': stats[1],
            'mean': stats[2],
            'stddev': stats[3]
        }

    def get_pixel_value(self, x: float, y: float, band_number: int = 1) -> Optional[float]:
        """Get pixel value at geographic coordinates."""
        if self.data_type != 'raster':
            raise ValueError("Pixel values only work with raster data")

        # Convert geographic coordinates to pixel coordinates
        geotransform = self.dataset.GetGeoTransform()
        inv_geotransform = gdal.InvGeoTransform(geotransform)

        pixel_x = int(inv_geotransform[0] + inv_geotransform[1] * x + inv_geotransform[2] * y)
        pixel_y = int(inv_geotransform[3] + inv_geotransform[4] * x + inv_geotransform[5] * y)

        # Check if within bounds
        if pixel_x < 0 or pixel_x >= self.dataset.RasterXSize or \
           pixel_y < 0 or pixel_y >= self.dataset.RasterYSize:
            return None

        # Read pixel value
        band = self.dataset.GetRasterBand(band_number)
        value = band.ReadAsArray(pixel_x, pixel_y, 1, 1)

        return float(value[0, 0]) if value is not None else None

    def close(self) -> None:
        """Close the dataset."""
        if self.dataset:
            self.dataset = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
