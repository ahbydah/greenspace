import pandas as pd
import numpy as np
import geopandas as gpd
import pyproj
from shapely.geometry import Polygon

METERS_PER_MILE = 1609.34

def generate_aeqd_params(val):
    """
    val:iterable of lat, lon coordinates for a single point
    reutrns: proejction string for reprojecting points to the Azimuthal
            equidistant projection.
            This string is a required input for gpd.GeoDataFrame.to_crs
    The aeqd projection allows us to calculate accurate circular buffers around 
    a point by centering the projection at that point.
    """
    lat, lon = val[0], val[1]
    aeqd_crs = pyproj.Proj(proj='aeqd'
                           , ellps='WGS84'
                           , datum='WGS84'
                           , lat_0=lat
                           , lon_0=lon
                          ).srs
    return aeqd_crs

def get_buffer(val, radius=.5):
    '''
    val: list, np.ndarray, tuple
        val has two elements:
            - val[0] is an iterable of coordinates.
                (val[0][0]=lat, val[0][1]=lon)
            - val[1] is a projection string generated for this set of coordinates.
                Its used to project coordinates to AEQD for accurate buffer calculations.
    '''
    coords = val[0]
    lat, lon = coords[0], coords[1]
    prj_str = val[1]
    
    geom = gpd.points_from_xy([lon], [lat])
    point_gdf = gpd.GeoDataFrame([[coords]]
                                 , columns=['coords']
                                 , geometry=geom
                                 , crs='EPSG:4326')
    point_gdf = point_gdf.to_crs(crs=prj_str)
    # define global conversion variable
    point_gdf['buffer'] = point_gdf['geometry'].buffer(METERS_PER_MILE * radius)
    return point_gdf['buffer'].to_crs(epsg=4326)