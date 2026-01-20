import numpy as np

def latlon_to_lcc(lon, lat, params):
    """
    Convert latitude/longitude to Lambert Conformal Conic x/y.
    lon, lat in degrees
    params must contain:
      - standard_parallel (list or tuple, length 1)
      - latitude_of_projection_origin
      - longitude_of_central_meridian
      - earth_radius
    """

    # Convert to radians
    phi = np.radians(lat)
    lam = np.radians(lon)

    phi1 = np.radians(params['standard_parallel'][0])
    phi0 = np.radians(params['latitude_of_projection_origin'])
    lam0 = np.radians(params['longitude_of_central_meridian'])
    R    = params['earth_radius']

    # LCC constants
    n = np.sin(phi1)

    F = (R * np.cos(phi1) / n) * \
        (np.tan(np.pi / 4 + phi1 / 2) ** n)

    rho  = F / (np.tan(np.pi / 4 + phi / 2) ** n)
    rho0 = F / (np.tan(np.pi / 4 + phi0 / 2) ** n)

    x = rho * np.sin(n * (lam - lam0))
    y = rho0 - rho * np.cos(n * (lam - lam0))

    print("x:" + str(x) + " y:" + str(y))

    return x, y


def latlon_to_web_mercator(lon, lat):
    """
    Convert latitude/longitude (EPSG:4326) to Web Mercator (EPSG:3857)
    """

    R = 6378137.0

    # clamp latitude
    lat = np.clip(lat, -85.05112878, 85.05112878)

    lon_rad = np.radians(lon)
    lat_rad = np.radians(lat)

    x = R * lon_rad
    y = R * np.log(np.tan(np.pi / 4 + lat_rad / 2))

    return x, y
