import os
import xarray as xr
from datetime import datetime, timezone
import logging
from . import shift_longitude

def process_data(era5_data_folder: str, 
                 ifs_data_folder: str, 
                 target_folder: str) -> None:
    '''
    Imports the latest data from IFS, the latest data from ERA5, and concatenates
    them so that the latest ERA5 sea surface temperature is given along with the
    rest. Makes everything into a single file.
    '''
    logger = logging.getLogger(__name__)
    
    path_era5_p, path_era5_s = _get_latest_era5(era5_data_folder)
    path_ifs_p, path_ifs_s = _get_latest_ifs(ifs_data_folder)
    
    ds_ifs_p = xr.open_dataset(path_ifs_p, engine='netcdf4')
    ds_ifs_s = xr.open_dataset(path_ifs_s, engine='netcdf4')
    ds_era5_s = xr.open_dataset(path_era5_s, engine='netcdf4').squeeze("valid_time", drop=True)
    logger.info('Loaded all required netCDF files for processing')
    
    logger.info('Shifting longitudes to a common range')
    shift_longitude.shift_longitude(ds_era5_s, '-180-180')
    
    sst = ds_era5_s['sst']
    
    logger.info('Merging ERA5 SST into IFS single level')
    ds_single = xr.merge([sst.to_dataset(), ds_ifs_s])

    # Merge all
    logger.info('Merging IFS pressure levels with single level data')
    ds_merged = xr.merge([ds_single, ds_ifs_p])
    
    now = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    target_path = os.path.join(target_folder, f'{now}.nc')
    
    # Save to file
    logger.info(f'Saving to {target_path}')
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    ds_merged.to_netcdf(target_path)

def _get_latest_era5(data_folder: str) -> tuple[str, str]:
    '''
    Gets the latest ifs data file that has been downloaded.

    Returns:
        (pressure_path, single_path) (str, str): A tuple of paths to a pressure and
            single level file.
    '''
    pressure_files = [f for f in os.listdir(data_folder) if f.endswith("pressure.nc")]
    single_files = [f for f in os.listdir(data_folder) if f.endswith("single.nc")]
    
    pressure_file = os.path.join(data_folder, max(pressure_files))
    single_file = os.path.join(data_folder, max(single_files))
    
    return pressure_file, single_file

def _get_latest_ifs(data_folder: str) -> tuple[str, str]:
    '''
    Gets the latest ifs data file that has been downloaded.

    Returns:
        (pressure_path, single_path) (str, str): A tuple of paths to a pressure and
            single level file.
    '''
    pressure_files = [f for f in os.listdir(data_folder) if f.endswith("pressure.nc")]
    single_files = [f for f in os.listdir(data_folder) if f.endswith("single.nc")]
    
    pressure_file = os.path.join(data_folder, max(pressure_files))
    single_file = os.path.join(data_folder, max(single_files))
    
    return pressure_file, single_file

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #process_data('./data/era5', './data/ifs', './data/processed')
    ds = xr.open_dataset('./data/processed/2025-07-14T11:38:45Z.nc')
    print(ds)