# semi-perfect foresight battery trader (ignoring deg, RTE, double reg)

import gurobipy as gb
from gurobipy import GRB
import pandas as pd
import numpy as np
import datetime

print("Gurobi version:", gb.gurobi.version())

# prices
master = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/p5min_regionsolution.csv')
master['latest'] = master.groupby('INTERVAL_DATETIME')['RUN_DATETIME'].transform('max')
master = master.loc[master['RUN_DATETIME'] == master['latest']]
indx = master.loc[:, ['INTERVAL_DATETIME']]

# elasticity prices
master_elasticity = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/p5min_pricesensitivities.csv')
master_elasticity['latest'] = master_elasticity.groupby('INTERVAL_DATETIME')['RUN_DATETIME'].transform('max')
master_elasticity = master_elasticity.loc[(master_elasticity['RUN_DATETIME'] == master_elasticity['latest']) & (master_elasticity['INTERVENTION'] == 0)]
# scale price changes for 250MW decrease in system load (RRP5)
prices = pd.merge(master.drop(columns=['latest']), 
                  master_elasticity.drop(columns=['LASTCHANGED', 'latest']), 
                  on = ['RUN_DATETIME', 'REGIONID', 'INTERVAL_DATETIME'])

prices['RRP5_adj'] = prices['RRP5'] - (prices['RRP'] - prices['RRP5'])*250/150
prices['INTERVAL_DATETIME'] = pd.to_datetime(prices['INTERVAL_DATETIME'])

# existing load
dispatchload = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/research/nemweb/dispatchload.csv').sort_values(by = ['SETTLEMENTDATE', 'DUID'])
unit_commitments = dispatchload.loc[dispatchload['DUID'].isin(['VBBG1', 'VBB1']), ['SETTLEMENTDATE', 'INTERVENTION', 'TOTALCLEARED']]
unit_commitments['wholesale_dispatch'] = np.maximum(unit_commitments['TOTALCLEARED'], 0)
unit_commitments = unit_commitments.loc[:, ['SETTLEMENTDATE', 'INTERVENTION', 'wholesale_dispatch']].groupby(['SETTLEMENTDATE', 'INTERVENTION']).agg(wholesale_dispatch = ('wholesale_dispatch', 'sum'))

to_join = dispatchload.loc[dispatchload['DUID'].isin(['VBBL1', 'VBB1']), ['SETTLEMENTDATE', 'DUID', 'INTERVENTION', 'TOTALCLEARED']]
conditions = [(to_join['DUID'] == 'VBBL1'),
              (to_join['DUID'] == 'VBB1')]
outcomes = [to_join['TOTALCLEARED']*-1, to_join['TOTALCLEARED']]
to_join['wholesale_charge'] = np.select(conditions, outcomes)
to_join['wholesale_charge'] = np.minimum(to_join['wholesale_charge'], 0)
to_join['wholesale_charge'] = np.abs(to_join['wholesale_charge'])
to_join = to_join.loc[:, ['SETTLEMENTDATE', 'INTERVENTION', 'wholesale_charge']].groupby(['SETTLEMENTDATE', 'INTERVENTION']).agg(wholesale_charge = ('wholesale_charge', 'sum'))

unit_commitments = pd.merge(unit_commitments, to_join, on = ['SETTLEMENTDATE', 'INTERVENTION'])

to_join = dispatchload.loc[:, ['SETTLEMENTDATE', 'INTERVENTION', 'RAISEREG', 'LOWERREG']].groupby(['SETTLEMENTDATE', 'INTERVENTION']).agg(raisereg = ('RAISEREG', 'sum'),
                                                                                                                                          lowerreg = ('LOWERREG', 'sum'))

unit_commitments = pd.merge(unit_commitments, to_join, on = ['SETTLEMENTDATE', 'INTERVENTION'])
unit_commitments = unit_commitments.reset_index()
unit_commitments['intervention_flag'] = unit_commitments.groupby('SETTLEMENTDATE')['INTERVENTION'].transform('max')
unit_commitments = unit_commitments.loc[unit_commitments['INTERVENTION'] == unit_commitments['intervention_flag']].drop(columns=['INTERVENTION', 'intervention_flag'])
unit_commitments = unit_commitments.reset_index()
unit_commitments['SETTLEMENTDATE'] = pd.to_datetime(unit_commitments['SETTLEMENTDATE'])

#variables
start_datetime = datetime.datetime(2021, 12, 8, 4, 0)
end_datetime = datetime.datetime(2022, 4, 1, 3, 55)
intervals = end_datetime - start_datetime
intervals = intervals.total_seconds()/60/5
intervals = int(intervals)
T = range(0, intervals)
dt = 1/12
P_min = 0
P_max = 250
E_min = 0
E_max = 250
cycles_day = 1
rreg_util = 0.21
lreg_util = 0.09

