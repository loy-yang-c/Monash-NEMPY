### Scrape constraint violation penalties (CVPs) from the NEMDE XML cache
###
### Writes two chunked Parquet datasets:
###   <RESULTS_PATH>/cvp_<START>_<END>/generic/  one row per (interval, constraint)
###   <RESULTS_PATH>/cvp_<START>_<END>/case/     one row per interval, group-level prices
###
### Read back in R with arrow::open_dataset() on either directory.

from pathlib import Path
import os

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path(r"C:\Users\rahee\OneDrive\文档\Monash-NEMPY")

os.chdir(SCRIPT_DIR)

import datetime as dt
import traceback

import pandas as pd
from joblib import Parallel, delayed
from nempy.historical_inputs import xml_cache

import vars

# Intervals per chunk -> one Parquet file per chunk. Override in vars if you want.
CHUNK_SIZE = getattr(vars, "CHUNK_SIZE", 288)

run_start_date = dt.datetime.strptime(vars.START_DATE, "%Y-%m-%d").date()
run_end_date = dt.datetime.strptime(vars.END_DATE, "%Y-%m-%d").date()


def get_test_intervals():
    start_time = dt.datetime(year=run_start_date.year, month=run_start_date.month,
                             day=run_start_date.day, hour=0, minute=0)
    end_time = dt.datetime(year=run_end_date.year, month=run_end_date.month,
                           day=run_end_date.day, hour=23, minute=55) - dt.timedelta(days=1)
    return pd.date_range(start=start_time, end=end_time,
                         freq="5min").strftime("%Y/%m/%d %H:%M:%S").tolist()


intervals = get_test_intervals()

skip_intervals = list(vars.SKIP_INTERVALS)
for i in range(len(vars.SKIP_RANGE_START)):
    times = pd.date_range(start=vars.SKIP_RANGE_START[i], end=vars.SKIP_RANGE_END[i],
                          freq="5min").strftime("%Y/%m/%d %H:%M:%S").tolist()
    skip_intervals.extend(times)

skip_intervals = set(skip_intervals)
intervals = [i for i in intervals if i not in skip_intervals]

OUT_ROOT = Path(vars.RESULTS_PATH)
GENERIC_DIR = OUT_ROOT / "generic"
CASE_DIR = OUT_ROOT / "case"
GENERIC_DIR.mkdir(parents=True, exist_ok=True)
CASE_DIR.mkdir(parents=True, exist_ok=True)


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def pull_chunk(interval_chunk):
    """Pull CVPs for one chunk of intervals and write a Parquet file per dataset.

    Returns (chunk_tag, n_intervals_ok, [(interval, error), ...]).
    """
    chunk_tag = interval_chunk[0].replace("/", "").replace(" ", "_").replace(":", "")
    print(chunk_tag, flush=True)

    # Only the XML cache is needed for CVPs - no MMS connection, no market build.
    xml_cache_manager = xml_cache.XMLCacheManager(Path(vars.DATA_PATH) / 'cache_directory')

    generic_frames = []
    case_rows = []
    failures = []

    for interval in interval_chunk:
        try:
            xml_cache_manager.load_interval(interval)

            # Per-constraint penalties: set, type ('LE'/'GE'/'EQ'), cost ($/MWh).
            # cost is the CVP factor x VoLL, so it moves with VoLL across the sample.
            generic = xml_cache_manager.get_constraint_type()
            generic = generic.loc[:, ['set', 'type', 'cost']].copy()
            generic['interval'] = interval
            generic_frames.append(generic)

            # Group-level prices, including regional_demand (energy deficit) and voll.
            case = dict(xml_cache_manager.get_constraint_violation_prices())
            case['interval'] = interval
            case_rows.append(case)

        except Exception:
            failures.append((interval, traceback.format_exc(limit=1).strip()))

    if generic_frames:
        generic_out = pd.concat(generic_frames, ignore_index=True)
        generic_out['interval'] = pd.to_datetime(generic_out['interval'],
                                                 format="%Y/%m/%d %H:%M:%S")
        generic_out['set'] = generic_out['set'].astype('category')
        generic_out['type'] = generic_out['type'].astype('category')
        generic_out = generic_out.loc[:, ['interval', 'set', 'type', 'cost']]
        generic_out.to_parquet(GENERIC_DIR / f"{chunk_tag}.parquet",
                               engine='pyarrow', compression='zstd', index=False)

    if case_rows:
        case_out = pd.DataFrame(case_rows)
        case_out['interval'] = pd.to_datetime(case_out['interval'],
                                              format="%Y/%m/%d %H:%M:%S")
        cols = ['interval'] + [c for c in case_out.columns if c != 'interval']
        case_out.loc[:, cols].to_parquet(CASE_DIR / f"{chunk_tag}.parquet",
                                         engine='pyarrow', compression='zstd', index=False)

    return chunk_tag, len(interval_chunk) - len(failures), failures


results = Parallel(n_jobs=vars.N_JOBS, backend="loky")(
    delayed(pull_chunk)(chunk) for chunk in chunks(intervals, CHUNK_SIZE)
)