import datetime
import warnings
import xml.etree.ElementTree

import lxml.etree
import numpy as np


def _load_calibration(path):
    """Load sentinel 1 calibration_table file as dictionary from PATH.
    The calibration_table file should be as included in .SAFE format
    retrieved from: https://scihub.copernicus.eu/
    Args:
        path: The path to the calibration_table file
    Returns:
        calibration_table: A dictionary with calibration_table constants
            {"abs_calibration_const": float(),
            "row": np.array(int),
            "column": np.array(int),
            "azimuth_time": np.array(datetime64[us]),
            "sigma_0": np.array(float),
            "beta_0": np.array(float),
            "gamma": np.array(float),
            "dn": np.array(float),}
        info: A dictionary with the meta data given in 'adsHeader'
            {child[0].tag: child[0].text,
             child[1].tag: child[1].text,
             ...}
    """
    # open xml file
    tree = xml.etree.ElementTree.parse(path)
    root = tree.getroot()

    # Find info
    info_xml = root.findall("adsHeader")
    if len(info_xml) == 1:
        info = {}
        for child in info_xml[0]:
            info[child.tag] = child.text
    else:
        warnings.warn("Warning adsHeader not found")
        info = None

    # Find calibration_table list
    cal_vectors = root.findall("calibrationVectorList")
    if len(cal_vectors) == 1:
        cal_vectors = cal_vectors[0]
    else:
        warnings.warn("Error loading calibration_table list")
        return None, info

    # get pixels from first vector
    pixel = np.array(list(map(int, cal_vectors[0][2].text.split())))
    # initialize arrays
    azimuth_time = np.empty([len(cal_vectors), len(pixel)], dtype="datetime64[us]")
    line = np.empty([len(cal_vectors)], dtype=int)
    sigma_0 = np.empty([len(cal_vectors), len(pixel)], dtype=float)
    beta_0 = np.empty([len(cal_vectors), len(pixel)], dtype=float)
    gamma = np.empty([len(cal_vectors), len(pixel)], dtype=float)
    dn = np.empty([len(cal_vectors), len(pixel)], dtype=float)

    # get data
    for i, cal_vec in enumerate(cal_vectors):
        pixel_i = np.array(list(map(int, cal_vec[2].text.split())))
        if not np.array_equal(pixel, pixel_i):
            warnings.warn(
                "Warning in _load_calibration. The calibration_table data is not on a proper grid"
            )
        azimuth_time[i, :] = np.datetime64(cal_vec[0].text)
        line[i] = int(cal_vec[1].text)
        sigma_0[i, :] = np.array(list(map(float, cal_vec[3].text.split())))
        beta_0[i, :] = np.array(list(map(float, cal_vec[4].text.split())))
        gamma[i, :] = np.array(list(map(float, cal_vec[5].text.split())))
        dn[i, :] = np.array(list(map(float, cal_vec[6].text.split())))

    # Combine calibration_table info
    calibration_table = {
        "abs_calibration_const": float(root[1][0].text),
        "row": line,
        "column": pixel,
        "azimuth_time": azimuth_time,
        "sigma_0": sigma_0,
        "beta_0": beta_0,
        "gamma": gamma,
        "dn": dn,
    }

    return calibration_table, info


