import numpy as np
from scipy import interpolate
from scipy.optimize import minimize


def get_coordinate(
    row, column, lat_gridpoints, long_gridpoints, row_gridpoints, column_gridpoints
):
    """Get coordinate from index by interpolating grid-points
    Args:
        row(number): index of the row of interest position
        column(number): index of the column of interest position
        lat_gridpoints(numpy array of length n): Latitude of grid-points
        long_gridpoints(numpy array of length n): Longitude of grid-points
        row_gridpoints(numpy array of length n): row of grid-points
        column_gridpoints(numpy array of length n): column of grid-points
    Returns:
        lat(float): Latitude of the position
        long(float): longitude of the position
    Raises:
    """

    # Create interpolate functions
    points = np.vstack([row_gridpoints, column_gridpoints]).transpose()
    lat = float(interpolate.griddata(points, lat_gridpoints, (row, column)))
    long = float(interpolate.griddata(points, long_gridpoints, (row, column)))
    return lat, long


def get_index_v1(
    lat, long, lat_gridpoints, long_gridpoints, row_gridpoints, column_gridpoints
):
    """Get index of a location by interpolating grid-points
    Args:
        lat(number): Latitude of the location
        long(number): Longitude of location
        lat_gridpoints(numpy array of length n): Latitude of grid-points
        long_gridpoints(numpy array of length n): Longitude of grid-points
        row_gridpoints(numpy array of length n): row of grid-points
        column_gridpoints(numpy array of length n): column of grid-points
    Returns:
        row(int): The row index of the location
        column(int): The column index of the location
    Raises:
    """

    points = np.vstack([lat_gridpoints, long_gridpoints]).transpose()
    row = int(np.round(interpolate.griddata(points, row_gridpoints, (lat, long))))
    column = int(np.round(interpolate.griddata(points, column_gridpoints, (lat, long))))
    return row, column


def get_index_v2(
    lat, long, lat_gridpoints, long_gridpoints, row_gridpoints, column_gridpoints
):
    """
    Same as "get_index_v1" but consistent with "get_coordinate". Drawback is that it is slower
    """

    # Get an initial guess
    row_i, column_i = get_index_v1(
        lat, long, lat_gridpoints, long_gridpoints, row_gridpoints, column_gridpoints
    )

    # Define a loss function
    def loss_function(index):
        lat_res, long_res = get_coordinate(
            index[0],
            index[1],
            lat_gridpoints,
            long_gridpoints,
            row_gridpoints,
            column_gridpoints,
        )
        return ((lat - lat_res) * 100) ** 2 + ((long - long_res) * 100) ** 2

    # Find the index where "get_coordinate" gives the closest coordinates
    res = minimize(loss_function, [row_i, column_i])

    return int(round(res.x[0])), int(round(res.x[1]))
