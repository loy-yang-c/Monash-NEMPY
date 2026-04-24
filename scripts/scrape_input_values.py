### For NEMDE data that isn't housed in MMS, i.e. analog SPD_ID values
# Temporary cwd fix
import os
os.chdir(r"C:\Users\rahee\OneDrive\文档\Monash-NEMPY")

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
from joblib import Parallel, delayed

START_DATE = "2021-11-29" # yyyy-mm-dd format
END_DATE = "2022-02-01" # excluding

# Convert start and end dates to appropriate format
run_start_date = dt.datetime.strptime(START_DATE, "%Y-%m-%d").date()
run_end_date = dt.datetime.strptime(END_DATE, "%Y-%m-%d").date()

# A list of intervals we want to recreate historical dispatch for.
def get_test_intervals(number=1):
    start_time = dt.datetime(year=run_start_date.year, month=run_start_date.month, day=run_start_date.day, hour=0, minute=0)
    end_time = dt.datetime(year=run_end_date.year, month=run_end_date.month, day=run_end_date.day, hour=23, minute=55) - dt.timedelta(days=1)
    #difference = end_time - start_time
    #difference_in_5_min_intervals = int(difference.days * 12 * 24 + difference.seconds / 60 / 5)
    #random.seed(1)
    #intervals = random.sample(range(1, difference_in_5_min_intervals), number)
    #times = [start_time + dt.timedelta(minutes=5 * i) for i in intervals]
    #times_formatted = [t.isoformat().replace('T', ' ').replace('-', '/') for t in times]
    times = pd.date_range(start=start_time, end=end_time, freq="5min").strftime("%Y/%m/%d %H:%M:%S").tolist()
    times_formatted = times
    return times_formatted

# Inputs and outputs
intervals = get_test_intervals()


# Function to pull values
def pull_values(interval, spd_id):
    print(interval)

    # Load data inside each pickled instance
    cwd = Path(os.getcwd())
    con = sqlite3.connect(cwd / 'market_management_system.db',
        timeout=60,
        check_same_thread=False)

    mms_db_manager = mms_db.DBManager(connection=con)
    xml_cache_manager = xml_cache.XMLCacheManager(cwd / 'cache_directory')

    raw_inputs_loader = loaders.RawInputsLoader(
        nemde_xml_cache_manager=xml_cache_manager,
        market_management_system_database=mms_db_manager)
    
    raw_inputs_loader.set_interval(interval)
    rhs_calculation_engine = rhs_calculator.RHSCalc(xml_cache_manager)

    values = []
    key = []
    scada = rhs_calculation_engine.scada_data.get('E', {})

    for s in spd_id:
        value = scada.get(s)
        if value is not None:
            values.extend(value)
            key.append(s)
    
    if not values:
        return pd.DataFrame()

    output = pd.DataFrame({
        'spd_id' : key,
        'value' : [float(values[i]['@Value']) for i in range(0, len(values))]
    })

    output['interval'] = interval

    return output

input = ['VRAT15MT_DDSM1', 'VRAT15MT_DDSM2', 'VRAT15MT_DDMS1', 'VRAT15MT_DDMS2', 'VRAT15MT_EPTT',
         'VRAT5M_DDSM1', 'VRAT5M_DDSM2', 'VRAT5M_DDMS1', 'VRAT5M_DDMS2', 'VRAT15MT_EPTT',
         'VRAT5M_MSDD1', 'VRAT5M_MSDD2']

results = Parallel(n_jobs=-1, backend="loky")(
    delayed(pull_values)(interval, input)
    for interval in intervals
)

values = pd.concat(results, ignore_index=True)

output_path = Path("research/nemweb") / f"{'analog'}_{START_DATE}_{END_DATE}.csv"
values.to_csv(output_path)
