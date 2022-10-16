import numpy as np
import copy
import os
import pickle
import warnings
import matplotlib.pyplot as plt
from . import _get_functions as get_functions
from . import _proces_tools as tools
from . import filters

# TODO: Decide the amount of checking and control in the class


class SarImage:
    """Class to contain SAR image, relevant meta data and methods.
    Attributes:
        bands(list of numpy arrays): The measurements.
        mission(str): Mission name:
        time(datetime): start time of acquisition
        footprint(dict): dictionary with footprint of image
                        footprint = {'latitude': np.array
                                    'longitude': np.array}
        product_meta(dict): Dictionary with meta data.
        band_names(list of str): Names of the band. Normally the polarisation.
        calibration_tables(list of dict): Dictionary with calibration_tables information for each band.
        geo_tie_point(list of dict): Dictionary with geo tie point for each band.
        band_meta(list of dict): Dictionary with meta data for each band.
    """

    def __init__(
        self,
        bands,
        mission=None,
        time=None,
        footprint=None,
        product_meta=None,
        band_names=None,
        calibration_tables=None,
        geo_tie_point=None,
        band_meta=None,
        unit=None,
    ):

        # assign values
        self.bands = bands
        self.mission = mission
        self.time = time
        self.footprint = footprint
        self.product_meta = product_meta
        self.band_names = band_names
        self.calibration_tables = calibration_tables
        self.geo_tie_point = geo_tie_point
        self.band_meta = band_meta
        self.unit = unit
        # Note that SlC is in strips. Maybe load as list of images

    def __repr__(self):
        return "Mission: %s \n Bands: %s" % (self.mission, str(self.band_names))

    def __getitem__(self, key):
        # Overload the get and slicing function a[2,4] a[:10,3:34]

        # Check i 2 dimension are given
        if len(key) != 2:
            raise ValueError("Need to slice both column and row like test_image[:,:]")

        # Get values as array
        if isinstance(key[0], int) & isinstance(key[1], int):
            return [band[key] for band in self.bands]

        if not isinstance(key[0], slice) & isinstance(key[1], slice):
            raise ValueError("Only get at slice is supported: a[2,4] a[:10,3:34]")

        # Else. Try to slice the image
        slice_row = key[0]
        slice_column = key[1]

        row_start = slice_row.start
        row_step = slice_row.step
        row_stop = slice_row.stop

        column_start = slice_column.start
        column_step = slice_column.step
        column_stop = slice_column.stop

        if row_start is None:
            row_start = 0
        if row_step is None:
            row_step = 1
        if row_stop is None:
            row_stop = self.bands[0].shape[0]
        if column_start is None:
            column_start = 0
        if column_step is None:
            column_step = 1
        if column_stop is None:
            column_stop = self.bands[0].shape[1]

        # Adjust footprint to window
        footprint_lat = np.zeros(4)
        footprint_long = np.zeros(4)

        window = ((row_start, row_stop), (column_start, column_stop))

        for i in range(2):
            for j in range(2):
                lat_i, long_i = self.get_coordinate(window[0][i], window[1][j])
                footprint_lat[2 * i + j] = lat_i
                footprint_long[2 * i + j] = long_i

        footprint = {"latitude": footprint_lat, "longitude": footprint_long}

        # Adjust geo_tie_point, calibration_tables
        n_bands = len(self.bands)
        geo_tie_point = copy.deepcopy(self.geo_tie_point)
        calibration_tables = copy.deepcopy(self.calibration_tables)
        for i in range(n_bands):
            geo_tie_point[i]["row"] = (geo_tie_point[i]["row"] - row_start) / row_step
            geo_tie_point[i]["column"] = (
                geo_tie_point[i]["column"] - column_start
            ) / column_step

            calibration_tables[i]["row"] = (
                calibration_tables[i]["row"] - row_start
            ) / row_step
            calibration_tables[i]["column"] = (
                calibration_tables[i]["column"] - column_start
            ) / column_step

        # slice the bands
        bands = [band[key] for band in self.bands]

        return SarImage(
            bands,
            mission=self.mission,
            time=self.time,
            footprint=footprint,
            product_meta=self.product_meta,
            band_names=self.band_names,
            calibration_tables=calibration_tables,
            geo_tie_point=geo_tie_point,
            band_meta=self.band_meta,
        )

    def get_index(self, lat, long):
        """Get index of a location by interpolating grid-points
        Args:
            lat(number): Latitude of the location
            long(number): Longitude of location
        Returns:
            row(int): The row index of the location
            column(int): The column index of the location
        Raises:
        """
        geo_tie_point = self.geo_tie_point
        row = np.zeros(len(geo_tie_point), dtype=int)
        column = np.zeros(len(geo_tie_point), dtype=int)

        # find index for each band
        for i in range(len(geo_tie_point)):
            lat_grid = geo_tie_point[i]["latitude"]
            long_grid = geo_tie_point[i]["longitude"]
            row_grid = geo_tie_point[i]["row"]
            column_grid = geo_tie_point[i]["column"]
            row[i], column[i] = get_functions.get_index_v2(
                lat, long, lat_grid, long_grid, row_grid, column_grid
            )

        # check that the results are the same
        if (abs(row.max() - row.min()) > 0.5) or (
            abs(column.max() - column.min()) > 0.5
        ):
            warnings.warn(
                "Warning different index found for each band. First index returned"
            )

        return row[0], column[0]

    def get_coordinate(self, row, column):
        """Get coordinate from index by interpolating grid-points
        Args:
            row(number): index of the row of interest position
            column(number): index of the column of interest position
        Returns:
            lat(float): Latitude of the position
            long(float): longitude of the position
        Raises:
        """

        geo_tie_point = self.geo_tie_point
        lat = np.zeros(len(geo_tie_point), dtype=float)
        long = np.zeros(len(geo_tie_point), dtype=float)

        # find index for each band
        for i in range(len(geo_tie_point)):
            lat_grid = geo_tie_point[i]["latitude"]
            long_grid = geo_tie_point[i]["longitude"]
            row_grid = geo_tie_point[i]["row"]
            column_grid = geo_tie_point[i]["column"]
            lat[i], long[i] = get_functions.get_coordinate(
                row, column, lat_grid, long_grid, row_grid, column_grid
            )

        # check that the results are the same
        if (abs(lat.max() - lat.min()) > 0.001) or (
            abs(long.max() - long.min()) > 0.001
        ):
            warnings.warn(
                "Warning different coordinates found for each band. Mean returned"
            )

        return lat.mean(), long.mean()

    def simple_plot(self, band_index=0, q_max=0.95, stride=1, **kwargs):
        """Makes a simple image of band and a color bar.
        Args:
            band_index(int): index of the band to plot.
            q_max(number): q_max is the quantile used to set the max of the color range for example
                            q_max = 0.95 shows the lowest 95 percent of pixel values in the color range
            stride(int): Used to skip pixels when showing. Good for large images.
            **kwargs: Passed on to matplotlib imshow
        Returns:
        Raises:
        """
        v_max = np.quantile(self.bands[band_index].reshape(-1), q_max)

        plt.imshow(
            self.bands[band_index][::stride, ::stride],
            cmap="gray",
            vmax=v_max,
            **kwargs
        )
        plt.colorbar()
        plt.show()

        return

    def calibrate(self, mode="gamma", tiles=4):
        """Get coordinate from index by interpolating grid-points
        Args:
            mode(string): 'sigma_0', 'beta' or 'gamma'
            tiles(int): number of tiles the image is divided into. This saves memory but reduce speed a bit
        Returns:
            Calibrated image as (SarImage)
        Raises:
        """
        if "raw" not in self.unit:
            warnings.warn(
                "Raw is not in units. The image have all ready been calibrated"
            )

        calibrated_bands = []
        for i, band in enumerate(self.bands):
            row = self.calibration_tables[i]["row"]
            column = self.calibration_tables[i]["column"]
            calibration_values = self.calibration_tables[i][mode]
            calibrated_bands.append(
                tools.calibration(band, row, column, calibration_values, tiles=tiles)
            )

        return SarImage(
            calibrated_bands,
            mission=self.mission,
            time=self.time,
            footprint=self.footprint,
            product_meta=self.product_meta,
            band_names=self.band_names,
            calibration_tables=self.calibration_tables,
            geo_tie_point=self.geo_tie_point,
            band_meta=self.band_meta,
            unit=mode,
        )

    def to_db(self):
        """Convert  to decibel"""
        db_bands = []
        for band in self.bands:
            if "amplitude" in self.unit:
                db_bands.append(20 * np.log(band))
            else:
                db_bands.append(10 * np.log(band))

        return SarImage(
            db_bands,
            mission=self.mission,
            time=self.time,
            footprint=self.footprint,
            product_meta=self.product_meta,
            band_names=self.band_names,
            calibration_tables=self.calibration_tables,
            geo_tie_point=self.geo_tie_point,
            band_meta=self.band_meta,
            unit=(self.unit + " dB"),
        )

    def boxcar(self, kernel_size, **kwargs):
        """Simple (kernel_size x kernel_size) boxcar filter.
        Args:
            kernel_size(int): size of kernel
            **kwargs: Additional arguments passed to scipy.ndimage.convolve
        Returns:
            Filtered image
        """

        filter_bands = []
        for band in self.bands:
            filter_bands.append(filters.boxcar(band, kernel_size, **kwargs))

        return SarImage(
            filter_bands,
            mission=self.mission,
            time=self.time,
            footprint=self.footprint,
            product_meta=self.product_meta,
            band_names=self.band_names,
            calibration_tables=self.calibration_tables,
            geo_tie_point=self.geo_tie_point,
            band_meta=self.band_meta,
            unit=self.unit,
        )

    def save(self, path):
        """Save the SarImage object in a folder at path.
        Args:
            path(str): Path of the folder where the the SarImage is saved.
                    Note that the folder is created and must not exist in advance
        Raises:
            ValueError: There already exist a folder at path
        """

        # Check if folder exists
        if os.path.exists(path):
            print("please give a path that is not used")
            raise ValueError

        # make folder
        os.makedirs(path)

        # save elements in separate files

        # product_meta
        file_path = os.path.join(path, "product_meta.pkl")
        pickle.dump(self.product_meta, open(file_path, "wb"))

        # unit
        file_path = os.path.join(path, "unit.pkl")
        pickle.dump(self.unit, open(file_path, "wb"))

        # footprint
        file_path = os.path.join(path, "footprint.pkl")
        pickle.dump(self.footprint, open(file_path, "wb"))

        # geo_tie_point
        file_path = os.path.join(path, "geo_tie_point.pkl")
        pickle.dump(self.geo_tie_point, open(file_path, "wb"))

        # band_names
        file_path = os.path.join(path, "band_names.pkl")
        pickle.dump(self.band_names, open(file_path, "wb"))

        # band_meta
        file_path = os.path.join(path, "band_meta.pkl")
        pickle.dump(self.band_meta, open(file_path, "wb"))

        # bands
        file_path = os.path.join(path, "bands.pkl")
        pickle.dump(self.bands, open(file_path, "wb"))

        # reduce size of calibration_tables list
        reduced_calibration = []
        for i in range(len(self.bands)):
            cal = self.calibration_tables[i]

            # Get mask of rows in the image.
            index_row = (0 < cal["row"]) & (cal["row"] < self.bands[i].shape[0])
            # Include one extra row on each side of the image to ensure interpolation
            index_row[1:] = index_row[1:] + index_row[:-1]
            index_row[:-1] = index_row[:-1] + index_row[1:]

            # Get mask of column in the image
            index_column = (0 < cal["column"]) & (
                cal["column"] < self.bands[i].shape[1]
            )
            # Include one extra column on each side of the image to ensure interpolation
            index_column[1:] = index_column[1:] + index_column[:-1]
            index_column[:-1] = index_column[:-1] + index_column[1:]

            # Get the relevant calibration_tables values
            reduced_cal_i = {
                "abs_calibration_const": cal["abs_calibration_const"],
                "row": cal["row"][index_row],
                "column": cal["column"][index_column],
                "azimuth_time": cal["azimuth_time"][index_row, :][:, index_column],
                "sigma_0": cal["sigma_0"][index_row, :][:, index_column],
                "beta_0": cal["beta_0"][index_row, :][:, index_column],
                "gamma": cal["gamma"][index_row, :][:, index_column],
                "dn": cal["dn"][index_row, :][:, index_column],
            }

            reduced_calibration.append(reduced_cal_i)

        # calibration_tables
        file_path = os.path.join(path, "calibration_tables.pkl")
        pickle.dump(reduced_calibration, open(file_path, "wb"))

        return

    def pop(self, index=-1):
        """
        Remove and return band at index (default last).
        Raises IndexError if list is empty or index is out of range.
        """

        band = self.bands.pop(index)
        name = self.band_names.pop(index)
        calibration_tables = self.calibration_tables.pop(index)
        geo_tie_point = self.geo_tie_point.pop(index)
        band_meta = self.band_meta.pop()

        return SarImage(
            [band],
            mission=self.mission,
            time=self.time,
            footprint=self.footprint,
            product_meta=self.product_meta,
            band_names=[name],
            calibration_tables=[calibration_tables],
            geo_tie_point=[geo_tie_point],
            band_meta=[band_meta],
            unit=self.unit,
        )

    def get_band(self, index):
        """
        Return SarImage of band at index (default last).
        """

        band = self.bands[index]
        name = self.band_names[index]
        calibration_tables = self.calibration_tables[index]
        geo_tie_point = self.geo_tie_point[index]
        band_meta = self.band_meta[index]

        return SarImage(
            [band],
            mission=self.mission,
            time=self.time,
            footprint=self.footprint,
            product_meta=self.product_meta,
            band_names=[name],
            calibration_tables=[calibration_tables],
            geo_tie_point=[geo_tie_point],
            band_meta=[band_meta],
            unit=self.unit,
        )
