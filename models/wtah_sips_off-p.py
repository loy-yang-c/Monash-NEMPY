# Dependent modules and functions
import os
import sqlite3
import pandas as pd
import gc
import pyarrow
from datetime import datetime
from pathlib import Path
from nempy import markets
from nempy.historical_inputs import loaders, mms_db, \
    xml_cache, units, demand, interconnectors, constraints, rhs_calculator
from nempy.help_functions.helper_functions import update_rhs_values
from scripts import nempy_utils
from joblib import Parallel, delayed


def interval_solve(interval, data_directory, mms_directory, MPC, MPF):

    print(interval)

    # Load data inside each pickled instance
    con = sqlite3.connect(mms_directory / 'market_management_system.db',
        timeout=60,
        check_same_thread=False)

    mms_db_manager = mms_db.DBManager(connection=con)
    xml_cache_manager = xml_cache.XMLCacheManager(data_directory / 'cache_directory')

    raw_inputs_loader = loaders.RawInputsLoader(
        nemde_xml_cache_manager=xml_cache_manager,
        market_management_system_database=mms_db_manager)

    # Begin solve
    raw_inputs_loader.set_interval(interval)
    unit_inputs = units.UnitData(raw_inputs_loader)
    interconnector_inputs = interconnectors.InterconnectorData(raw_inputs_loader)
    constraint_inputs = constraints.ConstraintData(raw_inputs_loader)
    demand_inputs = demand.DemandData(raw_inputs_loader)
    rhs_calculation_engine = rhs_calculator.RHSCalc(xml_cache_manager)

    unit_info = unit_inputs.get_unit_info()
    market = markets.SpotMarket(market_regions=['QLD1', 'NSW1', 'VIC1',
                                                'SA1', 'TAS1'],
                                unit_info=unit_info)
    
    # Pre-load generic constraints for updating
    generic_rhs = constraint_inputs.get_rhs_and_type_excluding_regional_fcas_constraints()
    
    # Update Constraints
    wtah_sips_constraints = []

    if len(rhs_calculation_engine.scada_data['S'].get('WTAH_SIPS_ONSTATUS', []))>0:
        rhs_calculation_engine.update_spd_id_value('WTAH_SIPS_ONSTATUS', 'S', '0')
        to_append = rhs_calculation_engine.get_rhs_constraint_equations_that_depend_value('WTAH_SIPS_ONSTATUS', 'S')
        wtah_sips_constraints = list(dict.fromkeys(wtah_sips_constraints + to_append))

    new_rhs_values = rhs_calculation_engine.compute_constraint_rhs(wtah_sips_constraints)
    generic_rhs = update_rhs_values(generic_rhs, new_rhs_values)

    # Set bids
    volume_bids, price_bids = unit_inputs.get_processed_bids()
    market.set_unit_volume_bids(volume_bids)
    market.set_unit_price_bids(price_bids)

    # Set bid in capacity limits
    unit_bid_limit = unit_inputs.get_unit_bid_availability()
    market.set_unit_bid_capacity_constraints(unit_bid_limit)
    cost = constraint_inputs.get_constraint_violation_prices()['unit_capacity']
    market.make_constraints_elastic('unit_bid_capacity', violation_cost=cost)

    # Set limits provided by the unconstrained intermittent generation forecasts. Primarily for wind and solar.
    unit_uigf_limit = unit_inputs.get_unit_uigf_limits()
    market.set_unconstrained_intermittent_generation_forecast_constraint(
        unit_uigf_limit)
    cost = constraint_inputs.get_constraint_violation_prices()['uigf']
    market.make_constraints_elastic('uigf_capacity', violation_cost=cost)

    ramp_rates = unit_inputs.get_bid_ramp_rates()
    scada_ramp_rates = unit_inputs.get_scada_ramp_rates(inlude_initial_output=True)
    initial_fast_start_profiles = unit_inputs.get_fast_start_profiles_for_dispatch()

    # Set unit ramp rates.
    def set_ramp_rates(run_type, fsp):
        if run_type == 'fast_start_first_run':
            fsp = fsp.loc[:, ['unit', 'current_mode']]
        else:
            fsp = fsp.loc[:, ['unit', 'end_mode', 'time_since_end_of_mode_two', 'min_loading']]
        cost = constraint_inputs.get_constraint_violation_prices()['ramp_rate']
        market.set_unit_ramp_rate_constraints(
            ramp_rates,
            scada_ramp_rates.loc[:, ['unit', 'scada_ramp_up_rate', 'scada_ramp_down_rate']],
            fsp,
            run_type=run_type, violation_cost=cost
        )
        cost = constraint_inputs.get_constraint_violation_prices()['fcas_profile']
        market.set_joint_ramping_constraints_reg(
            scada_ramp_rates, fsp, run_type=run_type, violation_cost=cost
        )

    set_ramp_rates('fast_start_first_run', initial_fast_start_profiles)

    # Set unit FCAS trapezium constraints.
    unit_inputs.add_fcas_trapezium_constraints()
    cost = constraint_inputs.get_constraint_violation_prices()['fcas_max_avail']
    fcas_availability = unit_inputs.get_fcas_max_availability()
    market.set_fcas_max_availability(fcas_availability, violation_cost=cost)
    cost = constraint_inputs.get_constraint_violation_prices()['fcas_profile']
    regulation_trapeziums = unit_inputs.get_fcas_regulation_trapeziums()
    market.set_energy_and_regulation_capacity_constraints(regulation_trapeziums, violation_cost=cost)
    contingency_trapeziums = unit_inputs.get_contingency_services()
    market.set_joint_capacity_constraints(contingency_trapeziums, violation_cost=cost)

    # Set interconnector definitions, limits and loss models.
    interconnectors_definitions = \
        interconnector_inputs.get_interconnector_definitions()
    loss_functions, interpolation_break_points = \
        interconnector_inputs.get_interconnector_loss_model()
    market.set_interconnectors(interconnectors_definitions)
    market.set_interconnector_losses(loss_functions,
                                        interpolation_break_points)

    # Calculate rhs constraint values that depend on the basslink frequency controller from scratch so there is
    # consistency between the basslink switch runs.
    # Find the constraints that need to be calculated because they depend on the frequency controller status.
    constraints_to_update = (
        rhs_calculation_engine.get_rhs_constraint_equations_that_depend_value('BL_FREQ_ONSTATUS', 'W'))
    initial_bl_freq_onstatus = rhs_calculation_engine.scada_data['W']['BL_FREQ_ONSTATUS'][0]['@Value']
    # Calculate new rhs values for the constraints that need updating.
    new_rhs_values = rhs_calculation_engine.compute_constraint_rhs(constraints_to_update)

    # Add generic constraints and FCAS market constraints.
    fcas_requirements = constraint_inputs.get_fcas_requirements()
    fcas_requirements = update_rhs_values(fcas_requirements, new_rhs_values)
    cost = constraint_inputs.get_violation_costs()
    market.set_fcas_requirements_constraints(fcas_requirements, violation_cost=cost)
    generic_rhs = update_rhs_values(generic_rhs, new_rhs_values)
    market.set_generic_constraints(generic_rhs, violation_cost=cost)

    unit_generic_lhs = constraint_inputs.get_unit_lhs()
    market.link_units_to_generic_constraints(unit_generic_lhs)
    interconnector_generic_lhs = constraint_inputs.get_interconnector_lhs()
    market.link_interconnectors_to_generic_constraints(
        interconnector_generic_lhs)

    # Set the operational demand to be met by dispatch.
    regional_demand = demand_inputs.get_operational_demand()
    cost = constraint_inputs.get_constraint_violation_prices()['regional_demand']
    market.set_demand_constraints(regional_demand, violation_cost=cost)

    # Set tiebreak constraint to equalise dispatch of equally priced bids.
    cost = constraint_inputs.get_constraint_violation_prices()['tiebreak']
    market.set_tie_break_constraints(cost)

    # Get unit dispatch without fast start constraints and use it to
    # make fast start unit commitment decisions.
    market.dispatch()
    dispatch = market.get_unit_dispatch()
    fast_start_profiles = unit_inputs.get_fast_start_profiles_for_dispatch(dispatch)
    set_ramp_rates('fast_start_second_run', fast_start_profiles)
    cost = constraint_inputs.get_constraint_violation_prices()['fast_start']
    cols = ['unit', 'end_mode', 'time_in_end_mode', 'mode_two_length',
            'mode_four_length', 'min_loading']
    fsp = fast_start_profiles.loc[:, cols]
    market.set_fast_start_constraints(fsp, violation_cost=cost)

    # First run of Basslink switch runs
    market.dispatch()  # First dispatch without allowing over constrained dispatch re-run to get objective function.
    objective_value_run_one = market.objective_value
    energy_ceiling_violation = (market.get_energy_prices()['price'].max() >= MPC) 
    energy_floor_violation = (market.get_energy_prices()['price'].min() <= MPF)
    fcas_ceiling_violation = (market.get_fcas_prices()['price'].max() >= MPC)
    if (energy_ceiling_violation | energy_floor_violation | fcas_ceiling_violation):
        market.dispatch(allow_over_constrained_dispatch_re_run=True,
                            energy_market_floor_price = MPF,
                            energy_market_ceiling_price = MPC,
                            fcas_market_ceiling_price = MPC)
    energy_prices_run_one = market.get_energy_prices()  # If this is the lowest cost run these will be the market prices.
    fcas_prices_run_one = market.get_fcas_prices()
    constraint_prices_run_one = market.get_generic_prices()
    unit_dispatch_run_one = market.get_unit_dispatch()


    # Re-run dispatch with Basslink Frequency controller off.
    # Set frequency controller to off in rhs calculations
    rhs_calculation_engine.update_spd_id_value('BL_FREQ_ONSTATUS', 'W', '0')
    new_bl_freq_onstatus = rhs_calculation_engine.scada_data['W']['BL_FREQ_ONSTATUS'][0]['@Value']
    # Find the constraints that need to be updated because they depend on the frequency controller status.
    constraints_to_update = (
        rhs_calculation_engine.get_rhs_constraint_equations_that_depend_value('BL_FREQ_ONSTATUS', 'W'))
    # Calculate new rhs values for the constraints that need updating.
    new_rhs_values = rhs_calculation_engine.compute_constraint_rhs(constraints_to_update)
    # Update the constraints in the market.
    fcas_requirements = update_rhs_values(fcas_requirements, new_rhs_values)
    cost = constraint_inputs.get_violation_costs()
    market.set_fcas_requirements_constraints(fcas_requirements, violation_cost=cost)
    generic_rhs = update_rhs_values(generic_rhs, new_rhs_values)
    market.set_generic_constraints(generic_rhs, violation_cost=cost)

    # Reset ramp rate constraints for first run of second Basslink switchrun
    set_ramp_rates('fast_start_first_run', initial_fast_start_profiles)

    # Get unit dispatch without fast start constraints and use it to
    # make fast start unit commitment decisions.
    market.remove_fast_start_constraints()
    market.dispatch()
    dispatch = market.get_unit_dispatch()
    fast_start_profiles = unit_inputs.get_fast_start_profiles_for_dispatch(dispatch)
    set_ramp_rates('fast_start_second_run', fast_start_profiles)
    cost = constraint_inputs.get_constraint_violation_prices()['fast_start']
    cols = ['unit', 'end_mode', 'time_in_end_mode', 'mode_two_length',
            'mode_four_length', 'min_loading']
    fsp = fast_start_profiles.loc[:, cols]
    market.set_fast_start_constraints(fsp, violation_cost=cost)

    market.dispatch()  # First dispatch without allowing over constrained dispatch re-run to get objective function.
    objective_value_run_two = market.objective_value
    energy_ceiling_violation = (market.get_energy_prices()['price'].max() >= MPC) 
    energy_floor_violation = (market.get_energy_prices()['price'].min() <= MPF)
    fcas_ceiling_violation = (market.get_fcas_prices()['price'].max() >= MPC)
    if (energy_ceiling_violation | energy_floor_violation | fcas_ceiling_violation):
        market.dispatch(allow_over_constrained_dispatch_re_run=True,
                            energy_market_floor_price = MPF,
                            energy_market_ceiling_price = MPC,
                            fcas_market_ceiling_price = MPC)
    energy_prices_run_two = market.get_energy_prices()  # If this is the lowest cost run these will be the market prices.
    fcas_prices_run_two = market.get_fcas_prices()
    constraint_prices_run_two = market.get_generic_prices()
    unit_dispatch_run_two = market.get_unit_dispatch()

    energy_prices_interval = energy_prices_run_one.merge(energy_prices_run_two, on = 'region').rename(columns = {'price_x': 'price_run1', 'price_y': 'price_run2'})
    fcas_prices_interval = fcas_prices_run_one.merge(fcas_prices_run_two, on = ['region', 'service']).rename(columns = {'price_x': 'price_run1', 'price_y': 'price_run2'})
    constraint_prices_interval = constraint_prices_run_one.merge(constraint_prices_run_two, on = ['set', 'type']).rename(columns = {'rhs_x': 'rhs_run1', 
                                                                                                                            'rhs_y': 'rhs_run2',
                                                                                                                            'slack_x': 'slack_run1', 
                                                                                                                            'slack_y': 'slack_run2',
                                                                                                                            'price_x': 'price_run1', 
                                                                                                                            'price_y': 'price_run2'})
    unit_dispatch_interval = unit_dispatch_run_one.merge(unit_dispatch_run_two, on = ['unit', 'dispatch_type', 'service']).rename(columns = {'dispatch_x': 'dispatch_run1', 
                                                                                                                                            'dispatch_y': 'dispatch_run2'})

    # The prices from the run with the lowest objective function value are used.
    if objective_value_run_one < objective_value_run_two:
        energy_prices_interval['price'] = energy_prices_interval['price_run1']
        fcas_prices_interval['price'] = fcas_prices_interval['price_run1']
        constraint_prices_interval['rhs'] = constraint_prices_interval['rhs_run1']
        constraint_prices_interval['slack'] = constraint_prices_interval['slack_run1']
        constraint_prices_interval['price'] = constraint_prices_interval['price_run1']
        unit_dispatch_interval['dispatch'] = unit_dispatch_interval['dispatch_run1']
        energy_prices_interval['interval'] = interval
        fcas_prices_interval['interval'] = interval
        constraint_prices_interval['interval'] = interval
        unit_dispatch_interval['interval'] = interval
    else:
        energy_prices_interval['price'] = energy_prices_interval['price_run2']
        fcas_prices_interval['price'] = fcas_prices_interval['price_run2']
        constraint_prices_interval['rhs'] = constraint_prices_interval['rhs_run2']
        constraint_prices_interval['slack'] = constraint_prices_interval['slack_run2']
        constraint_prices_interval['price'] = constraint_prices_interval['price_run2']
        unit_dispatch_interval['dispatch'] = unit_dispatch_interval['dispatch_run2']
        energy_prices_interval['interval'] = interval
        fcas_prices_interval['interval'] = interval
        constraint_prices_interval['interval'] = interval
        unit_dispatch_interval['interval'] = interval

        energy_prices_interval = energy_prices_interval.loc[:, ['interval', 'region', 'price']]
        fcas_prices_interval = fcas_prices_interval.loc[:, ['interval', 'region', 'service', 'price']]
        constraint_prices_interval = constraint_prices_interval.loc[:, ['interval', 'set', 'type', 'rhs', 'slack', 'price']]
        unit_dispatch_interval = unit_dispatch_interval.loc[:, ['interval', 'unit', 'dispatch_type', 'service', 'dispatch']]

    con.close()

    return energy_prices_interval, fcas_prices_interval, constraint_prices_interval, unit_dispatch_interval


