from fastapi import FastAPI, HTTPException, Query
import xarray as xr
import numpy as np
from pathlib import Path
from typing import Literal
from datetime import datetime, timezone
from pandas import to_datetime

app = FastAPI()
DATA_DIR = Path("data")


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




def dttm_to_filename(dttm:str, model:str) -> Path:
  """
  Generate the filename from the datetime (YYYYMMDDHH)  
  :param dttm: Date time string in YYYYMMDDHH format
  :param model: The name of the forecast model
  Returns the filename
  """

  dttm = f"{dttm[:8]}T{dttm[8:]}Z"
  file_name = f"{model}_{dttm}.nc"
  return DATA_DIR / file_name



def short_param_to_ncdf_param(param: str):
  """
  Convert the parameter shortname that the API recieves to the 
  name of the parameter in the netcdf file
  
  :param param: short name for the parameter
  Returns the netcdf name of the giveb parameter
  """
  params = {
    "temp":   "air_temperature_2m",
    "press":  "air_pressure_at_sea_level",
    "cloud":  "cloud_area_fraction",
    "precip": "precipitation_amount_acc",
    "wind":   ["x_wind_10m", "y_wind_10m"]
  }

  nc_name = params[param]
  return nc_name


# timeseries endpoint - get request
@app.get("/api/timeseries")
async def get_timeseries(
  lat: float = Query(..., ge = -90, le = 90),
  lon: float = Query(..., ge = -180, le = 180),
  dttm: str = Query(..., pattern = r"\d{10}$"),
  model: str = Query(...),
  param: Literal["temp", "press", "cloud", "precip", "wind"] = Query(...)
):

  try:

    datetime.strptime(dttm, "%Y%m%d%H")

    nc_var = short_param_to_ncdf_param(param)
    file_path = dttm_to_filename(dttm, model)
    
    # Validate file path
    if not file_path.exists():
      raise HTTPException(status_code=404, detail="Dataset not found")

    # Get the data
    with xr.open_dataset(file_path) as ds:

      # Validate projection attributes
      required_proj_attrs = ['standard_parallel',
                             'latitude_of_projection_origin',
                             'longitude_of_central_meridian',
                             'earth_radius']

      if 'projection_lambert' not in ds:
        raise HTTPException(
          status_code=500,
          detail=f"Missing variable 'projection_lambert' in NetCDF"
        )

      proj_attrs = ds['projection_lambert'].attrs
      missing_attrs = [k for k in required_proj_attrs if k not in proj_attrs]
      if missing_attrs:
        raise HTTPException(
          status_code=500,
           detail=f"Missing Lambert projection attributes: {missing_attrs}"
        )

      # Requested lat and lon to projected coords
      x, y = latlon_to_lcc(lon, lat, proj_attrs)

      # Nearest grid point by subtraction
      x_grid = ds["x"].values
      y_grid = ds["y"].values

      x_min, x_max = x_grid.min(), x_grid.max()
      y_min, y_max = y_grid.min(), y_grid.max()

      if not (x_min <= x <= x_max):
        raise ValueError(f"x={x:.2f} outside grid bounds [{x_min:.2f}, {x_max:.2f}]")
      if not (y_min <= y <= y_max):
        raise ValueError(f"y={y:.2f} outside grid bounds [{y_min:.2f}, {y_max:.2f}]")
      
      x_idx = int(np.abs(x_grid - x).argmin())
      y_idx = int(np.abs(y_grid - y).argmin())

      print("x:" + str(x_idx) + " y:" + str(y_idx))

      # Extract the timeseries for the requested variable
      # For wind get the wind speed from x and y wind
      if isinstance(nc_var, list):
        u  = ds[nc_var[0]].isel(x = x_idx, y = y_idx).values
        v  = ds[nc_var[1]].isel(x = x_idx, y = y_idx).values
        ts = np.sqrt(u ** 2 + v ** 2)
      else:
        ts = ds[nc_var].isel(x = x_idx, y = y_idx).values

      # Get the times and convert to UTC
      dttm = to_datetime(ds["time"].values).strftime("%Y-%m-%d %H:%M:%S").tolist()

      # Get the ensemble members and generate the json output: {dttm: [...], mbr000: [...], mbr001: [...], ...}
      ens_mbrs = ds["ensemble_member"].values

      data = {}
      for idx, member in enumerate(ens_mbrs):
        key = f"mbr{member:03d}"
        data[key] = ts[:, idx].tolist()

      result = {"dttm": dttm, "data": data}

      return result
    
  except ValueError as e:
    raise HTTPException(status_code = 400, detail = str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code = 500, detail = str(e))
