import gurobipy as gb
from gurobipy import GRB
import pandas as pd

m = gp.Model()
print("Gurobi version:", gp.gurobi.version())

# semi-perfect foresight battery trader (ignoring deg, RTE, FCAS, elasticity)
prices = pd.read_csv('results/nem_full - parallel_energy_2021-11-29_2022-01-01.csv')
prices = prices.loc[prices['region'] == 'VIC1', 'price'].to_numpy(dtype=float)

intervals = len(prices)
T = range(1, intervals + 1)
dt = 1/12
P_min = 0
P_max = 250
hrs = 1.5
E_min = 0
E_max = P_max * hrs
cycles_day = 1

# decison variables
d = m.addVar(T, lb=P_min, ub=P_max, vtype=GRB.CONTINUOUS, name='dispatch')
l = m.addVar(T, lb=P_min, ub=P_max, vtype=GRB.CONTINUOUS, name='load')
s = m.addVar(T, lb=E_min, ub=E_max, vtype=GRB.CONTINUOUS, name='soc')

# objective
m.setObjective(
    gp.quicksum(prices[t] * (d[t] - l[t]) * dt for t in T),
    GRB.MAXIMIZE
)

# init
m.addConstr(s[0] == E_max/2)

# soc
for t in T:
    if t > 0:
        m.addConstr(
            s[t] == s[t-1] + l[t] * dt - d[t] * dt
        )

# dispatch and load
for t in T:
    m.addConstr(d[t] * dt <= s[t-1])
    m.addConstr(l[t] * dt <= E_max - s[t-1])

# cycle limit
m.addConstr(gb.quicksum(d[t] * dt for t in T) <= 
            E_max * cycles_day * intervals * dt / 24)

m.optimize()