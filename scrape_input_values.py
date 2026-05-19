### For NEMDE data that isn't housed in MMS, i.e. analog SPD_ID values
from pathlib import Path
import os

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path(r"C:\Users\rahee\OneDrive\文档\Monash-NEMPY")

os.chdir(SCRIPT_DIR)

# Dependent modules and functions
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
import vars

# Convert start and end dates to appropriate format
run_start_date = dt.datetime.strptime(vars.START_DATE, "%Y-%m-%d").date()
run_end_date = dt.datetime.strptime(vars.END_DATE, "%Y-%m-%d").date()

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
def pull_values(interval, spd_id, spd_type):
    print(interval)

    # Load data inside each pickled instance
    cwd = Path(os.getcwd())
    con = sqlite3.connect(Path(vars.MMS_DB_PATH) / 'market_management_system.db',
        timeout=60,
        check_same_thread=False)

    mms_db_manager = mms_db.DBManager(connection=con)
    xml_cache_manager = xml_cache.XMLCacheManager(Path(vars.DATA_PATH) / 'cache_directory')

    raw_inputs_loader = loaders.RawInputsLoader(
        nemde_xml_cache_manager=xml_cache_manager,
        market_management_system_database=mms_db_manager)
    
    raw_inputs_loader.set_interval(interval)
    rhs_calculation_engine = rhs_calculator.RHSCalc(xml_cache_manager)

    values = []
    key = []

    for s, t in zip(spd_id, spd_type):
        scada = rhs_calculation_engine.scada_data.get(t, {})
        value = scada.get(s)
        if value is not None:
            values.extend(value)
            key.extend([s] * len(value))

    if not values:
        return pd.DataFrame()

    output = pd.DataFrame({
        'spd_id' : key,
        'value' : [float(v['@Value']) for v in values]
    })

    output['interval'] = interval

    return output

pairs = [
    ('VRAT15MT_DDSM1', 'A'),
    ('VRAT15MT_DDSM2', 'A'),
    ('VRAT15MT_DDMS1', 'A'),
    ('VRAT15MT_DDMS2', 'A'),
    ('VRAT15MT_EPTT',  'A'),
    ('VRAT5M_DDSM1',   'A'),
    ('VRAT5M_DDSM2',   'A'),
    ('VRAT5M_DDMS1',   'A'),
    ('VRAT5M_DDMS2',   'A'),
    ('VRAT5M_EPTT',    'A'),
    ('VRAT5M_MSDD1',   'A'),
    ('VRAT5M_MSDD2',   'A'),
    ('SIPS_MAIN_STAT', 'S'),
    ('SIPS_DDTS_MSS_STAT',   'S'),
    ('SIPS_IN_SERVICE_STAT',   'S'),
    ('WTAH_SIPS_AVAIL','A'),
    ('WTAH_SIPS_ONSTATUS',   'S'),
    ('WTAH_SIPS_84_ON', 'S'),
    ('WTAH_SIPS_85_ON', 'S'),
    ('WTAH_SIPS_88_ON', 'S'),
    ('WTAH_SIPS_86_ON', 'S'),
    ('WTAH_SIPS_8U_ON', 'S'),
    ('METZSF1.NMTZ1M',  'T'),
    ('METZSF_SIPS_STATUS', 'S'),
    ('SAPHWF1.NSAP1S',  'T'),
    ('SAPHWF1_SIPS_STATUS', 'S')
]

spd_ids, spd_types = zip(*pairs)

results = Parallel(n_jobs=vars.N_JOBS, backend="loky")(
    delayed(pull_values)(interval, spd_ids, spd_types)
    for interval in intervals
)

values = pd.concat(results, ignore_index=True)

output_path = Path(vars.RESULTS_PATH) / f"{'scrape'}_{START_DATE}_{END_DATE}.csv"
values.to_csv(output_path)