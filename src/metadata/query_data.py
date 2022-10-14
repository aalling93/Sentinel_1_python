from sentinelsat import SentinelAPI
from ._utilities import add_mgcs




def get_s2_metadata_area(
    footprint,
    username,
    password,
    start_data: str = "20151023",
    end_date: str = "20151025",
):
    # getting metadata s2 func
    api = api = SentinelAPI(username, password, "https://scihub.copernicus.eu/dhus/")
    products = api.query(
        footprint, date=(start_data, end_date), platformname="Sentinel-2"
    )
    products_df = api.to_geodataframe(products)
    # products_df = Satellite_metadata.add_mgcs(products_df)
    return products_df


def get_s1_slc_metadata_area(
    footprint,
    username,
    password,
    start_data: str = "20151023",
    end_date: str = "20151025",
):
    # getting metadata s1 slc func
    api = api = SentinelAPI(username, password, "https://scihub.copernicus.eu/dhus/")
    products = api.query(
        footprint,
        date=(start_data, end_date),
        producttype="SLC",
        platformname="Sentinel-1",
    )
    products_df = api.to_geodataframe(products)
    # products_df = Satellite_metadata.add_mgcs(products_df)
    return products_df


def get_s1_raw_metadata_area(
    footprint,
    username,
    password,
    start_data: str = "20151023",
    end_date: str = "20151025",
):
    # getting metadata s1 slc func
    api = api = SentinelAPI(username, password, "https://scihub.copernicus.eu/dhus/")
    products = api.query(
        footprint,
        date=(start_data, end_date),
        producttype="RAW",
        platformname="Sentinel-1",
    )
    products_df = api.to_geodataframe(products)

    return products_df



def get_s1_grd_metadata_area(
        footprint,
        username,
        password,
        start_data: str = "20151023",
        end_date: str = "20151025",
    ):
        # getting metadata s1 grd func
        api = api = SentinelAPI(
            username, password, "https://scihub.copernicus.eu/dhus/"
        )
        products = api.query(
            footprint,
            date=(start_data, end_date),
            producttype="GRD",
            platformname="Sentinel-1",
        )
        products_df = api.to_geodataframe(products)
        products_df = add_mgcs(products_df)
        return products_df