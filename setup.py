from distutils.core import setup

setup(
  name='Sentinel_1_python',
  url='https://github.com/aalling93/Sentinel_1_python',
  author='Kristian Aalling Soerensen',
  author_email='kaaso@space.dtu.dk',
  packages=['namees',],
  install_requires=['numpy','geopandas','mgrs','scikit-learn','scipy','cartopy','rasterio','Pillow','pandas','sentinelsat','matplotlib'],
  version='0.1',
  license='MIT',
  description='A module to works with sentinel-1 images using only Python. You can get Metadata, you can Download images (after filtering the ones you want). You can Load and Calibrate the images and a bunch of other things.',
  long_description='see Readme'
)