import sys
import xarray as xr
import os

if len(sys.argv) != 2:
    print('Missing file target!')
    print(f'\nUsage: python3 {os.path.basename(__file__)} [path to a NetCDF4 file]')
    sys.exit(1)

path = sys.argv[1]
ds = xr.open_dataset(path)
print("--- Full Structure ---\n")
print(ds)
print("\n--- Variables ---\n")
print(ds.data_vars)
print("\n--- Coordinates ---\n")
print(ds.coords)