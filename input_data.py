from pathlib import Path
import os

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path(r"C:\Users\rahee\OneDrive\文档\Monash-NEMPY")

os.chdir(SCRIPT_DIR)

import sqlite3
import pandas as pd
import datetime as dt
import importlib.util as imp
from nempy.historical_inputs import mms_db, xml_cache
import vars

# Convert start and end dates to appropriate format
run_start_date = dt.datetime.strptime(vars.START_DATE, "%Y-%m-%d").date()
run_end_date = dt.datetime.strptime(vars.END_DATE, "%Y-%m-%d").date()

data_dir = Path(vars.DATA_PATH)
mms_db_dir = Path(vars.MMS_DB_WRITE_PATH)

# Scrape data
con = sqlite3.connect(mms_db_dir / f"market_management_system_{vars.MMS_DB_WRITE_APNDX}.db")

mms_db_manager = mms_db.DBManager(connection=con)
xml_cache_manager = xml_cache.XMLCacheManager(data_dir / "cache_directory")

mms_db_manager.populate(start_year=run_start_date.year, start_month=run_start_date.month,
                        end_year=run_end_date.year, end_month=run_end_date.month)

xml_cache_manager.populate_by_day(start_year=run_start_date.year, start_month=run_start_date.month, start_day=run_start_date.day,
                        end_year=run_end_date.year, end_month=run_end_date.month, end_day=run_end_date.day)