def _load_meta(SAFE_path):
    """Load manifest.safe as dictionary from SAFE_path.
    The manifest.safe file should be as included in .SAFE format
    retrieved from: https://scihub.copernicus.eu/
    Args:
        path: The path to the manifest.safe file
    Returns:
        metadata: A dictionary with meta_data
            example:
            {'mode': 'EW',
             'swath': ['EW'],
             'instrument_config': 1,
             'mission_data_ID': '110917',
             'polarisation': ['HH', 'HV'],
             'product_class': 'S',
             'product_composition': 'Slice',
             'product_type': 'GRD',
             'product_timeliness': 'Fast-24h',
             'slice_product_flag': 'true',
             'segment_start_time': datetime.datetime(2019, 1, 17, 19, 12, 32, 164986),
             'slice_number': 4,
             'total_slices': 4,
             'footprint': {'latitude': array([69.219566, 69.219566, 69.219566, 69.219566]),
                            'longitude': array([-35.149223, -35.149223, -35.149223, -35.149223])},
             'nssdc_identifier': '2016-025A',
             'mission': 'SENTINEL-1B',
             'orbit_number': array([14538, 14538]),
             'relative_orbit_number': array([162, 162]),
             'cycle_number': 89,
             'phase_identifier': 1,
             'start_time': datetime.datetime(2019, 1, 17, 19, 15, 36, 268585),
             'stop_time': datetime.datetime(2019, 1, 17, 19, 16, 25, 598196),
             'pass': 'ASCENDING',
             'ascending_node_time': datetime.datetime(2019, 1, 17, 18, 57, 16, 851007),
             'start_time_ANX': 1099418.0,
             'stop_time_ANX': 1148747.0}
            error: List of dictionary keys that was not found.
    """
    # Sorry the code look like shit but I do not like the file format
    # and I do not trust that ESA will keep the structure.
    # This is the reason for all the if statements and the error list

    # Open the xml like file
    with open(SAFE_path) as f:
        safe_test = f.read()
    safe_string = safe_test.encode(errors="ignore")
    safe_xml = lxml.etree.fromstring(safe_string)

    # Initialize results
    metadata = {}
    error = []

    # Prefixes used in the tag of the file. Do not ask me why the use them
    prefix1 = "{http://www.esa.int/safe/sentinel-1.0}"
    prefix2 = "{http://www.esa.int/safe/sentinel-1.0/sentinel-1}"
    prefix3 = "{http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1}"

    # Put the data into the metadata

    # Get nssdc_identifier
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "nssdcIdentifier")]
    if len(values) == 1:
        metadata["nssdc_identifier"] = values[0].text
    else:
        error.append("nssdcIdentifier")

    # Get mission
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "familyName")]
    values2 = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "number")]
    if (len(values) > 0) & (len(values2) == 1):
        metadata["mission"] = values[0].text + values2[0].text
    else:
        error.append("mission")

    # get orbit_number
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "orbitNumber")]
    if len(values) == 2:
        metadata["orbit_number"] = np.array([int(values[0].text), int(values[1].text)])
    else:
        error.append("orbit_number")

    # get relative_orbit_number
    values = [
        elem for elem in safe_xml.iterfind(".//" + prefix1 + "relativeOrbitNumber")
    ]
    if len(values) == 2:
        metadata["relative_orbit_number"] = np.array(
            [int(values[0].text), int(values[1].text)]
        )
    else:
        error.append("relative_orbit_number")

    # get cycle_number
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "cycleNumber")]
    if len(values) == 1:
        metadata["cycle_number"] = int(values[0].text)
    else:
        error.append("cycle_number")

    # get phase_identifier
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "phaseIdentifier")]
    if len(values) == 1:
        metadata["phase_identifier"] = int(values[0].text)
    else:
        error.append("phase_identifier")

    # get start_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "startTime")]
    if len(values) == 1:
        t = values[0].text
        metadata["start_time"] = datetime.datetime(
            int(t[:4]),
            int(t[5:7]),
            int(t[8:10]),
            int(t[11:13]),
            int(t[14:16]),
            int(t[17:19]),
            int(float(t[19:]) * 10**6),
        )
    else:
        error.append("start_time")

    # get stop_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + "stopTime")]
    if len(values) == 1:
        t = values[0].text
        metadata["stop_time"] = datetime.datetime(
            int(t[:4]),
            int(t[5:7]),
            int(t[8:10]),
            int(t[11:13]),
            int(t[14:16]),
            int(t[17:19]),
            int(float(t[19:]) * 10**6),
        )
    else:
        error.append("stop_time")

    # get pass
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + "pass")]
    if len(values) == 1:
        metadata["pass"] = values[0].text
    else:
        error.append("pass")

    # get ascending_node_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + "ascendingNodeTime")]
    if len(values) == 1:
        t = values[0].text
        metadata["ascending_node_time"] = datetime.datetime(
            int(t[:4]),
            int(t[5:7]),
            int(t[8:10]),
            int(t[11:13]),
            int(t[14:16]),
            int(t[17:19]),
            int(float(t[19:]) * 10**6),
        )
    else:
        error.append("ascending_node_time")

    # get start_time_ANX
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + "startTimeANX")]
    if len(values) == 1:
        metadata["start_time_ANX"] = float(values[0].text)
    else:
        error.append("start_time_ANX")

    # get stop_time_ANX
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + "stopTimeANX")]
    if len(values) == 1:
        metadata["stop_time_ANX"] = float(values[0].text)
    else:
        error.append("stop_time_ANX")

    # get mode
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "mode")]
    if len(values) == 1:
        metadata["mode"] = values[0].text
    else:
        error.append("mode")

    # get swath
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "swath")]
    if len(values) > 0:
        metadata["swath"] = [child.text for child in values]
    else:
        error.append("swath")

    # get instrument_config
    values = [
        elem
        for elem in safe_xml.iterfind(".//" + prefix3 + "instrumentConfigurationID")
    ]
    if len(values) == 1:
        metadata["instrument_config"] = int(values[0].text)
    else:
        error.append("instrument_config")

    # get mission_data_ID
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "missionDataTakeID")]
    if len(values) == 1:
        metadata["mission_data_ID"] = values[0].text
    else:
        error.append("mission_data_ID")

    # get polarisation
    values = [
        elem
        for elem in safe_xml.iterfind(
            ".//" + prefix3 + "transmitterReceiverPolarisation"
        )
    ]
    if len(values) > 0:
        metadata["polarisation"] = [child.text for child in values]
    else:
        error.append("polarisation")

    # get product_class
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "productClass")]
    if len(values) == 1:
        metadata["product_class"] = values[0].text
    else:
        error.append("product_class")

    # get product_composition
    values = [
        elem for elem in safe_xml.iterfind(".//" + prefix3 + "productComposition")
    ]
    if len(values) == 1:
        metadata["product_composition"] = values[0].text
    else:
        error.append("product_composition")

    # get product_type
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "productType")]
    if len(values) == 1:
        metadata["product_type"] = values[0].text
    else:
        error.append("product_type")

    # get product_timeliness
    values = [
        elem
        for elem in safe_xml.iterfind(".//" + prefix3 + "productTimelinessCategory")
    ]
    if len(values) == 1:
        metadata["product_timeliness"] = values[0].text
    else:
        error.append("product_timeliness")

    # get slice_product_flag
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "sliceProductFlag")]
    if len(values) == 1:
        metadata["slice_product_flag"] = values[0].text
    else:
        error.append("slice_product_flag")

    # get segment_start_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "segmentStartTime")]
    if len(values) == 1:
        t = values[0].text
        metadata["segment_start_time"] = datetime.datetime(
            int(t[:4]),
            int(t[5:7]),
            int(t[8:10]),
            int(t[11:13]),
            int(t[14:16]),
            int(t[17:19]),
            int(float(t[19:]) * 10**6),
        )
    else:
        error.append("segment_start_time")

    # get slice_number
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "sliceNumber")]
    if len(values) == 1:
        metadata["slice_number"] = int(values[0].text)
    else:
        error.append("slice_number")

    # get total_slices
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + "totalSlices")]
    if len(values) == 1:
        metadata["total_slices"] = int(values[0].text)
    else:
        error.append("total_slices")

    # get footprint
    values = [
        elem
        for elem in safe_xml.iterfind(".//" + "{http://www.opengis.net/gml}coordinates")
    ]
    if len(values) == 1:
        coordinates = values[0].text.split()
        lat = np.zeros(4)
        lon = np.zeros(4)
        for i in range(0, len(coordinates)):
            coord_i = coordinates[i].split(",")
            lat[i] = float(coord_i[0])
            lon[i] = float(coord_i[1])
        footprint = {"latitude": lat, "longitude": lon}
        metadata["footprint"] = footprint
    else:
        error.append("footprint")

    return metadata, error


