# https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
# https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels

import os
import requests
import cdsapi
import logging
from datetime import datetime

def download_latest(target: str):
    '''
    Download the latest relevant files given by the era5 model.
    In order for this function to work, a CDS API key must be provided as an
    environment variable called CDS_API_KEY (https://cds.climate.copernicus.eu).
        
        Parameters:
            - target(str): The target output **folder**.
        Returns:
            - datetime(str): The date and time of the downloaded data, in ISO
            8601 format (YYYY-mm-ddTHH-MMZ).
    '''
    
    CDS_API_KEY = os.environ['CDS_API_KEY']
    
    # Save the API key (env var) to the ~/.cdsapirc file (as required by the spec)
    with open(os.path.expandvars("$HOME/.cdsapirc"), "w+") as f:
        f.write(f'url: https://cds.climate.copernicus.eu/api\nkey: {CDS_API_KEY}')
    
    datetime = _latest_datetime()
    
    logger = logging.getLogger(__file__)
    logger.info(f'Found latest datetime: {datetime}')
    logger.info(f'Downloading pressure levels for {datetime}...')
    _download_latest_pressure_levels(target, datetime)
    logger.info(f'Downloading single levels for {datetime}...')
    _download_latest_single_levels(target, datetime)
    return datetime

def _download_latest_pressure_levels(target, datetime):
    '''
    Download the latest pressure levels. See
    [here](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels)
    for more info. The selected variables are the same as in the APPA paper.
    
    Will not work if called externally (requires the API key to first be stored).
    '''
    
    year, month, day = datetime.split('T')[0].split('-')[0:3]
    dataset = "reanalysis-era5-pressure-levels"
    request = {
        "product_type": ["reanalysis"],
        "variable": [
            "geopotential",
            "specific_humidity",
            "temperature",
            "u_component_of_wind",
            "v_component_of_wind"
        ],
        "year": [year],
        "month": [month],
        "day": [day],
        "time": [datetime.split('T')[1].removesuffix('Z')],
        "pressure_level": [
            "50", "100", "150",
            "200", "250", "300",
            "400", "500", "600",
            "700", "850", "925",
            "1000"
        ],
        "data_format": "netcdf",
        "download_format": "zip"
    }

    path = os.path.join(target, f'{datetime}-pressure.zip')

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(target=path)

def _download_latest_single_levels(target, datetime):
    '''
    Download the latest single levels. See
    [here](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels)
    for more info. The selected variables are the same as in the APPA paper.
    
    Will not work if called externally (requires the API key to first be stored).
    '''

    year, month, day = datetime.split('T')[0].split('-')[0:3]
    dataset = "reanalysis-era5-single-levels"
    request = {
        "product_type": ["reanalysis"],
        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_temperature",
            "mean_sea_level_pressure",
            "sea_surface_temperature",
            "total_precipitation"
        ],
        "year": [year],
        "month": [month],
        "day": [day],
        "time": [datetime.split('T')[1].removesuffix('Z')],
        "data_format": "netcdf",
        "download_format": "zip"
    }

    path = os.path.join(target, f'{datetime}-single.zip')

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(target=path)


def _latest_datetime():
    '''
    Get the latest datetime available for the era5 hourly dataset.
    Returns:
        datetime(str): Latest date and time available (YYYY-mm-ddTHH-MMZ)
    '''
    r = requests.get("https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels")
    json = r.json()
    latest_single = json['extent']['temporal']['interval'][0][1]
    latest_single_dt = datetime.fromisoformat(latest_single.replace('Z','+00:00'))
    
    r = requests.get("https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-pressure-levels")
    json = r.json()
    latest_pressure = json['extent']['temporal']['interval'][0][1]
    latest_pressure_dt = datetime.fromisoformat(latest_pressure.replace('Z','+00:00'))
    
    # Just as an extra safety, we make sure we take the last datetime that is
    # available for both datasets (single levels and pressure levels). The datetimes
    # should normally be equal.
    if latest_pressure_dt < latest_single_dt:
        return latest_pressure
    return latest_single

if __name__ == '__main__':
    datetime = _latest_datetime()
    print(datetime)