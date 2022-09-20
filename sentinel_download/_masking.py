import geopandas as gpd


def inwater(products_df, landmask_file: str = "landmask/simplified_land_polygons.shp"):
    landmasks = get_mask(landmask_file)
    products_df = gpd.overlay(
        products_df, landmasks, how="difference", keep_geom_type=False
    )
    return products_df


def inland(products_df, landmask_file: str = "landmask/simplified_land_polygons.shp"):
    landmasks = get_mask(landmask_file)
    products_df = gpd.overlay(
        products_df, landmasks, how="intersection", keep_geom_type=False
    )
    return products_df


def get_mask(mask: str = None):
    """
    Fetching the landmask shape file. This is turned into a geopanda dataframe..
    """
    try:
        mask = gpd.read_file(mask)
        mask = mask.set_crs("epsg:3857", allow_override=True)  # 32634

    except:
        mask = gpd.read_file(mask)
        pass
    mask = mask.to_crs(crs=4326)
    return mask


def landmask_df(gdf, mask):
    """
    Removing land from the original gdf using the landmask gdf.
    If youre looking for habours, dont use this.. Lookin for ships, use this.

    """
    gdf_landmask = gpd.overlay(gdf, mask, how="difference", keep_geom_type=False)

    return gdf_landmask
