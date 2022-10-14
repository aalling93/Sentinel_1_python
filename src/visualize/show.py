import cartopy
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib import rc
from PIL import Image


def show_thumbnail_function(
    gpd, amount: int = 60, username: str = "", password: str = ""
):
    """ """
    if (len(gpd)) < amount:
        amount = len(gpd)

    fig, axs = plt.subplots(
        int(amount / 5) + 1,
        5,
        figsize=(25, int(amount + 5)),
        facecolor="w",
        edgecolor="k",
    )
    fig.subplots_adjust(hspace=0.5, wspace=0.001)
    axs = axs.ravel()

    for i in range(amount):
        try:
            link = gpd.link_icon.iloc[i]
            im = Image.open(
                requests.get(link, stream=True, auth=(username, password)).raw
            )
            axs[i].imshow(im)
            axs[i].set_title(f"Img {i}")
        except:
            pass

    plt.show()


def show_co_pol_function(gpd, amount: int = 60, username: str = "", password: str = ""):
    """ """
    if (len(gpd)) < amount:
        amount = len(gpd)

    fig, axs = plt.subplots(
        int(amount / 5) + 1,
        5,
        figsize=(25, int(amount + 5)),
        facecolor="w",
        edgecolor="k",
    )
    fig.subplots_adjust(hspace=0.5, wspace=0.001)
    axs = axs.ravel()

    for i in range(amount):
        try:
            link = gpd.link_icon.iloc[i]
            im = np.array(
                Image.open(
                    requests.get(link, stream=True, auth=(username, password)).raw
                )
            )

            axs[i].imshow(im[:, :, 0], cmap="gray")
            axs[i].set_title(f"Img {i}")
        except:
            pass

    plt.show()


def show_cross_pol_function(
    gpd, amount: int = 60, username: str = "", password: str = ""
):
    """ """
    if (len(gpd)) < amount:
        amount = len(gpd)

    fig, axs = plt.subplots(
        int(amount / 5) + 1,
        5,
        figsize=(25, int(amount + 5)),
        facecolor="w",
        edgecolor="k",
    )
    fig.subplots_adjust(hspace=0.5, wspace=0.001)
    axs = axs.ravel()

    for i in range(amount):
        try:
            link = gpd.link_icon.iloc[i]
            im = np.array(
                Image.open(
                    requests.get(link, stream=True, auth=(username, password)).raw
                )
            )

            axs[i].imshow(im[:, :, 1], cmap="gray")
            axs[i].set_title(f"Img {i}")
        except:
            pass

    plt.show()











def plot_polygon(gdf):
    """
    Plotting polygons from a gdf.
    """
    projections = [
        cartopy.crs.PlateCarree(),
        cartopy.crs.Robinson(),
        cartopy.crs.Mercator(),
        cartopy.crs.Orthographic(),
        cartopy.crs.InterruptedGoodeHomolosine(),
    ]

    plt.figure(figsize=(20, 10))
    ax = plt.axes(projection=projections[0])
    try:
        extent = [
            gdf.bounds.minx.min() - 3,
            gdf.bounds.maxx.max() + 3,
            gdf.bounds.miny.min() - 3,
            gdf.bounds.maxy.max() + 3,
        ]
        ax.set_extent(extent)
    except:
        pass

    ax.stock_img()
    ax.coastlines(resolution="10m")
    ax.add_feature(cartopy.feature.OCEAN, zorder=0)
    ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor="black")
    ax.gridlines()
    try:
        ax.add_geometries(gdf.geometry, alpha=0.7, crs=projections[0], ec="red")
    except:
        pass
    gl3 = ax.gridlines(
        draw_labels=True, linewidth=1.0, color="black", alpha=0.75, linestyle="--"
    )
    gl3.left_labels = False
    gl3.top_labels = False
    gl3.xlabel_style = {"size": 10.0, "color": "gray", "weight": "bold"}
    gl3.ylabel_style = {"size": 10.0, "color": "gray", "weight": "bold"}
    gl3.xlabel_style = {"rotation": 45}
    gl3.ylabel_style = {"rotation": 45}

    return None


def initi(size: int = 32):
    matplotlib.rcParams.update({"font.size": size})
    rc("font", **{"family": "sans-serif", "sans-serif": ["Helvetica"]})
    rc("font", **{"family": "serif", "serif": ["Palatino"]})
    rc("text", usetex=True)
