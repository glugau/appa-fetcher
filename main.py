import os
from dotenv import load_dotenv
import cdsapi
import requests

load_dotenv() # development

DATA_FOLDER = os.environ['DATA_FOLDER']
CDS_API_KEY = os.environ['CDS_API_KEY']

# Save the API key (env var) to the ~/.cdsapirc file (as required by the spec)
with open(os.path.expandvars("$HOME/.cdsapirc"), "w+") as f:
    f.write(f'url: https://cds.climate.copernicus.eu/api\nkey: {CDS_API_KEY}')
    
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def get_latest_datetime():
    """_summary_
    Get the latest datetime available for the era5 hourly dataset.
    Returns:
        tuple(str): year, month, day, hour, minute
    """
    r = requests.get("https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels")
    json = r.json()
    latest = json['extent']['temporal']['interval'][0][1]
    date = str(latest).split('T')[0].split('-')
    time = str(latest).split('T')[1].split(':')
    return date[0], date[1], date[2], time[0], time[1]

latest_datetime = get_latest_datetime()
filename = f'{latest_datetime[0]}-{latest_datetime[1]}-{latest_datetime[2]} {latest_datetime[3]}:{latest_datetime[4]}.zip'
target_file = os.path.join(DATA_FOLDER, filename)

dataset = "reanalysis-era5-single-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_dewpoint_temperature",
        "2m_temperature",
        "mean_sea_level_pressure",
        "mean_wave_direction",
        "mean_wave_period",
        "sea_surface_temperature",
        "significant_height_of_combined_wind_waves_and_swell",
        "surface_pressure",
        "total_precipitation"
    ],
    "year": [latest_datetime[0]],
    "month": [latest_datetime[1]],
    "day": [latest_datetime[2]],
    "time": [f'{latest_datetime[3]}:{latest_datetime[4]}'],
    "data_format": "netcdf",
    "download_format": "zip"
}

client = cdsapi.Client()
client.retrieve(dataset, request).download(target=target_file)