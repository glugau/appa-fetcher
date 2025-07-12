# The IFS model is maintained by ECMWF, and outputs, from a set of observations
# and recent forecasts, an estimate of the current system.
# More information: 
#   https://www.ecmwf.int/en/forecasts/documentation-and-support/changes-ecmwf-model
#   https://data.ecmwf.int/forecasts/
#   https://confluence.ecmwf.int/display/DAC/ECMWF+open+data%3A+real-time+forecasts+from+IFS+and+AIFS
#   https://github.com/ecmwf/ecmwf-opendata - List of available params

from ecmwf.opendata import Client
import os
import xarray as xr

def download_latest(target: str):
    '''
    Download the latest relevant files given by the ifs model.
    In order for this function to work, a CDS API key must be provided as an
    environment variable called CDS_API_KEY (https://cds.climate.copernicus.eu).
        
        Parameters:
            - target(str): The target output **folder**.
        Returns:
            - datetime(str): The date and time of the downloaded data, in ISO
            8601 format (YYYY-mm-ddTHH-MMZ).
    '''
    data_file = os.path.join(target, 'data.grib2')
    client = Client(model='ifs')
    result = client.retrieve(
        type='fc',
        step=0,
        # param=[
        #         '10u',  # 10 metre U wind component
        #         '10v',  # 10 metre V wind component
        #         '2t',   # 2 metre temperature
        #         'msl',  # Mean sea level pressure
        #         'ro',   # Runoff
        #         'skt',  # Skin temperature
        #         'sp',   # Surface pressure
        #         # 'st',   # Soil Temperature - Not found?!
        #         # 'stl1', # Soil temperature level 1 - Not found?!
        #         'tcwv', # Total column vertically-integrated water vapour 	
        #         'tp',   # Total Precipitation
        #     ],
        target=data_file,
    )
    
    iso_format = result.datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    os.rename(data_file, os.path.join(target, f'{iso_format}.grib2'))
    data_file = os.path.join(target, f'{iso_format}.grib2')
    return iso_format
    ds_surface = xr.open_dataset(
            data_file,
            engine="cfgrib",
            decode_timedelta=True,
            backend_kwargs={"filter_by_keys": {"typeOfLevel": "surface"}}
    )
    
    print(ds)
    
    while True: pass
    
    ds_2m = xr.open_dataset(
        data_file,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "heightAboveGround", "level": 2}},
        decode_timedelta=True
    )
    
    ds_10m = xr.open_dataset(
        data_file,
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"typeOfLevel": "heightAboveGround", "level": 10}},
        decode_timedelta=True
    )
    
    print(ds_10m)
    
    #ds_2m = ds_2m.reset_coords('heightAboveGround', drop=True)
    #ds_10m = ds_10m.reset_coords('heightAboveGround', drop=True)

    combined = xr.merge([ds_2m, ds_10m])

    combined.to_netcdf(os.path.splitext(data_file)[0] + '.nc')
    return iso_format

if __name__ == '__main__':
    pass