def _load_annotation(path):
    """Load sentinel 1 annotation file as dictionary from PATH.
    The annotation file should be as included in .SAFE format
    retrieved from: https://scihub.copernicus.eu/
    Note that the file contains more information. Only the relevant have been chosen
    Args:
        path: The path to the annotation file
    Returns:
        geo_locations: A dictionary with geo location tie-points
            {'azimuth_time': np.array(datetime64[us]),
           'slant_range_time': np.array(float),
           'row': np.array(int),
           'column': np.array(int),
           'latitude': np.array(float),
           'longitude': np.array(float),
           'height': np.array(float),
           'incidence_angle': np.array(float),
           'elevation_angle': np.array(float)}
        info: A dictionary with the meta data given in 'adsHeader'
            {child[0].tag: child[0].text,
             child[1].tag: child[1].text,
             ...}
    """

    # open xml file
    tree = xml.etree.ElementTree.parse(path)
    root = tree.getroot()

    # Find info
    info_xml = root.findall("adsHeader")
    if len(info_xml) == 1:
        info = {}
        for child in info_xml[0]:
            info[child.tag] = child.text
    else:
        warnings.warn("Warning adsHeader not found")
        info = None

    # Find geo location list
    geo_points = root.findall("geolocationGrid")
    if len(geo_points) == 1:
        geo_points = geo_points[0][0]
    else:
        warnings.warn("Warning geolocationGrid not found")
        return None, None

    # initialize arrays
    n_points = len(geo_points)
    azimuth_time = np.empty(n_points, dtype="datetime64[us]")
    slant_range_time = np.zeros(n_points, dtype=float)
    line = np.zeros(n_points, dtype=int)
    pixel = np.zeros(n_points, dtype=int)
    latitude = np.zeros(n_points, dtype=float)
    longitude = np.zeros(n_points, dtype=float)
    height = np.zeros(n_points, dtype=float)
    incidence_angle = np.zeros(n_points, dtype=float)
    elevation_angle = np.zeros(n_points, dtype=float)

    # get the data
    for i in range(0, n_points):
        point = geo_points[i]

        azimuth_time[i] = np.datetime64(point[0].text)
        slant_range_time[i] = float(point[1].text)
        line[i] = int(point[2].text)
        pixel[i] = int(point[3].text)
        latitude[i] = float(point[4].text)
        longitude[i] = float(point[5].text)
        height[i] = float(point[6].text)
        incidence_angle[i] = float(point[7].text)
        elevation_angle[i] = float(point[8].text)

    # Combine geo_locations info
    geo_locations = {
        "azimuth_time": azimuth_time,
        "slant_range_time": slant_range_time,
        "row": line,
        "column": pixel,
        "latitude": latitude,
        "longitude": longitude,
        "height": height,
        "incidence_angle": incidence_angle,
        "elevation_angle": elevation_angle,
    }

    return geo_locations, info