def simulation(intervals, data_directory, mms_directory, results_dir, jobs, MPC, MPF, 
               chunk_size=288, run_label=None, chunk_start=0, skip_intervals=[]):

    unit_dispatch =  None

    # If no run label given, time-stamp the run so multiple runs don't clobber
    if run_label is None:
        run_label = datetime.now().strftime("run_%Y%m%d_%H%M%S")
 
    base = Path(results_dir) / run_label
    dirs = {
        "energy_prices":     base / "energy_prices",
        "fcas_prices":       base / "fcas_prices",
        "constraint_prices": base / "constraint_prices",
        "unit_dispatch":     base / "unit_dispatch",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
 
    n_chunks = (len(intervals) + chunk_size - 1) // chunk_size
    print(f"[simulation] {len(intervals)} intervals "
          f"-> {n_chunks} chunks of <= {chunk_size}, "
          f"writing to {base}")
 
    for chunk_idx in range(chunk_start, n_chunks):
        start = chunk_idx * chunk_size
        end = min(start + chunk_size, len(intervals))
        chunk_intervals = intervals[start:end]
        chunk_intervals = [int for int in chunk_intervals if int not in skip_intervals]
 
        print(f"[simulation] chunk {chunk_idx + 1}/{n_chunks} "
              f"({len(chunk_intervals)} intervals: "
              f"{chunk_intervals[0]} -> {chunk_intervals[-1]})")

        results = Parallel(n_jobs=jobs, backend="loky")(
            delayed(interval_solve)(interval, data_directory, mms_directory, MPC, MPF)
            for interval in chunk_intervals     
        )

        energy_chunks, fcas_chunks, constraint_chunks, unit_chunks = zip(*results)

        # Concat and write each data type, then drop the references
        # immediately so peak memory stays at one-chunk size.
        suffix = f"chunk_{chunk_idx:05d}.parquet"
 
        pd.concat(energy_chunks, ignore_index=True).to_parquet(
            dirs["energy_prices"] / suffix, index=False
        )
        del energy_chunks
 
        pd.concat(fcas_chunks, ignore_index=True).to_parquet(
            dirs["fcas_prices"] / suffix, index=False
        )
        del fcas_chunks
 
        pd.concat(constraint_chunks, ignore_index=True).to_parquet(
            dirs["constraint_prices"] / suffix, index=False
        )
        del constraint_chunks
 
        pd.concat(unit_chunks, ignore_index=True).to_parquet(
            dirs["unit_dispatch"] / suffix, index=False
        )
        del unit_chunks
 
        del results
        gc.collect()
    print(f"[simulation] done. Output: {base}")
    return dirs