from ._masking import *
from ..visualize import show
from ._utilities import *
from .query_data import *
import getpass


class Sentinel_metadata:
    """'"""

    def __init__(self, fontsize: int = 32):
        super(Sentinel_metadata, self).__init__()

        try:
            new_username = raw_input("Username for Copernicus Hub: ")
        except NameError:
            new_username = input("Username for Copernicus Hub: ")
        new_password = getpass.getpass(prompt="Password (will not be displayed): ")

        self.USERNAME = new_username
        self.PASSWORD = new_password

        show.initi(fontsize)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def get_metadata(
        self, sensor: str = "s1_slc", start_data: str = "", end_date: str = ""
    ):

        # getting metadata

        if sensor.lower() in ["s1_slc", "sentinel1_slc", "sentinel-1_slc"]:
            self.products_df = get_s1_slc_metadata_area(
                self.bbox, self.USERNAME, self.PASSWORD, start_data, end_date
            )
            self.sensor = "sentinel_1_slc"

        if sensor.lower() in ["s1_raw", "sentinel1_level0", "s1_l0", "raw"]:
            try:
                self.products_df = get_s1_raw_metadata_area(
                    self.bbox, self.USERNAME, self.PASSWORD, start_data, end_date
                )
            except:
                pass
            self.sensor = "sentinel_1_raw"

        elif sensor.lower() in ["s1_grd", "sentinel1_grd", "sentinel-1_grd"]:
            self.products_df = get_s1_grd_metadata_area(
                self.bbox, self.USERNAME, self.PASSWORD, start_data, end_date
            )
            self.sensor = "sentinel_1_grd"
        elif sensor.lower() in ["s2_l1c", "sentinel2_l1c", "sentinel-2_l1c"]:
            self.products_df = get_s2_metadata_area(
                self.bbox, self.USERNAME, self.PASSWORD, start_data, end_date
            )
            self.sensor = "sentinel_2_l1c"

        elif sensor.lower() in ["s2_l2a", "sentinel2_l2a", "sentinel-2_l2a"]:
            self.products_df = get_s2_l2a_metadata_area(
                self.bbox, self.USERNAME, self.PASSWORD, start_data, end_date
            )
            self.sensor = "sentinel_2_l2a"

        self.org_products_df = self.products_df

        return self

    def area(self, bbox: list = []):
        # getting area
        """lonmin, lonmax, latmin,latmax"""
        self.bbox = get_area(bbox)

        return self

    def show_thumnails(self, amount=10):
        show.show_thumbnail_function(
            self.products_df,
            amount=amount,
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        return None

    def show_cross_pol(self, amount=10):
        if self.sensor in ["sentinel_1_grd", "sentinel_1_slc", "sentinel_1_raw"]:
            show.show_cross_pol_function(
                self.products_df,
                amount=amount,
                username=self.USERNAME,
                password=self.PASSWORD,
            )
            return None

    def show_co_pol(self, amount=10):
        if self.sensor in ["sentinel_1_grd", "sentinel_1_slc", "sentinel_1_raw"]:
            show.show_co_pol_function(
                self.products_df,
                amount=amount,
                username=self.USERNAME,
                password=self.PASSWORD,
            )
            return None

    def land(self):
        self.products_df = inland(self.products_df)

    def water(self):
        self.products_df = inwater(self.products_df)

    def plot_image_areas(self):
        show.plot_polygon(self.products_df)

    def cloud_cover(self, cloud_cover: float = 1):
        if self.sensor in ["sentinel_2_l1c", "sentinel_2_l2a"]:
            self.products_df = self.products_df[
                self.products_df.cloudcoverpercentage < cloud_cover
            ]

    def vv(self):
        if self.sensor in ["sentinel_1_grd", "sentinel_1_slc", "sentinel_1_raw"]:
            self.products_df = self.products_df[
                self.products_df.polarisationmode == "VV VH"
            ]

    def iw(self):
        if self.sensor in ["sentinel_1_grd", "sentinel_1_slc", "sentinel_1_raw"]:
            self.products_df = self.products_df[
                self.products_df.sensoroperationalmode == "IW"
            ]

    def ew(self):
        if self.sensor in ["sentinel_1_grd", "sentinel_1_slc", "sentinel_1_raw"]:
            self.products_df = self.products_df[
                self.products_df.sensoroperationalmode == "EW"
            ]

    def hh(self):
        if self.sensor in ["sentinel_1_grd", "sentinel_1_slc", "sentinel_1_raw"]:
            self.products_df = self.products_df[
                self.products_df.polarisationmode == "HH HV"
            ]
