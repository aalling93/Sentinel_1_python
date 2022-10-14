

from .download_s1grd import *
from ._utilities_dwl import * 
import os 


class Satellite_download:
    def __init__(self, metadata=None):
        super(Satellite_download, self).__init__()

        self.PASSWORD = os.getenv('COPERNICUS_HUP_PASSWORD')
        self.USERNAME = os.getenv('COPERNICUS_HUP_USERNAME')
        self.products_df = metadata

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass


    def download_sentinel_1(self,data_folder: str = "sentinel_images"):
        
        if self.products_df.shape[0]>0:
            download_sentinel_1_function(self.products_df,data_folder)
        else:
            print('\n(note): No products')


    

    def download_thumbnails(self, index: list = None, folder="s1_thumnails"):
        download_thumbnails_function(
            self.products_df,
            index,
            folder,
            username=self.USERNAME,
            password=self.PASSWORD,
        )

    