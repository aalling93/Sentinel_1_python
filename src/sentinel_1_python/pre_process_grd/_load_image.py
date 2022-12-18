import os
import pickle
import warnings
from itertools import compress
import matplotlib
import numpy as np
from . import load_data
from ._get_functions import get_coordinate, get_index_v2
from .Process import SarImage


def s1_load(path, polarisation="all", location=None, size=None):
    """Function to load SAR image into SarImage python object.
    Currently supports: unzipped Sentinel 1 GRDH products
    Args:
        path(number): Path to the folder containing the SAR image
                as retrieved from: https://scihub.copernicus.eu/
        polarisation(list of str): List of polarisations to load.
        location(array/list): [latitude,longitude] Location to center the image.
                                If None the entire Image is loaded
        size(array/list): [width, height] Extend of image to load.
                                If None the entire Image is loaded
    Returns:
        SarImage: object with the SAR measurements and meta data from path. Meta data index
                and foot print are adjusted to the window
    Raises:
        ValueError: Location not in image
    """
    # manifest.safe
    path_safe = os.path.join(path, "manifest.safe")
    meta, error = load_data._load_meta(path_safe)

    # annotation
    ls_annotation = os.listdir(os.path.join(path, "annotation"))
    xml_files = [file[-3:] == "xml" for file in ls_annotation]
    xml_files = list(compress(ls_annotation, xml_files))
    annotation_temp = [
        load_data._load_annotation(os.path.join(path, "annotation", file))
        for file in xml_files
    ]

    # calibration_tables
    path_cal = os.path.join(path, "annotation", "calibration")
    ls_cal = os.listdir(path_cal)
    cal_files = [file[:11] == "calibration" for file in ls_cal]
    cal_files = list(compress(ls_cal, cal_files))
    calibration_temp = [
        load_data._load_calibration(os.path.join(path_cal, file)) for file in cal_files
    ]

    # measurement
    measurement_path = os.path.join(path, "measurement")
    ls_meas = os.listdir(measurement_path)
    tiff_files = [file[-4:] == "tiff" for file in ls_meas]
    tiff_files = list(compress(ls_meas, tiff_files))
    with warnings.catch_warnings():  # Ignore the "NotGeoreferencedWarning" when opening the tiff
        warnings.simplefilter("ignore")
        measurement_temp = [
            matplotlib.open(os.path.join(measurement_path, file)) for file in tiff_files
        ]

    # Check if polarisation is given
    if polarisation == "all":
        polarisation = meta["polarisation"]
    else:
        polarisation = [elem.upper() for elem in polarisation]

    # only take bands of interest and sort
    n_bands = len(polarisation)
    calibration_tables = [None] * n_bands
    geo_tie_point = [None] * n_bands
    band_meta = [None] * n_bands
    measurement = [None] * n_bands

    for i in range(n_bands):

        for idx, file in enumerate(tiff_files):
            if file.split("-")[3].upper() == polarisation[i]:
                measurement[i] = measurement_temp[idx]

        for band in calibration_temp:
            if band[1]["polarisation"] == polarisation[i]:
                calibration_tables[i] = band[0]

        for band in annotation_temp:
            if band[1]["polarisation"] == polarisation[i]:
                geo_tie_point[i] = band[0]
                band_meta[i] = band[1]

    # Check that there is one band in each tiff
    for i in range(n_bands):
        if measurement[i].count != 1:
            warnings.warn(
                "Warning tiff file contains several bands. First band read from each tiff file"
            )

    if (location is None) or (size is None):
        bands = [image.read(1) for image in measurement]
    else:
        # Check location is in foot print
        maxlat = meta["footprint"]["latitude"].max()
        minlat = meta["footprint"]["latitude"].min()
        maxlong = meta["footprint"]["longitude"].max()
        minlong = meta["footprint"]["longitude"].min()

        if not (minlat < location[0] < maxlat) & (minlong < location[1] < maxlong):
            raise ValueError("Location not inside the footprint")

        # get the index
        row = np.zeros(len(geo_tie_point), dtype=int)
        column = np.zeros(len(geo_tie_point), dtype=int)
        for i in range(len(geo_tie_point)):
            lat_grid = geo_tie_point[i]["latitude"]
            long_grid = geo_tie_point[i]["longitude"]
            row_grid = geo_tie_point[i]["row"]
            column_grid = geo_tie_point[i]["column"]
            row[i], column[i] = get_index_v2(
                location[0], location[1], lat_grid, long_grid, row_grid, column_grid
            )
        # check if index are the same for all bands
        if (abs(row.max() - row.min()) > 0.5) or (
            abs(column.max() - column.min()) > 0.5
        ):
            warnings.warn(
                "Warning different index found for each band. First index returned"
            )

        # Find the window
        row_index_min = row[0] - int(size[0] / 2)
        row_index_max = row[0] + int(size[0] / 2)

        column_index_min = column[0] - int(size[1] / 2)
        column_index_max = column[0] + int(size[1] / 2)

        # Check if window is in image
        if row_index_max < 0 or column_index_max < 0:
            raise ValueError("Error window not in image ")

        if row_index_min < 0:
            warnings.warn("Extend out of image. Window constrained ")
            row_index_min = 0

        if column_index_min < 0:
            warnings.warn("Extend out of image. Window constrained ")
            column_index_min = 0

        for image in measurement:
            if row_index_min > image.height or column_index_min > image.width:
                raise ValueError("Error window not in image")

            if row_index_max > image.height:
                warnings.warn("Extend out of image. Window constrained ")
                row_index_max = image.height

            if column_index_max > image.width:
                warnings.warn("Extend out of image. Window constrained ")
                column_index_max = image.width

        # Adjust footprint to window
        footprint_lat = np.zeros(4)
        footprint_long = np.zeros(4)
        window = ((row_index_min, row_index_max), (column_index_min, column_index_max))

        for i in range(2):
            for j in range(2):
                lat_i, long_i = get_coordinate(
                    window[0][i],
                    window[1][j],
                    geo_tie_point[0]["latitude"],
                    geo_tie_point[0]["longitude"],
                    geo_tie_point[0]["row"],
                    geo_tie_point[0]["column"],
                )
                footprint_lat[2 * i + j] = lat_i
                footprint_long[2 * i + j] = long_i

        meta["footprint"]["latitude"] = footprint_lat
        meta["footprint"]["longitude"] = footprint_long

        # Adjust geo_tie_point, calibration_tables
        for i in range(n_bands):
            geo_tie_point[i]["row"] = geo_tie_point[i]["row"] - row_index_min
            geo_tie_point[i]["column"] = geo_tie_point[i]["column"] - column_index_min

            calibration_tables[i]["row"] = calibration_tables[i]["row"] - row_index_min
            calibration_tables[i]["column"] = (
                calibration_tables[i]["column"] - column_index_min
            )

        # load the data window
        bands = [image.read(1, window=window) for image in measurement]

    return SarImage(
        bands,
        mission=meta["mission"],
        time=meta["start_time"],
        footprint=meta["footprint"],
        product_meta=meta,
        band_names=polarisation,
        calibration_tables=calibration_tables,
        geo_tie_point=geo_tie_point,
        band_meta=band_meta,
        unit="raw amplitude",
    )


