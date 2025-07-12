# appa-fetcher

A service that pulls data from online sources on which the APPA model is then conditioned for its public predictions.

## Usage

```bash
python main.py [-h] [-t TARGET_FOLDER] [-s DATA_SOURCE]
```

## API key requirements

| Data Source | API  key required | Key Environment variable |
|-------------|-------------------|--------------------------|
|ifs          | No                | /                        |
|era5         | Yes               | CDS_API_KEY |

Note that `era5` also requires accepting the terms and conditions. On first try, an error message should guide you to do so.

## Arguments

- **-h, --help**
    Show an help message and exit.

- **-t, --target-folder** _TARGET_FOLDER_: 
    Destination output folder for the NetCDF4 files. Files will be saved in a subfolder named after the data source. The name of the data files will be the timestamp of the time at which they were generated, in the format `YY-mm-ddTHH-MM-SSZ`. Default is `./data`.

- **-s, --data-source** _DATA_SOURCE_: 
    The database or algorithm to fetch data from. Available options: `era5`, `ifs`. Default is `era5`.
