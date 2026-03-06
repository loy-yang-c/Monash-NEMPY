# Dependent modules and functions
import os
import sqlite3
import pandas as pd
import datetime as dt
from pathlib import Path
from nempy import markets
from nempy.historical_inputs import loaders, mms_db, \
    xml_cache, units, demand, interconnectors, constraints, rhs_calculator
from nempy.help_functions.helper_functions import update_rhs_values
from scripts import nempy_utils

interval = dt.datetime(year=2022, month=1, day=1, hour=16, minute=0, second=0)
interval = interval.strftime("%Y/%m/%d %H:%M:%S")

# Load data
cwd = Path(os.getcwd())
con = sqlite3.connect(cwd / "market_management_system.db")

mms_db_manager = mms_db.DBManager(connection=con)
xml_cache_manager = xml_cache.XMLCacheManager(cwd / "cache_directory")

raw_inputs_loader = loaders.RawInputsLoader(
    nemde_xml_cache_manager=xml_cache_manager,
    market_management_system_database=mms_db_manager)

#xml_cache_manager.load_interval(interval)
#xml_cache_manager.get_constraint_rhs()
#xml_cache_manager.get_constraint_interconnector_lhs()['interconnector'].unique()
#xml_cache_manager.get_constraint_interconnector_lhs().query("interconnector == 'VIC1-NSW1'")[['set', 'coefficient']]

raw_inputs_loader.set_interval(interval)
rhs_calculation_engine = rhs_calculator.RHSCalc(xml_cache_manager)

rhs_calculation_engine.inputs
rhs_calculation_engine.entered_values
rhs_calculation_engine.scada_data.keys()
rhs_calculation_engine.scada_data['S']['SIPS_MAIN_STAT']
rhs_calculation_engine.get_rhs_constraint_equations_that_depend_value('SIPS_MAIN_STAT', 'S')
rhs_calculation_engine.get_rhs_constraint_equations_that_depend_value('SIPS_5M_STAT', 'S')
rhs_calculation_engine.get_rhs_constraint_equations_that_depend_value('SIPS_IN_SERVICE_STAT', 'S')

for scada_type_set in rhs_calculation_engine.scada_data:
    print(f"{scada_type_set}")