def load(path):
    """Load SarImage saved with the SarImage save method (img.save(path)).
    Args:
        path(str): Path to the folder where SarImage is saved.
    Returns:
        SarImage
    """

    # product_meta
    file_path = os.path.join(path, "product_meta.pkl")
    product_meta = pickle.load(open(file_path, "rb"))

    # unit
    file_path = os.path.join(path, "unit.pkl")
    unit = pickle.load(open(file_path, "rb"))

    # footprint
    file_path = os.path.join(path, "footprint.pkl")
    footprint = pickle.load(open(file_path, "rb"))

    # geo_tie_point
    file_path = os.path.join(path, "geo_tie_point.pkl")
    geo_tie_point = pickle.load(open(file_path, "rb"))

    # band_names
    file_path = os.path.join(path, "band_names.pkl")
    band_names = pickle.load(open(file_path, "rb"))

    # band_meta
    file_path = os.path.join(path, "band_meta.pkl")
    band_meta = pickle.load(open(file_path, "rb"))

    # bands
    file_path = os.path.join(path, "bands.pkl")
    bands = pickle.load(open(file_path, "rb"))

    # calibration_tables
    file_path = os.path.join(path, "calibration_tables.pkl")
    calibration_tables = pickle.load(open(file_path, "rb"))

    return SarImage(
        bands,
        mission=product_meta["mission"],
        time=product_meta["start_time"],
        footprint=footprint,
        product_meta=product_meta,
        band_names=band_names,
        calibration_tables=calibration_tables,
        geo_tie_point=geo_tie_point,
        band_meta=band_meta,
        unit=unit,
    )
