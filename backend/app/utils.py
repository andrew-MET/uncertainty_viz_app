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
