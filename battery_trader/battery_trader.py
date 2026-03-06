import gurobipy as gb
from gurobipy import GRB
import pandas as pd

m = gb.Model()
print("Gurobi version:", gb.gurobi.version())

# semi-perfect foresight battery trader (ignoring deg, RTE, double reg, elasticity)
master = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel_energy_2021-11-29_2022-01-01.csv')
rop = master.loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)

ancillary = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel_fcas_2021-11-29_2022-01-01.csv')
rreg = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "raise_reg"), 'price'].to_numpy(dtype=float)
lreg = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "lower_reg"), 'price'].to_numpy(dtype=float)
r6 = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "raise_6s"), 'price'].to_numpy(dtype=float)
r60 = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "raise_60s"), 'price'].to_numpy(dtype=float)
r5 = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "raise_5min"), 'price'].to_numpy(dtype=float)
l6 = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "lower_6s"), 'price'].to_numpy(dtype=float)
l60 = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "lower_60s"), 'price'].to_numpy(dtype=float)
l5 = ancillary.loc[(ancillary['region'] == 'VIC1') & (ancillary['service'] == "lower_5min"), 'price'].to_numpy(dtype=float)

intervals = len(rop)
T = range(0, intervals)
dt = 1/12
P_min = 0
P_max = 250
hrs = 1.5
E_min = 0
E_max = P_max * hrs
cycles_day = 1
rreg_util = 0.18
lreg_util = 0.08

# decison variables
d = m.addVars(T, lb=P_min, ub=P_max, vtype=GRB.CONTINUOUS, name='dispatch')
l = m.addVars(T, lb=P_min, ub=P_max, vtype=GRB.CONTINUOUS, name='load')
s = m.addVars(T, lb=E_min, ub=E_max, vtype=GRB.CONTINUOUS, name='soc')
c_rr = m.addVars(T, lb=0, ub=P_max, vtype=GRB.CONTINUOUS, name='capacity_rr')
c_lr = m.addVars(T, lb=0, ub=P_max, vtype=GRB.CONTINUOUS, name='capacity_lr')
d_rr = m.addVars(T, lb=0, ub=P_max*rreg_util, vtype=GRB.CONTINUOUS, name='dispatch_rr')
d_lr = m.addVars(T, lb=0, ub=P_max*lreg_util, vtype=GRB.CONTINUOUS, name='dispatch_lr')
c_r6 = m.addVars(T, lb=0, ub=P_max*0.41, vtype=GRB.CONTINUOUS, name='capacity_r6')
c_r60 = m.addVars(T, lb=0, ub=P_max*0.41, vtype=GRB.CONTINUOUS, name='capacity_r60')
c_r5 = m.addVars(T, lb=0, ub=P_max*0.41, vtype=GRB.CONTINUOUS, name='capacity_r5')
c_l6 = m.addVars(T, lb=0, ub=P_max*0.41, vtype=GRB.CONTINUOUS, name='capacity_l6')
c_l60 = m.addVars(T, lb=0, ub=P_max*0.41, vtype=GRB.CONTINUOUS, name='capacity_l60')
c_l5 = m.addVars(T, lb=0, ub=P_max*0.41, vtype=GRB.CONTINUOUS, name='capacity_l5')
throughput_d = m.addVars(T, lb=0, ub=P_max, vtype=GRB.CONTINUOUS, name='throughput_d')
throughput_l = m.addVars(T, lb=0, ub=P_max, vtype=GRB.CONTINUOUS, name='throughput_l')


# objective
m.setObjective(
    gb.quicksum(rop[t] * (d[t] + d_rr[t] * rreg_util - l[t] - d_lr[t] * lreg_util) * dt + 
                (c_rr[t] * rreg[t] + c_lr[t] * lreg[t] + c_r6[t] * r6[t] + c_r60[t] * r60[t] + c_r5[t] * r5[t]
                  + c_l6[t] * l6[t] + c_l60[t] * l60[t] + c_l5[t] * l5[t]) * dt
                 for t in T),
    GRB.MAXIMIZE
)

# init
m.addConstr(s[0] == E_max/2 + (l[0] + d_lr[0]) * dt - (d[0] + d_rr[0]) * dt)
m.addConstr((d[0] + d_rr[0]) * dt + c_r6[0]/3600 * (0.5 * 5 + 0.5 * 54) + c_r60[0]/3600 * (0.5 * 54 + 0.5 * 240) + c_r5[0]/3600 * (0.5 * 240 + 300) <= E_max/2)
m.addConstr((l[0] + d_lr[0]) * dt + c_l6[0]/3600 * (0.5 * 5 + 0.5 * 54) + c_l60[0]/3600 * (0.5 * 54 + 0.5 * 240) + c_l5[0]/3600 * (0.5 * 240 + 300) <= E_max - E_max/2)

