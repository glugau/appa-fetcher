import os
from dotenv import load_dotenv
import data_sources
import argparse
import importlib
import logging

load_dotenv() # development (API keys)

AVAILABLE_SOURCES = ['era5', 'ifs']

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--target-folder',
                    required=False, default='./data',
                    dest='target_folder',
                    help=('Destination output folder of the NetCDF4 files.The'
                          'files will be in a subfolder bearing the name of '
                          'the data source.'))
parser.add_argument('-s', '--data-source', required=False, default='era5',
                    help=('The database/algorithm to fetch from. '
                          f'Available options are: {', '.join(AVAILABLE_SOURCES)}.'))

args = parser.parse_args()

# Disable the internal logger of ECMWF, which causes duplicate logs.
logger = logging.getLogger(__name__)
logging.getLogger('ecmwf.datastores.legacy_client').propagate = False
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    force=True
)

target = os.path.join(args.target_folder, args.data_source)

logger.info(f'Fetching the latest data from {args.data_source} into the folder {target}')

if not os.path.exists(target):
    os.makedirs(target)
    
data_source = importlib.import_module(f'data_sources.{args.data_source}')
datetime = data_source.download_latest(target)
logger.info(f'Successfuly downloaded data from timestamp {datetime}')