from fastapi import APIRouter, Query, HTTPException
from typing import Literal
from datetime import datetime, timezone
from pandas import to_datetime
import xarray as xr
import numpy as np
import time

from app.settings import settings
from app.utils import dttm_to_filename, short_param_to_ncdf_param, short_param_to_deode_param, deode_filename, scale_deode
from app.projections import latlon_to_lcc, latlon_to_web_mercator

router = APIRouter(prefix="/api", tags=["timeseries"])

# cf complient timeseries endpoint - get request
@router.get("/cf-timeseries")
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
    file_path = dttm_to_filename(dttm, model, settings.DATA_DIR)
    print(file_path)
    
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


# Time series for deode specific netcdf files
# Separate file for each param, not cf standard names
# In web mercator projection
# Data stored as 2-byte integers - need scaling
@router.get("/deode-timeseries")
async def get_timeseries(
  lat: float = Query(..., ge = -90, le = 90),
  lon: float = Query(..., ge = -180, le = 180),
  dttm: str = Query(..., pattern = r"\d{10}$"),
  param: Literal["temp", "press", "cloud", "precip", "wind", "wind100"] = Query(...)
):
  
  try:

    datetime.strptime(dttm, "%Y%m%d%H")

    nc_var_info = short_param_to_deode_param(param)
    file_path = deode_filename(nc_var_info["filename"], settings.DATA_DIR)
    print(file_path)
    
    # Validate file path
    if not file_path.exists():
      raise HTTPException(status_code=404, detail="Dataset not found")

    # Get the data
    t0 = time.perf_counter()

    with xr.open_dataset(file_path) as ds:

      t1 = time.perf_counter()
      print("open: ", t1 - t0)

      # Requested lat and lon to projected coords
      x, y = latlon_to_web_mercator(lon, lat)

      t2 = time.perf_counter()
      print("reproject: ", t2 - t1)


      # Nearest grid point by subtraction
      x_grid = ds["lon"].values
      y_grid = ds["lat"].values

      x_min, x_max = x_grid.min(), x_grid.max()
      y_min, y_max = y_grid.min(), y_grid.max()

      if not (x_min <= x <= x_max):
        raise ValueError(f"x={x:.2f} outside grid bounds [{x_min:.2f}, {x_max:.2f}]")
      if not (y_min <= y <= y_max):
        raise ValueError(f"y={y:.2f} outside grid bounds [{y_min:.2f}, {y_max:.2f}]")
      
      x_idx = int(np.abs(x_grid - x).argmin())
      y_idx = int(np.abs(y_grid - y).argmin())

      print("x:" + str(x_idx) + " y:" + str(y_idx))
      t3 = time.perf_counter()
      print("find indices: ", t3 - t2)


      # Extract the timeseries for the requested variable
      ts = ds[nc_var_info["paramname"]].isel(lon = x_idx, lat = y_idx).values

      t4 = time.perf_counter()
      print("read: ", t4 - t3)

      ts = scale_deode(ts, ds[nc_var_info["paramname"]].attrs)

      t5 = time.perf_counter()
      print("rescale: ", t5 - t4)


      # Get the times - they are in "%Y-%m%-%d %H:%M" - need to add the "%S" for consistency
      dttm =  list(map(lambda s: s + ":00", ds["valid_time"].values))
      t6 = time.perf_counter()
      print("dttm: ", t6 - t5)


      # Get the ensemble members and generate the json output: {dttm: [...], mbr000: [...], mbr001: [...], ...}
      ens_mbrs = ds["member"].values

      data = {}
      for idx, member in enumerate(ens_mbrs):
        key = f"mbr{member:03d}"
        data[key] = ts[idx, :].tolist()

      result = {"dttm": dttm, "data": data}
      t7 = time.perf_counter()
      print("to json: ", t7 - t6)


      return result
    
  except ValueError as e:
    raise HTTPException(status_code = 400, detail = str(e))
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code = 500, detail = str(e))