# soc
for t in T:
    if t > 0:
        m.addConstr(
            s[t] == s[t-1] + l[t] * dt - d[t] * dt +
            d_lr[t] * dt * lreg_util - d_rr[t] * dt * rreg_util
        )

# dispatch, load and as energy
for t in T:
    if t > 0:
        m.addConstr((d[t] + c_rr[t]) * dt + c_r6[t]/3600 * (0.5 * 5 + 0.5 * 54) + c_r60[t]/3600 * (0.5 * 54 + 0.5 * 240) + c_r5[t]/3600 * (0.5 * 240 + 300) <= s[t-1])
        m.addConstr((l[t] + c_lr[t]) * dt + c_l6[t]/3600 * (0.5 * 5 + 0.5 * 54) + c_l60[t]/3600 * (0.5 * 54 + 0.5 * 240) + c_l5[t]/3600 * (0.5 * 240 + 300) <= E_max - s[t-1])
    if t >= 0:
        m.addConstr(d_rr[t] == c_rr[t])
        m.addConstr(d_lr[t] == c_lr[t])

# dispatch and as capacity
for t in T:
    if t >= 0:
        m.addConstr((d[t] + c_rr[t] + c_r6[t] - l[t] <= P_max))
for t in T:
    if t >= 0:
        m.addConstr((d[t] + c_rr[t] + c_r60[t] - l[t] <= P_max))
for t in T:
    if t >= 0:
        m.addConstr((d[t] + c_rr[t] + c_r5[t] - l[t] <= P_max))

# load and as capacity
for t in T:
    if t >= 0:
        m.addConstr((l[t] + c_lr[t] + c_l6[t] - d[t] <= P_max))
for t in T:
    if t >= 0:
        m.addConstr((l[t] + c_lr[t] + c_l60[t] - d[t] <= P_max))
for t in T:
    if t >= 0:
        m.addConstr((l[t] + c_lr[t] + c_l5[t] - d[t] <= P_max))

# cycle limit
for t in T:
    if t >= 0:
        m.addConstr(throughput_d[t] >= d_rr[t] * dt)
        m.addConstr(throughput_d[t] >= (d_rr[t] + d[t] - d_lr[t] * lreg_util) * dt)
        m.addConstr(throughput_l[t] >= d_lr[t] * dt)
        m.addConstr(throughput_l[t] >= (d_lr[t] + l[t] - d_rr[t] * rreg_util) * dt)

m.addConstr(gb.quicksum(throughput_d[t] for t in T) <= 
            E_max * cycles_day * intervals * dt / 24)
m.addConstr(gb.quicksum(throughput_l[t] for t in T) <= 
            E_max * cycles_day * intervals * dt / 24)

# view model
m.write("model.lp")

m.optimize()

if m.status != GRB.OPTIMAL:
    raise RuntimeError(f"Model did not solve optimally (status={m.status})")

results = pd.DataFrame({
    "interval": master.loc[master['region'] == 'VIC1','interval'],
    "ws_price": rop,
    "rreg_price": rreg,
    "lreg_price": lreg,
    "r6_price": r6,
    "r60_price": r60,
    "r5_price": r5,
    "l6_price": l6,
    "l60_price": l60,
    "l5_price": l5,
    "ws_discharge": [d[t].X for t in T],
    "ws_charge": [l[t].X for t in T],
    "rreg_capacity": [c_rr[t].X for t in T],
    "rreg_discharge": [d_rr[t].X for t in T],
    "lreg_capacity": [c_lr[t].X for t in T],
    "lreg_charge": [d_lr[t].X for t in T],
    "r6_capacity": [c_r6[t].X for t in T],
    "r60_capacity": [c_r60[t].X for t in T],
    "r5_capacity": [c_r5[t].X for t in T],
    "l6_capacity": [c_l6[t].X for t in T],
    "l60_capacity": [c_l60[t].X for t in T],
    "l5_capacity": [c_l5[t].X for t in T],
    "soc": [s[t].X for t in T]
})

results.to_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/battery_trader/results/vbb_250_toy_pfs.csv')