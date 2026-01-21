# Dependent modules and functions
import os
import sqlite3
import pandas as pd
from pathlib import Path
from nempy import markets
from nempy.historical_inputs import loaders, mms_db, \
    xml_cache, units, demand, interconnectors, constraints, rhs_calculator
from nempy.help_functions.helper_functions import update_rhs_values
from scripts import nempy_utils

# Load data
cwd = Path(os.getcwd())
con = sqlite3.connect(cwd / "market_management_system.db")

mms_db_manager = mms_db.DBManager(connection=con)
xml_cache_manager = xml_cache.XMLCacheManager(cwd / "cache_directory")

raw_inputs_loader = loaders.RawInputsLoader(
    nemde_xml_cache_manager=xml_cache_manager,
    market_management_system_database=mms_db_manager)

xml_cache_manager.load_interval(interval)
xml_cache_manager.get_constraint_rhs()
xml_cache_manager.get_constraint_interconnector_lhs()['interconnector'].unique()
xml_cache_manager.get_constraint_interconnector_lhs().query("interconnector == 'VIC1-NSW1'")[['set', 'coefficient']]