# create input dataframe with time indexing
input_data = pd.DataFrame({'DateTime' : pd.date_range(start = start_datetime, end=end_datetime, freq='5min')})
input_data = pd.merge(input_data, prices.loc[:, ['INTERVAL_DATETIME', 'RRP', 'RRP4', 'RRP5_adj', 'RRP6']], 
                                             left_on = 'DateTime', right_on = 'INTERVAL_DATETIME', how = 'left')
input_data = input_data.drop(columns = ['INTERVAL_DATETIME'])

input_data = pd.merge(input_data, unit_commitments, left_on = 'DateTime', right_on = 'SETTLEMENTDATE', how = 'left')
input_data = input_data.drop(columns = ['SETTLEMENTDATE', 'index'])

# create variable that blocks capacity
conditions = [(input_data['wholesale_dispatch'] == 0),
              (input_data['wholesale_dispatch'] > 0)]
outcomes = [250, np.minimum(input_data['wholesale_dispatch'] + input_data['raisereg'], 250)]
input_data['dispatch'] = np.select(conditions, outcomes)

conditions = [(input_data['wholesale_charge'] == 0),
              (input_data['wholesale_charge'] > 0)]
outcomes = [250, np.minimum(input_data['wholesale_charge'] + input_data['lowerreg'], 250)]
input_data['charge'] = np.select(conditions, outcomes)

# elasticity breakpoints and variables
d_q_bp = {
    t: [0.0, 250.0] for t in T
}
l_q_bp = {
    t: [0.0, 150.0, 300] for t in T
}
d_p_bp = {
    t: [input_data['RRP'][t], input_data['RRP5_adj'][t]] for t in T
}
l_p_bp = {
    t: [input_data['RRP'][t], input_data['RRP4'][t], input_data['RRP6'][t]] for t in T
}

def monotonic_prices(p, direction="decreasing"):

    if direction != "decreasing" and direction != "increasing":
        raise ValueError("p direction argument must take 'increasing' or 'decreasing' in q")

    p_bounded = [p[0]]

    if direction=="decreasing":
        for i in range(1, len(p)):
            p_bounded.append(min(p[i], p_bounded[i-1]))
    
    if direction=="increasing":
        for i in range(1, len(p)):
            p_bounded.append(max(p[i], p_bounded[i-1]))

    return p_bounded

d_p_bp_monotonic = {
    t: monotonic_prices(d_p_bp[t]) for t in T
}

l_p_bp_monotonic = {
    t: monotonic_prices(l_p_bp[t], direction="increasing") for t in T
}

def pw_integral(q, p):
    q = [float(x) for x in q]
    p = [float(x) for x in p]

    if len(q) != len(p):
        raise ValueError(f"q and p length mismatch: {len(q)} vs {len(p)}")

    if len(q) < 2:
        raise ValueError(f"Need at least 2 breakpoints, got {len(q)}")

    rev = [0.0]
    for i in range(1, len(q)):
        area = 0.5 * (p[i] + p[i-1]) * (q[i] - q[i-1])
        rev.append(rev[-1] + area)
    return rev

rev_d_bp = {
    t: pw_integral(d_q_bp[t], d_p_bp_monotonic[t]) for t in T
}
rev_l_bp = {
    t: pw_integral(l_q_bp[t], l_p_bp_monotonic[t]) for t in T
}

K_d = range(0, len(d_q_bp[1]))
K_l = range(0, len(l_q_bp[1]))

# create model object
m = gb.Model()

# standard decison variables
d = m.addVars(T, lb=P_min, ub=P_max, vtype=GRB.CONTINUOUS, name='dispatch')
l = m.addVars(T, lb=P_min, ub=P_max, vtype=GRB.CONTINUOUS, name='load')
s = m.addVars(T, lb=E_min, ub=E_max, vtype=GRB.CONTINUOUS, name='soc')
throughput_d = m.addVars(T, lb=0, ub=P_max, vtype=GRB.CONTINUOUS, name='throughput_d')
throughput_l = m.addVars(T, lb=0, ub=P_max, vtype=GRB.CONTINUOUS, name='throughput_l')

# decision variables for elasticity
lam_d = m.addVars(T, K_d, lb=0, name="lambda_dispatch")
lam_l = m.addVars(T, K_l, lb=0, name="lambda_load")
R_d = m.addVars(T, name="revenue_dispatch")
C_l = m.addVars(T, name="cost_charge")

# objective
m.setObjective(
    gb.quicksum((R_d[t] - C_l[t]) * dt
                 for t in T),
    GRB.MAXIMIZE
)

# init
m.addConstr(s[0] == E_max/2 + (l[0] + input_data['wholesale_charge'][0] + input_data['lowerreg'][0] * lreg_util) * dt 
            - (d[0] + input_data['wholesale_dispatch'][0] + input_data['raisereg'][0] * rreg_util) * dt)
m.addConstr((d[0] + input_data['wholesale_dispatch'][0] + input_data['raisereg'][0]) * dt <= E_max/2)
m.addConstr((l[0] + input_data['wholesale_charge'][0] + input_data['lowerreg'][0]) * dt <= E_max - E_max/2)

