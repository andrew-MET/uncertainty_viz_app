from pathlib import Path

def dttm_to_filename(dttm:str, model:str, data_dir: Path) -> Path:
  """
  Generate the filename from the datetime (YYYYMMDDHH)  
  :param dttm: Date time string in YYYYMMDDHH format
  :param model: The name of the forecast model
  Returns the filename
  """

  dttm = f"{dttm[:8]}T{dttm[8:]}Z"
  file_name = f"{model}_{dttm}.nc"
  return data_dir / file_name

def deode_filename(param:str, data_dir: Path) -> Path:
  file_name = f"{param}.nc"
  return data_dir / file_name

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

def short_param_to_deode_param(param: str):
  """
  Convert the parameter shortname that the API recieves to the 
  name of the name of the netcdf file and the parameter
  
  :param param: short name for the parameter
  :return a dictionary with the filename and parameter
  """
  
  params = {
    "temp": {"filename": "2t", "paramname": "2 metre temperature"},
    "press": {"filename": "msl", "paramname": "Mean sea level pressure"},
    "cloud": {"filename": "tcc", "paramname": "Total Cloud Cover"},
    "precip": {"filename": "tp", "paramname": "Total Precipitation"},
    "wind": {"filename": "10si", "paramname": "10 metre wind speed"},
    "wind100": {"filename": "100si", "paramname": "100 metre wind speed"}  
  }

  return params[param]

def scale_deode(data, params):
  return data * (params["agg_max"] - params["agg_min"]) / params["maxint"] + params["agg_min"]

  