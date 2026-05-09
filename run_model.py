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
import random
import importlib.util as imp
from nempy.historical_inputs import mms_db, xml_cache
import vars

# Call referenced model script
model_name = vars.NEMPY_MODEL.replace(".py", "")
model_path = Path("models") / vars.NEMPY_MODEL

spec = imp.spec_from_file_location(model_name, model_path)
model = imp.module_from_spec(spec)
spec.loader.exec_module(model)

# Convert start and end dates to appropriate format
run_start_date = dt.datetime.strptime(vars.START_DATE, "%Y-%m-%d").date()
run_end_date = dt.datetime.strptime(vars.END_DATE, "%Y-%m-%d").date()

data_dir = Path(vars.DATA_PATH)
mms_db_dir = Path(vars.MMS_DB_PATH)
results_dir = Path(vars.RESULTS_PATH)

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

# Run model
run_label = f"{model_name}_{vars.START_DATE}_{vars.END_DATE}"
outputs = model.simulation(intervals, data_dir, mms_db_dir, results_dir, vars.N_JOBS,
                            vars.MPC, vars.MPF, run_label=run_label, chunk_start = vars.CHUNK_START)

# simulation() now writes Parquet files directly to disk in chunks.
# `outputs` is a dict mapping data-type name -> directory of chunk files.
print("Output written to:")
for name, path in outputs.items():
    print(f"  {name}: {path}")