import requests

def latest_datetime():
    """_summary_
    Get the latest datetime available for the era5 hourly dataset.
    Returns:
        tuple(int): year, month, day, hour, minute
    """
    r = requests.get("https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels")
    json = r.json()
    latest = json['extent']['temporal']['interval'][0][1]
    date = str(latest).split('T')[0].split('-')
    time = str(latest).split('T')[1].split(':')
    return date[0], date[1], date[2], time[0], time[1]

if __name__ == '__main__':
    print(latest_datetime())