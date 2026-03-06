# semi-perfect foresight battery trader (ignoring deg, RTE, double reg)

import gurobipy as gb
from gurobipy import GRB
import pandas as pd

m = gb.Model()
print("Gurobi version:", gb.gurobi.version())

# prices
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

# elasticity prices
rop_p1 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - +50 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_p2 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - +100 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_p3 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - +150 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_p4 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - +200 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_p5 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - +250 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_n1 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - -50 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_n2 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - -100 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_n3 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - -150 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_n4 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - -200 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)
rop_n5 = pd.read_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/results/nem_full - parallel - -250 VIC1_energy_2021-11-29_2022-01-01.csv').loc[master['region'] == 'VIC1', 'price'].to_numpy(dtype=float)

#variables
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

# elasticity breakpoints and variables
d_q_bp = {
    t: [0.0, 50.0, 100, 150.0, 200.0, 250.0] for t in T
}
l_q_bp = {
    t: [0.0, 50.0, 100.0, 150.0, 200.0, 250.0] for t in T
}
d_p_bp = {
    t: [rop[t], rop_n1[t], rop_n2[t], rop_n3[t], rop_n4[t], rop_n5[t]] for t in T
}
l_p_bp = {
    t: [rop[t], rop_p1[t], rop_p2[t], rop_p3[t], rop_p4[t], rop_p5[t]] for t in T
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

# standard decison variables
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

# decision variables for elasticity
lam_d = m.addVars(T, K_d, lb=0, name="lambda_dispatch")
lam_l = m.addVars(T, K_l, lb=0, name="lambda_load")
R_d = m.addVars(T, name="revenue_dispatch")
C_l = m.addVars(T, name="cost_charge")

# objective
m.setObjective(
    gb.quicksum(rop[t] * (d_rr[t] * rreg_util - d_lr[t] * lreg_util) * dt + (R_d[t] - C_l[t]) * dt + 
                (c_rr[t] * rreg[t] + c_lr[t] * lreg[t] + c_r6[t] * r6[t] + c_r60[t] * r60[t] + c_r5[t] * r5[t] + 
                c_l6[t] * l6[t] + c_l60[t] * l60[t] + c_l5[t] * l5[t]) * dt
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
    "soc": [s[t].X for t in T],
    "R_d": [R_d[t].X for t in T],
    "C_l": [C_l[t].X for t in T],
    "lambda_d1": [lam_d[t,0].X for t in T],
    "lambda_d2": [lam_d[t,1].X for t in T],
    "lambda_d3": [lam_d[t,2].X for t in T],
    "lambda_d4": [lam_d[t,3].X for t in T],
    "lambda_d5": [lam_d[t,4].X for t in T],
    "lambda_c1": [lam_l[t,0].X for t in T],
    "lambda_c2": [lam_l[t,1].X for t in T],
    "lambda_c3": [lam_l[t,2].X for t in T],
    "lambda_c4": [lam_l[t,3].X for t in T],
    "lambda_c5": [lam_l[t,4].X for t in T],
    "lambda_c6": [lam_l[t,5].X for t in T]
})

results.to_csv('C:/Users/rahee/OneDrive/文档/Monash-NEMPY/lambda_pwl_energy_elasticity.csv')