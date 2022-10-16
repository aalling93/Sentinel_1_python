import numpy as np
from scipy.interpolate import RegularGridInterpolator


def calibration(band, rows, columns, calibration_values, tiles=4):
    """Calibrates image using linear interpolation.
    See https://sentinel.esa.int/documents/247904/685163/S1-Radiometric-Calibration-V1.0.pdf
    Args:
        band(2d numpy array): The non calibrated image
        rows(number): rows of calibration point
        columns(number): columns of calibration point
        calibration_values(2d numpy array): grid of calibration values
        tiles(int): number of tiles the image is divided into. This saves memory but reduce speed a bit
    Returns:
        calibrated image (2d numpy array)
    Raises:
    """

    # Create interpolation function
    f = RegularGridInterpolator((rows, columns), calibration_values)

    result = np.zeros(band.shape)
    # Calibrate one tile at the time
    column_start = 0
    column_max = band.shape[1]
    for i in range(tiles):
        column_end = int(column_max / tiles * (i + 1))
        # Create array of point where calibration is needed
        column_mesh, row_mesh = np.meshgrid(
            np.array(range(column_start, column_end)), np.array(range(band.shape[0]))
        )
        points = np.array([row_mesh.reshape(-1), column_mesh.reshape(-1)]).T
        # Get the image tile and the calibration values for it
        img_tile = band[:, column_start:column_end]
        img_cal = f(points).reshape(img_tile.shape)
        # Set in result
        result[:, column_start:column_end] = img_tile / img_cal

        column_start = column_end
    return result**2