# soc
for t in T:
    if t > 0:
        m.addConstr(
            s[t] == s[t-1] + 
            (l[t] + input_data['wholesale_charge'][0] + input_data['lowerreg'][0] * lreg_util) * dt - 
            (d[t] + input_data['wholesale_dispatch'][0] + input_data['raisereg'][0] * rreg_util) * dt
        )

# dispatch, load and as energy
for t in T:
    if t > 0:
        m.addConstr((d[t] + input_data['wholesale_dispatch'][t] + input_data['raisereg'][t]) * dt <= s[t-1])
        m.addConstr((l[t] + input_data['wholesale_charge'][t] + input_data['lowerreg'][t]) * dt <= E_max - s[t-1])

# dispatch and as capacity
for t in T:
    if t >= 0:
        m.addConstr((d[t] + input_data['dispatch'][t]) <= P_max)

# load and as capacity
for t in T:
    if t >= 0:
        m.addConstr((l[t] + input_data['charge'][t]) <= P_max)

# cycle limit
for t in T:
    if t >= 0:
        m.addConstr(throughput_d[t] >= input_data['raisereg'][t] * rreg_util * dt)
        m.addConstr(throughput_d[t] >= (d[t] + input_data['wholesale_dispatch'][t] + input_data['raisereg'][t] * rreg_util - input_data['lowerreg'][t] * lreg_util) * dt)
        m.addConstr(throughput_l[t] >= input_data['lowerreg'][t] * lreg_util * dt)
        m.addConstr(throughput_l[t] >= (l[t] + input_data['wholesale_charge'][t] + input_data['lowerreg'][t] * lreg_util - input_data['raisereg'][t] * rreg_util) * dt)

m.addConstr(gb.quicksum(throughput_d[t] for t in T) <= 
            E_max * cycles_day * intervals * dt / 24)
m.addConstr(gb.quicksum(throughput_l[t] for t in T) <= 
            E_max * cycles_day * intervals * dt / 24)

# elasticity
for t in T:
    if t >= 0:
        m.addConstr(gb.quicksum(lam_d[t,k] for k in K_d) == 1)
        m.addConstr(gb.quicksum(lam_l[t,k] for k in K_l) == 1)
        m.addSOS(GRB.SOS_TYPE2, [lam_d[t,k] for k in K_d])
        m.addSOS(GRB.SOS_TYPE2, [lam_l[t,k] for k in K_l])

for t in T:
    if t >= 0:
        #m.addGenConstrPWL(d[t], R_d[t], d_q_bp[t], rev_d_bp[t], name=f"dispatch_revenue_pwl_{t}")
        #m.addGenConstrPWL(l[t], C_l[t], l_q_bp[t], rev_l_bp[t], name=f"load_cost_pwl_{t}")
        m.addConstr(d[t] == gb.quicksum(lam_d[t,k] * d_q_bp[t][k] for k in K_d))
        m.addConstr(l[t] == gb.quicksum(lam_l[t,k] * l_q_bp[t][k] for k in K_l))
        m.addConstr(R_d[t] == gb.quicksum(lam_d[t,k] * rev_d_bp[t][k] for k in K_d))
        m.addConstr(C_l[t] == gb.quicksum(lam_l[t,k] * rev_l_bp[t][k] for k in K_l))

# view model
m.write("model.lp")

m.optimize()

if m.status != GRB.OPTIMAL:
    raise RuntimeError(f"Model did not solve optimally (status={m.status})")

results = pd.DataFrame({
    "interval": master.loc[master['region'] == 'VIC1','interval'],
    "ws_price": rop,
    "ws_price_p1": rop_p1,
    "ws_price_p2": rop_p2,
    "ws_price_p3": rop_p3,
    "ws_price_p4": rop_p4,
    "ws_price_p5": rop_p5,
    "ws_price_n1": rop_n1,
    "ws_price_n2": rop_n2,
    "ws_price_n3": rop_n3,
    "ws_price_n4": rop_n4,
    "ws_price_n5": rop_n5,
    "ws_discharge": [d[t].X for t in T],
    "ws_charge": [l[t].X for t in T],
    "soc": [s[t].X for t in T],
    "R_d": [R_d[t].X for t in T],
    "C_l": [C_l[t].X for t in T],
    "lambda_d0": [lam_d[t,0].X for t in T],
    "lambda_d1": [lam_d[t,1].X for t in T],
    "lambda_d2": [lam_d[t,2].X for t in T],
    "lambda_d3": [lam_d[t,3].X for t in T],
    "lambda_d4": [lam_d[t,4].X for t in T],
    "lambda_d5": [lam_d[t,5].X for t in T],
    "lambda_c0": [lam_l[t,0].X for t in T],
    "lambda_c1": [lam_l[t,1].X for t in T],
    "lambda_c2": [lam_l[t,2].X for t in T],
    "lambda_c3": [lam_l[t,3].X for t in T],
    "lambda_c4": [lam_l[t,4].X for t in T],
    "lambda_c5": [lam_l[t,5].X for t in T]
})

results.to_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/lambda_pwl_energy_only_elasticity.csv')