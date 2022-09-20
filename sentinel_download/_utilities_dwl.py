import os
import sys

import geopandas as gpd
import requests

from .download_s1grd import bulk_downloader


def signal_handler(sig, frame):
    global abort
    sys.stderr.output("\n > Caught Signal. Exiting!\n")
    abort = True  # necessary to cause the program to stop
    raise SystemExit  # this will only abort the thread that the ctrl+c was caught in


def get_download_name(gpd):
    try:
        name = gpd.identifier.split("_")
        if gpd.producttype == "GRD":
            dwl_link = f"https://datapool.asf.alaska.edu/GRD_HD/S{name[0][-1]}/{gpd.identifier}.zip"
        else:
            dwl_link = f"https://datapool.asf.alaska.edu/{name[2]}/S{name[0][-1]}/{gpd.identifier}.zip"

        return dwl_link
    except Exception as e:
        print(e)
        pass


def download_sentinel_1_function(
    gdf: gpd.geodataframe.GeoDataFrame = None, data_folder: str = "sentinel_images"
):
    path = os.getcwd()

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        os.chdir(data_folder)

    if "sentinel-1" in gdf.platformname.iloc[0].lower():
        downloader = bulk_downloader(gdf)
        downloader.download_files()
        downloader.print_summary()
    os.chdir(path)


def download_thumbnails_function(
    grd,
    index: list = None,
    folder: str = "s1_thumbnails",
    username: str = "",
    password="",
):
    """ """
    # print(folder)
    if not os.path.exists(folder):
        os.makedirs(folder)

    if index:
        for link_in in index:
            link = grd.link_icon.iloc[link_in]
            name = grd.uuid.iloc[link_in]
            im = requests.get(link, stream=True, auth=(username, password)).content

            with open(f"{folder}/{name}.jpg", "wb") as handler:
                handler.write(im)
    else:
        for i in range(len(grd)):
            link = grd.link_icon.iloc[i]
            name = grd.uuid.iloc[i]
            im = requests.get(link, stream=True, auth=(username, password)).content

            with open(f"{folder}/{name}.jpg", "wb") as handler:
                handler.write(im)
