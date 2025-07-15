import numpy as np
from datetime import datetime, timezone, timedelta
import xarray as xr

TSI = 1361 # W m^-2

def toa_solar_radiation(latitude_degrees, longitude_degrees, datetime: datetime):
    '''
    Approximate TOA solar radiation at given latitude, longitude, and datetime.
    Ignores TSI variability and equation of time.
    
    Params:
        latitude_degrees (float or np.array): Latitude(s) in degrees
        longitude_degrees (float or np.array): Longitude(s) in degrees
        datetime (datetime): Time of calculation
    
    Returns:
        float or np.array: Solar radiation (W/m²), clipped at zero
    '''
    return np.maximum(TSI * cos_solar_zenith_angle(
        latitude_degrees,
        declination_angle_degrees(datetime.timetuple().tm_yday),
        hour_angle_degrees(datetime, longitude_degrees)
    ), 0)

def integrated_toa_solar_radiation(latitude_degrees, longitude_degrees, datetime, hours):
    '''
    Integrate TOA solar radiation over a period (hours) using trapezoidal rule.
    Valid for short durations (~1 hour).
    
    Params:
        latitude_degrees (float or np.array): Latitude(s) in degrees
        longitude_degrees (float or np.array): Longitude(s) in degrees
        datetime (datetime): End time of integration
        hours (float): Duration of integration in hours
    
    Returns:
        float or np.array: Integrated solar radiation (J/m²)
    '''
    toa_b = toa_solar_radiation(
        latitude_degrees,
        longitude_degrees,
        datetime
    )
    toa_a = toa_solar_radiation(
        latitude_degrees,
        longitude_degrees,
        datetime - timedelta(hours=int(hours))
    )
    return hours * 3600 * (toa_b + toa_a) / 2

def xarray_integrated_toa_solar_radiation(datetime, hours=1) -> xr.DataArray:
    lats = np.arange(-90, 90, 0.25)
    lons = np.arange(-180, 180, 0.25)
    toa_radiation_vec = np.vectorize(integrated_toa_solar_radiation)
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    values = integrated_toa_solar_radiation(lat_grid, lon_grid, datetime, hours)
    toa_da = xr.DataArray(
        values,
        coords={"latitude": lats, "longitude": lons},
        dims=["latitude", "longitude"],
        name="toa_radiation",
        attrs={
            "units": "J m-2",
            "long_name": "Hourly TOA solar radiation"
        }
    )
    return toa_da
    
def cos_solar_zenith_angle(latitude_degrees, declination_degrees, hour_angle_degrees):
    '''
    Get the cosine of the solar zenith angle.
    Formula found [here](https://en.wikipedia.org/wiki/Solar_zenith_angle).
    '''
    phi = np.deg2rad(latitude_degrees)
    delta = np.deg2rad(declination_degrees)
    h = np.deg2rad(hour_angle_degrees)
    return np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.cos(h)

def declination_angle_degrees(day_of_year):
    '''
    Get the declination angle, in degrees.
    Formula found [here](https://www.pveducation.org/pvcdrom/properties-of-sunlight/declination-angle).
    
        Params:
            - day_of_year(int): day of year, with Jan 1 as d = 1.
        Returns:
            - declination_angle_degrees(float): The declination angle, in degrees.
    '''
    return -23.45 * np.cos(np.deg2rad((360/365) * (day_of_year + 10)))

def utc_decimal_hours(dt: datetime):
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600

def hour_angle_degrees(datetime, longitude_degrees):
    '''Get the hour angle, in degrees, for a given datetime object.
    Formulas found [here](https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time).
        Params:
            - datetime(datetime): The datetime at which t
    '''
    utc_hours = utc_decimal_hours(datetime)
    return 15 * (utc_hours + longitude_degrees/15 - 12)
    
if __name__ == '__main__':
    dt = datetime(2025, 7, 9, 10, 0, 0, tzinfo=timezone.utc)
    toa_da = xarray_integrated_toa_solar_radiation(dt, 1)
    ds = xr.Dataset({"toa_radiation": toa_da})
    ds.to_netcdf("toa_radiation_map.nc")