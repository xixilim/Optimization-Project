# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 11:42:46 2021

@author: Team 13 - Chenlin Cheng / Megan Brunick / Sebastian Rincon

"""
### Optimization Final Project ###
### December 10, 2021 ###

## Import gurogi package
import gurobipy as gp
from gurobipy import GRB
import csv as csv

## Data for Year 1
demand = [1000, 1200, 1800, 1200, 1000, 1400, 1600, 1000]   # for retail centers 1...8
T = 10200  # total demand
plantcapacity = [16000, 12000, 14000, 10000, 13000]  #for plants 1...5
maxwidgetcost = [1920000, 1440000, 1680000, 1200000, 1560000]
constructioncost = [2000000, 1600000, 1800000, 900000, 1500000]   #one-time cost when production line is constructed
operatingcost = [420000, 380000, 460000, 280000, 340000]   #annual cost of operating
reopeningcost = [190000, 150000, 160000, 100000, 130000]
shutdowncost = [170000, 120000, 130000, 80000, 110000]
planttowarehouse =[[120, 130, 80, 50],
                    [100, 30, 100, 90],
                    [50, 70, 60, 30],
                    [60, 30, 70, 70],
                    [60, 20, 40, 80]]
warehousetoretail = [[90, 100, 60, 50, 80, 90, 20, 120],
                     [50, 70, 120, 40, 30, 90, 30, 80],
                     [60, 90, 70, 90, 90, 40, 110, 70],
                     [70, 80, 90, 60, 100, 70, 60, 90]]
M = 70000
year = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
alloy = [[94,94,94,94],
         [94,94,94,94],
         [94,94,94,94],
         [94,94,94,94],
         [94,94,94,94]]

# Create indexed sets
plants = range(len(plantcapacity))           # 5 plants
warehouses = range(len(warehousetoretail))   # 4 warehouses
retailcenters = range(len(demand))           # 8 retail centers
time = range(len(year))                      # 10 years

# Objective arrays

# planttowarehouse
planttowarehouse_cost = []
for t in range(len(year)):
    planttowarehouse_cost.append([])
    for i in range(len(plants)):
        planttowarehouse_cost[t].append([])
        for j in range(len(warehouses)):
            planttowarehouse_cost[t][i].append(planttowarehouse[i][j]*1.03**(year[t]-1))

# warehousetoretail
warehousetoretail_cost = []
for t in range(len(year)):
    warehousetoretail_cost.append([])
    for j in range(len(warehouses)):
        warehousetoretail_cost[t].append([])
        for k in range(len(retailcenters)):
            warehousetoretail_cost[t][j].append(round(warehousetoretail[j][k]*\
                                                      1.03**(year[t]-1),2))
# alloycost      
alloycost = []
for t in range(len(year)):
    alloycost.append([])
    for i in range(len(plants)):
        alloycost[t].append([])
        for j in range(len(warehouses)):
            alloycost[t][i].append(round(alloy[i][j]*1.03**(year[t]-1),2))
            
# constructioncost
constructioncost_t = []
for t in range(len(year)):
    constructioncost_t.append([])
    for i in range(len(plants)):
        constructioncost_t[t].append(round(constructioncost[i]*1.03**(year[t]-1),2))

# operatingcost
operatingcost_t = []
for t in range(len(year)):
    operatingcost_t.append([])
    for i in range(len(plants)):
        operatingcost_t[t].append(round(operatingcost[i]*1.03**(year[t]-1),2))

# reopeningcost
reopeningcost_t = []
for t in range(len(year)):
    reopeningcost_t.append([])
    for i in range(len(plants)):
        reopeningcost_t[t].append(round(reopeningcost[i]*1.03**(year[t]-1),2))
        
# shutdowncost
shutdowncost_t = []
for t in range(len(year)):
    shutdowncost_t.append([])
    for i in range(len(plants)):
        shutdowncost_t[t].append(round(shutdowncost[i]*1.03**(year[t]-1),2))
        
# widgetcost
widgetcost_t = []
for t in range(len(year)):
    widgetcost_t.append([])
    for i in range(len(plants)):
        widgetcost_t[t].append(round(maxwidgetcost[i]*1.03**(year[t]-1),2))


# demand 
retail_1 = [0, 1, 3, 4, 7]
retail_2 = [2, 5, 6]

# demand adjusted for different growth rates
demand_t = []
for t in range(len(year)):
    demand_t.append([])
    for i in range(len(demand)):
        if i in retail_1:
            demand_t[t].append(round(demand[i] + 0.2*demand[i]*(year[t]-1),2))
        elif i in retail_2:
            demand_t[t].append(round(demand[i] + 0.25*demand[i]*(year[t]-1),2))


# Create model called Flugel Production
m = gp.Model("Flugel Production")

# Create decision variables
xvars_1 = m.addVars(plants, warehouses, time, vtype=GRB.CONTINUOUS, obj = planttowarehouse_cost, lb = 0, name = "xvars_1")   # flugels produced at plant i and set to warehouse j in year t
xvars_2 = m.addVars(plants, warehouses, time, vtype=GRB.CONTINUOUS, obj = alloycost, lb = 0, name = "xvars_2")   # same as above, except objective is alloycost
yvars = m.addVars(warehouses, retailcenters, time, vtype=GRB.CONTINUOUS, obj=warehousetoretail_cost, lb = 0, name = "yvars")   # flugels shipped from warehouse j to retail center k in year t
bvars = m.addVars(plants, time, vtype=GRB.BINARY, obj = constructioncost_t, lb = 0, ub = 1,  name = "bvars")  #Plant i constructed at beginning of year t
ovars = m.addVars(plants, time, vtype=GRB.BINARY, obj = operatingcost_t, lb = 0, ub = 1,  name = "ovars")     #Plant i is operating at year t
rvars = m.addVars(plants, time, vtype=GRB.BINARY, obj = reopeningcost_t, lb = 0, ub = 1,  name = "rvars")     #Plant i is reopened at beginning of year t
svars = m.addVars(plants, time, vtype=GRB.BINARY, obj = shutdowncost_t, lb = 0, ub = 1,  name = "svars")     #Plant i is shutdown at end of year t
ivars = m.addVars(warehouses, time, vtype = GRB.CONTINUOUS, lb = 0, name = 'ivars')         #Inventory in warehouse i at end of year t



# Decision variables for cost structure
lambda1 = m.addVars(plants, time, vtype = GRB.CONTINUOUS, obj = 0, lb = 0, name = 'lambda1')        
lambda2 = m.addVars(plants, time, vtype = GRB.CONTINUOUS, obj = 450000, lb = 0, name = 'lambda2')   # 0 <= xvars <= 3000
lambda3 = m.addVars(plants, time, vtype = GRB.CONTINUOUS, obj = widgetcost_t, lb = 0, name = 'lambda3')  # 3000 <= xvars <= plantcapacity i

Y1 = m.addVars(plants, time, vtype = GRB.BINARY, lb = 0, ub = 1, name = 'Y1')        
Y2 = m.addVars(plants, time, vtype = GRB.BINARY, lb = 0, ub = 1, name = 'Y2')
Y3 = m.addVars(plants, time, vtype = GRB.BINARY, lb = 0, ub = 1, name = 'Y3')

# Minimization problem
m.modelSense = GRB.MINIMIZE

# Create constraints
m.addConstrs((xvars_1[i, j, t] == xvars_2[i, j, t] for i in plants for j in warehouses for t in time), "xvar_1 = xvar_2")
m.addConstrs((xvars_2.sum(i, '*', t)*4.7 <= 60000 for i in plants for t in time), "Resource Constraint_Alloy")
m.addConstrs((xvars_1.sum(i, '*', t) <= plantcapacity[i]*ovars[i,t] for t in time for i in plants), "Plant Production Capacity")
m.addConstrs((yvars.sum('*', k, t) == demand_t[t][k] for k in retailcenters for t in time), 'Demand of Retail Centers')

# Constraints for cost structure
m.addConstrs((lambda1[i, t] + lambda2[i, t] + lambda3[i, t] == 1 for i in plants for t in time), "Lambdas sum to 1")
m.addConstrs((Y1[i, t] + Y2[i, t] == 1 for i in plants for t in time), "Y sum to 1")
m.addConstrs((lambda1[i, t] <= Y1[i, t] for i in plants for t in time), "Lambda 1 <= Y1")
m.addConstrs((lambda2[i, t] <= Y1[i, t] + Y2[i, t] for i in plants for t in time), "Lambda 2 <= Y1 and Y2")
m.addConstrs((lambda3[i, t] <= Y2[i, t] for i in plants for t in time), "Lambda 3 <= Y2")
m.addConstrs((xvars_1.sum(i, '*', t) == 0*lambda1[i, t] + 3000*lambda2[i, t] + plantcapacity[i]*lambda3[i, t] for i in plants for t in time), "Convex Combination")

# Constraints for warehouse capacity
m.addConstrs((yvars.sum(j, '*', t) - xvars_1.sum('*', j, t) == ivars[j, t]\
              for j in warehouses for t in time), 'Inventory Definition Constraint') 
m.addConstrs((xvars_1.sum('*', j, t) +ivars[j, t-1] <= 12000 \
              for j in warehouses for t in range(1, 10)), 'Flow-in Constraint') 
m.addConstrs((yvars.sum(j, '*', t) <= 12000\
              for t in time for j in warehouses), "Flow-out Constraint")
m.addConstrs((xvars_1.sum('*', j, t) +ivars[j, t-1] == yvars.sum(j, '*', t) + ivars[j, t] \
              for j in warehouses for t in range(1, 10)), 'Flow Equilibrium') 
m.addConstrs(((ivars[j, 9] == 0) for j in warehouses), \
             'Ending inventory equals to 0')
m.addConstrs(((bvars[i, t] == 1) >> (rvars[i, t] == 1) for i in plants for t in time), \
             'Product line is constructed, the plant incurs reopening cost')

    
# Constraints for Plant Production Lines
m.addConstrs((bvars.sum(i, '*') <= 1 for i in plants), "Plant i construction")
m.addConstrs(((rvars[i, t] == 1) >> (ovars[i, t] == 1) for i in plants for t in time), \
             'Product line is reopen, the plant incurs operating cost')
m.addConstrs(((bvars[i, t] == 1) >> (ovars[i, t] == 1) for i in plants for t in time), \
             'Product line is constructed, the plant incurs operating cost')
m.addConstrs(((svars[i, t] == 1) >> (xvars_1[i, j, t+1] == 0) for i in plants for j in warehouses for t in time[0:9]), \
             'Product line is not operating, no Flugel will be produced in the next year')
    
o = m.addVars(plants, time, vtype = GRB.BINARY, lb = 0, ub = 1, name = 'o_minus')
m.addConstrs(o[i,t] == ovars[i, t] - ovars[i, t-1] for i in plants for t in range(1, 10))

m.addConstrs(((o[i, t] == 1) >> (bvars[i, t] == 1) for i in plants for t in time), \
             'Product line is constructed, the plant incurs operating cost')
    
m.addConstrs(((ovars[i, 0] == 1) >> (bvars[i, 0] == 1) for i in plants for t in time), \
             'Product line is constructed, the plant incurs operating cost')
    
# Prints model in a form to look at it line by line (to ensure constraints and objective function written correctly)
m.write('Final Project Model_Team 13.lp')

# Optimize Model
m.optimize()

# Objective Function Value
print('\nTotal Costs: %g' % m.objVal)

xvar_cost = 120 *xvars_1[0,0,0].X + 130 *xvars_1[0,0,1].X + 80 *xvars_1[0,0,2].X + \
    50 *xvars_1[0,0,3].X + 100 *xvars_1[0,0,4].X + 30 *xvars_1[0,0,5].X + 100 *xvars_1[0,0,6].X + \
    90 *xvars_1[0,0,7].X + 50 *xvars_1[0,0,8].X + 70 *xvars_1[0,0,9].X + 60 *xvars_1[0,1,0].X + \
   30 *xvars_1[0,1,1].X+ 60 *xvars_1[0,1,2].X + 30 *xvars_1[0,1,3].X + 70 *xvars_1[0,1,4].X + \
      70 *xvars_1[0,1,5].X+ 60 *xvars_1[0,1,6].X + 20 *xvars_1[0,1,7].X + 40 *xvars_1[0,1,8].X + \
        80 *xvars_1[0,1,9].X + 123.6 *xvars_1[0,2,0].X + 133.9 *xvars_1[0,2,1].X + \
    82.4 *xvars_1[0,2,2].X + 51.5 *xvars_1[0,2,3].X + 103 *xvars_1[0,2,4].X + \
   30.9 *xvars_1[0,2,5].X + 103 *xvars_1[0,2,6].X + 92.7 *xvars_1[0,2,7].X + \
      51.5 *xvars_1[0,2,8].X + 72.1 *xvars_1[0,2,9].X + 61.8 *xvars_1[0,3,0].X + \
         0.9 *xvars_1[0,3,1].X + 61.8 *xvars_1[0,3,2].X + 30.9 *xvars_1[0,3,3].X + \
        72.1 *xvars_1[0,3,4].X + 72.1 *xvars_1[0,3,5].X + 61.8 *xvars_1[0,3,6].X + \
    20.6 *xvars_1[0,3,7].X + 41.2 *xvars_1[0,3,8].X + 82.4 *xvars_1[0,3,9].X + \
   127.308 *xvars_1[1,0,0].X + 137.917 *xvars_1[1,0,1].X + \
     84.872 *xvars_1[1,0,2].X + 53.045 *xvars_1[1,0,3].X + \
    106.09 *xvars_1[1,0,4].X + 31.827 *xvars_1[1,0,5].X + 106.09 *xvars_1[1,0,6].X + \
        95.481 *xvars_1[1,0,7].X + 53.045 *xvars_1[1,0,8].X + 74.263 *xvars_1[1,0,9].X + \
        63.654 *xvars_1[1,1,0].X + 31.827 *xvars_1[1,1,1].X + 63.654 *xvars_1[1,1,2].X + \
        31.827 *xvars_1[1,1,3].X + 74.263 *xvars_1[1,1,4].X + 74.263 *xvars_1[1,1,5].X + \
        63.654 *xvars_1[1,1,6].X + 21.218 *xvars_1[1,1,7].X + 42.436 *xvars_1[1,1,8].X + \
        84.872 *xvars_1[1,1,9].X + 131.12724 *xvars_1[1,2,0].X + 142.05451 *xvars_1[1,2,1].X + \
    87.41816 *xvars_1[1,2,2].X + 54.63635 *xvars_1[1,2,3].X + 109.2727 *xvars_1[1,2,4].X + \
        32.78181 *xvars_1[1,2,5].X + 109.2727 *xvars_1[1,2,6].X + 98.34542999999999 *xvars_1[1,2,7].X + \
    54.63635 *xvars_1[1,2,8].X + 76.49089000000001 *xvars_1[1,2,9].X + 65.56362 *xvars_1[1,3,0].X + \
   32.78181 *xvars_1[1,3,1].X + 65.56362 *xvars_1[1,3,2].X + 32.78181 *xvars_1[1,3,3].X + \
     76.49089000000001 *xvars_1[1,3,4].X + 76.49089000000001 *xvars_1[1,3,5].X + 65.56362 *xvars_1[1,3,6].X + \
    21.85454 *xvars_1[1,3,7].X + 43.70908 *xvars_1[1,3,8].X + 87.41816 *xvars_1[1,3,9].X + \
        135.0610572 *xvars_1[2,0,0].X + 146.3161453 *xvars_1[2,0,1].X + 90.04070480000001 *xvars_1[2,0,2].X + \
    56.27544050000001 *xvars_1[2,0,3].X + 112.550881 *xvars_1[2,0,4].X + 33.76526430000001 *xvars_1[2,0,5].X + \
    112.550881 *xvars_1[2,0,6].X + 101.2957929 *xvars_1[2,0,7].X + 56.27544050000001 *xvars_1[2,0,8].X + \
    78.78561670000001 *xvars_1[2,0,9].X + 67.53052860000001 *xvars_1[2,1,0].X + \
   33.76526430000001 *xvars_1[2,1,1].X + 67.53052860000001 *xvars_1[2,1,2].X + \
     33.76526430000001 *xvars_1[2,1,3].X + 78.78561670000001 *xvars_1[2,1,4].X + 78.78561670000001 *xvars_1[2,1,5].X + \
         67.53052860000001 *xvars_1[2,1,6].X + 22.5101762 *xvars_1[2,1,7].X + \
             45.02035240000001 *xvars_1[2,1,8].X + 90.04070480000001 *xvars_1[2,1,9].X + \
    139.112888916 *xvars_1[2,2,0].X + 150.705629659 *xvars_1[2,2,1].X + 92.741925944 *xvars_1[2,2,2].X + \
   57.963703715 *xvars_1[2,2,3].X + 115.92740743 *xvars_1[2,2,4].X + 34.778222229 *xvars_1[2,2,5].X + \
     115.92740743 *xvars_1[2,2,6].X + 104.334666687 *xvars_1[2,2,7].X + 57.963703715 *xvars_1[2,2,8].X + \
    81.14918520100001 *xvars_1[2,2,9].X + 69.556444458 *xvars_1[2,3,0].X + 34.778222229 *xvars_1[2,3,1].X + \
        69.556444458 *xvars_1[2,3,2].X + 34.778222229 *xvars_1[2,3,3].X + 81.14918520100001 *xvars_1[2,3,4].X + \
            81.14918520100001 *xvars_1[2,3,5].X + 69.556444458 *xvars_1[2,3,6].X + 23.185481486 *xvars_1[2,3,7].X + \
    46.370962972 *xvars_1[2,3,8].X + 92.741925944 *xvars_1[2,3,9].X + 143.28627558348 *xvars_1[3,0,0].X + \
        155.22679854877 *xvars_1[3,0,1].X + 95.52418372232 *xvars_1[3,0,2].X + 59.70261482645001 *xvars_1[3,0,3].X + \
            119.4052296529 *xvars_1[3,0,4].X + 35.82156889587 *xvars_1[3,0,5].X + 119.4052296529 *xvars_1[3,0,6].X + \
   107.46470668761 *xvars_1[3,0,7].X + 59.70261482645001 *xvars_1[3,0,8].X + 83.58366075703 *xvars_1[3,0,9].X + \
       71.64313779174 *xvars_1[3,1,0].X + 35.82156889587 *xvars_1[3,1,1].X + 71.64313779174 *xvars_1[3,1,2].X + \
           35.82156889587 *xvars_1[3,1,3].X + 83.58366075703 *xvars_1[3,1,4].X + 83.58366075703 *xvars_1[3,1,5].X + \
    71.64313779174 *xvars_1[3,1,6].X + 23.88104593058 *xvars_1[3,1,7].X + 47.76209186116 *xvars_1[3,1,8].X + \
    95.52418372232 *xvars_1[3,1,9].X + 147.5848638509844 *xvars_1[3,2,0].X + 159.8836025052331 *xvars_1[3,2,1].X + 98.38990923398961 *xvars_1[3,2,2].X + 61.49369327124351 *xvars_1[3,2,3].X + 122.987386542487 *xvars_1[3,2,4].X + 36.8962159627461 *xvars_1[3,2,5].X + 122.987386542487 *xvars_1[3,2,6].X + 110.6886478882383 *xvars_1[3,2,7].X + 61.49369327124351 *xvars_1[3,2,8].X + 86.09117057974092 *xvars_1[3,2,9].X + 73.79243192549221 *xvars_1[3,3,0].X + 36.8962159627461 *xvars_1[3,3,1].X + 73.79243192549221 *xvars_1[3,3,2].X + 36.8962159627461 *xvars_1[3,3,3].X + 86.09117057974092 *xvars_1[3,3,4].X + 86.09117057974092 *xvars_1[3,3,5].X + 73.79243192549221 *xvars_1[3,3,6].X + 24.5974773084974 *xvars_1[3,3,7].X + 49.19495461699481 *xvars_1[3,3,8].X + 98.38990923398961 *xvars_1[3,3,9].X + 152.012409766514 *xvars_1[4,0,0].X + 164.6801105803901 *xvars_1[4,0,1].X + 101.3416065110093 *xvars_1[4,0,2].X + 63.33850406938082 *xvars_1[4,0,3].X + 126.6770081387616 *xvars_1[4,0,4].X + 38.00310244162849 *xvars_1[4,0,5].X + 126.6770081387616 *xvars_1[4,0,6].X + 114.0093073248855 *xvars_1[4,0,7].X + 63.33850406938082 *xvars_1[4,0,8].X + 88.67390569713315 *xvars_1[4,0,9].X + 76.00620488325698 *xvars_1[4,1,0].X + 38.00310244162849 *xvars_1[4,1,1].X + 76.00620488325698 *xvars_1[4,1,2].X + 38.00310244162849 *xvars_1[4,1,3].X + 88.67390569713315 *xvars_1[4,1,4].X + 88.67390569713315 *xvars_1[4,1,5].X + 76.00620488325698 *xvars_1[4,1,6].X + 25.33540162775233 *xvars_1[4,1,7].X + 50.67080325550465 *xvars_1[4,1,8].X + 101.3416065110093 *xvars_1[4,1,9].X + 156.5727820595094 *xvars_1[4,2,0].X + 169.6205138978018 *xvars_1[4,2,1].X + 104.3818547063396 *xvars_1[4,2,2].X + 65.23865919146225 *xvars_1[4,2,3].X + 130.4773183829245 *xvars_1[4,2,4].X + 39.14319551487735 *xvars_1[4,2,5].X + 130.4773183829245 *xvars_1[4,2,6].X + 117.429586544632 *xvars_1[4,2,7].X + 65.23865919146225 *xvars_1[4,2,8].X + 91.33412286804715 *xvars_1[4,2,9].X + 78.2863910297547 *xvars_1[4,3,0].X + 39.14319551487735 *xvars_1[4,3,1].X + 78.2863910297547 *xvars_1[4,3,2].X + 39.14319551487735 *xvars_1[4,3,3].X + 91.33412286804715 *xvars_1[4,3,4].X + 91.33412286804715 *xvars_1[4,3,5].X + 78.2863910297547 *xvars_1[4,3,6].X + 26.0954636765849 *xvars_1[4,3,7].X + 52.1909273531698 *xvars_1[4,3,8].X + 104.3818547063396 *xvars_1[4,3,9].X

alloy_cost = 94*xvars_2[0,0,0].X+94*xvars_2[0,0,1].X+94*xvars_2[0,0,2].X\
+94*xvars_2[0,0,3].X+94*xvars_2[0,0,4].X+94*xvars_2[0,0,5].X\
+94*xvars_2[0,0,6].X+94*xvars_2[0,0,7].X+94*xvars_2[0,0,8].X\
+94*xvars_2[0,0,9].X+94*xvars_2[0,1,0].X+94*xvars_2[0,1,1].X\
+94*xvars_2[0,1,2].X+94*xvars_2[0,1,3].X+94*xvars_2[0,1,4].X\
+94*xvars_2[0,1,5].X+94*xvars_2[0,1,6].X+94*xvars_2[0,1,7].X\
+94*xvars_2[0,1,8].X+94*xvars_2[0,1,9].X+96.82*xvars_2[0,2,0].X\
+96.82*xvars_2[0,2,1].X+96.82*xvars_2[0,2,2].X+96.82*xvars_2[0,2,3].X\
+96.82*xvars_2[0,2,4].X+96.82*xvars_2[0,2,5].X+96.82*xvars_2[0,2,6].X\
+96.82*xvars_2[0,2,7].X+96.82*xvars_2[0,2,8].X+96.82*xvars_2[0,2,9].X\
+96.82*xvars_2[0,3,0].X+96.82*xvars_2[0,3,1].X+96.82*xvars_2[0,3,2].X\
+96.82*xvars_2[0,3,3].X+96.82*xvars_2[0,3,4].X+96.82*xvars_2[0,3,5].X\
+96.82*xvars_2[0,3,6].X+96.82*xvars_2[0,3,7].X+96.82*xvars_2[0,3,8].X\
+96.82*xvars_2[0,3,9].X+99.72*xvars_2[1,0,0].X+99.72*xvars_2[1,0,1].X\
+99.72*xvars_2[1,0,2].X+99.72*xvars_2[1,0,3].X+99.72*xvars_2[1,0,4].X\
+99.72*xvars_2[1,0,5].X+99.72*xvars_2[1,0,6].X+99.72*xvars_2[1,0,7].X\
+99.72*xvars_2[1,0,8].X+99.72*xvars_2[1,0,9].X+99.72*xvars_2[1,1,0].X\
+99.72*xvars_2[1,1,1].X+99.72*xvars_2[1,1,2].X+99.72*xvars_2[1,1,3].X\
+99.72*xvars_2[1,1,4].X+99.72*xvars_2[1,1,5].X+99.72*xvars_2[1,1,6].X\
+99.72*xvars_2[1,1,7].X+99.72*xvars_2[1,1,8].X+99.72*xvars_2[1,1,9].X\
+102.72*xvars_2[1,2,0].X+102.72*xvars_2[1,2,1].X+102.72*xvars_2[1,2,2].X\
+102.72*xvars_2[1,2,3].X+102.72*xvars_2[1,2,4].X+102.72*xvars_2[1,2,5].X\
+102.72*xvars_2[1,2,6].X+102.72*xvars_2[1,2,7].X+102.72*xvars_2[1,2,8].X\
+102.72*xvars_2[1,2,9].X+102.72*xvars_2[1,3,0].X+102.72*xvars_2[1,3,1].X\
+102.72*xvars_2[1,3,2].X+102.72*xvars_2[1,3,3].X+102.72*xvars_2[1,3,4].X\
+102.72*xvars_2[1,3,5].X+102.72*xvars_2[1,3,6].X+102.72*xvars_2[1,3,7].X\
+102.72*xvars_2[1,3,8].X+102.72*xvars_2[1,3,9].X+105.8*xvars_2[2,0,0].X\
+105.8*xvars_2[2,0,1].X+105.8*xvars_2[2,0,2].X+105.8*xvars_2[2,0,3].X\
+105.8*xvars_2[2,0,4].X+105.8*xvars_2[2,0,5].X+105.8*xvars_2[2,0,6].X\
+105.8*xvars_2[2,0,7].X+105.8*xvars_2[2,0,8].X+105.8*xvars_2[2,0,9].X\
+105.8*xvars_2[2,1,0].X+105.8*xvars_2[2,1,1].X+105.8*xvars_2[2,1,2].X\
+105.8*xvars_2[2,1,3].X+105.8*xvars_2[2,1,4].X+105.8*xvars_2[2,1,5].X\
+105.8*xvars_2[2,1,6].X+105.8*xvars_2[2,1,7].X+105.8*xvars_2[2,1,8].X\
+105.8*xvars_2[2,1,9].X+108.97*xvars_2[2,2,0].X+108.97*xvars_2[2,2,1].X\
+108.97*xvars_2[2,2,2].X+108.97*xvars_2[2,2,3].X+108.97*xvars_2[2,2,4].X\
+108.97*xvars_2[2,2,5].X+108.97*xvars_2[2,2,6].X+108.97*xvars_2[2,2,7].X\
+108.97*xvars_2[2,2,8].X+108.97*xvars_2[2,2,9].X+108.97*xvars_2[2,3,0].X\
+108.97*xvars_2[2,3,1].X+108.97*xvars_2[2,3,2].X+108.97*xvars_2[2,3,3].X\
+108.97*xvars_2[2,3,4].X+108.97*xvars_2[2,3,5].X+108.97*xvars_2[2,3,6].X\
+108.97*xvars_2[2,3,7].X+108.97*xvars_2[2,3,8].X+108.97*xvars_2[2,3,9].X\
+112.24*xvars_2[3,0,0].X+112.24*xvars_2[3,0,1].X+112.24*xvars_2[3,0,2].X\
+112.24*xvars_2[3,0,3].X+112.24*xvars_2[3,0,4].X+112.24*xvars_2[3,0,5].X\
+112.24*xvars_2[3,0,6].X+112.24*xvars_2[3,0,7].X+112.24*xvars_2[3,0,8].X\
+112.24*xvars_2[3,0,9].X+112.24*xvars_2[3,1,0].X+112.24*xvars_2[3,1,1].X\
+112.24*xvars_2[3,1,2].X+112.24*xvars_2[3,1,3].X+112.24*xvars_2[3,1,4].X\
+112.24*xvars_2[3,1,5].X+112.24*xvars_2[3,1,6].X+112.24*xvars_2[3,1,7].X\
+112.24*xvars_2[3,1,8].X+112.24*xvars_2[3,1,9].X+115.61*xvars_2[3,2,0].X\
+115.61*xvars_2[3,2,1].X+115.61*xvars_2[3,2,2].X+115.61*xvars_2[3,2,3].X\
+115.61*xvars_2[3,2,4].X+115.61*xvars_2[3,2,5].X+115.61*xvars_2[3,2,6].X\
+115.61*xvars_2[3,2,7].X+115.61*xvars_2[3,2,8].X+115.61*xvars_2[3,2,9].X\
+115.61*xvars_2[3,3,0].X+115.61*xvars_2[3,3,1].X+115.61*xvars_2[3,3,2].X\
+115.61*xvars_2[3,3,3].X+115.61*xvars_2[3,3,4].X+115.61*xvars_2[3,3,5].X\
+115.61*xvars_2[3,3,6].X+115.61*xvars_2[3,3,7].X+115.61*xvars_2[3,3,8].X\
+115.61*xvars_2[3,3,9].X+119.08*xvars_2[4,0,0].X+119.08*xvars_2[4,0,1].X\
+119.08*xvars_2[4,0,2].X+119.08*xvars_2[4,0,3].X+119.08*xvars_2[4,0,4].X\
+119.08*xvars_2[4,0,5].X+119.08*xvars_2[4,0,6].X+119.08*xvars_2[4,0,7].X\
+119.08*xvars_2[4,0,8].X+119.08*xvars_2[4,0,9].X+119.08*xvars_2[4,1,0].X\
+119.08*xvars_2[4,1,1].X+119.08*xvars_2[4,1,2].X+119.08*xvars_2[4,1,3].X\
+119.08*xvars_2[4,1,4].X+119.08*xvars_2[4,1,5].X+119.08*xvars_2[4,1,6].X\
+119.08*xvars_2[4,1,7].X+119.08*xvars_2[4,1,8].X+119.08*xvars_2[4,1,9].X\
+122.65*xvars_2[4,2,0].X+122.65*xvars_2[4,2,1].X+122.65*xvars_2[4,2,2].X\
+122.65*xvars_2[4,2,3].X+122.65*xvars_2[4,2,4].X+122.65*xvars_2[4,2,5].X\
+122.65*xvars_2[4,2,6].X+122.65*xvars_2[4,2,7].X+122.65*xvars_2[4,2,8].X\
+122.65*xvars_2[4,2,9].X+122.65*xvars_2[4,3,0].X+122.65*xvars_2[4,3,1].X\
+122.65*xvars_2[4,3,2].X+122.65*xvars_2[4,3,3].X+122.65*xvars_2[4,3,4].X\
+122.65*xvars_2[4,3,5].X+122.65*xvars_2[4,3,6].X+122.65*xvars_2[4,3,7].X\
+122.65*xvars_2[4,3,8].X+122.65*xvars_2[4,3,9].X\

yvars_cost = 90*yvars[0,0,0].X\
+100*yvars[0,0,1].X+60*yvars[0,0,2].X+50*yvars[0,0,3].X+80*yvars[0,0,4].X\
+90*yvars[0,0,5].X+20*yvars[0,0,6].X+120*yvars[0,0,7].X+50*yvars[0,0,8].X\
+70*yvars[0,0,9].X+120*yvars[0,1,0].X+40*yvars[0,1,1].X+30*yvars[0,1,2].X\
+90*yvars[0,1,3].X+30*yvars[0,1,4].X+80*yvars[0,1,5].X+60*yvars[0,1,6].X\
+90*yvars[0,1,7].X+70*yvars[0,1,8].X+90*yvars[0,1,9].X+90*yvars[0,2,0].X\
+40*yvars[0,2,1].X+110*yvars[0,2,2].X+70*yvars[0,2,3].X+70*yvars[0,2,4].X\
+80*yvars[0,2,5].X+90*yvars[0,2,6].X+60*yvars[0,2,7].X+100*yvars[0,2,8].X\
+70*yvars[0,2,9].X+60*yvars[0,3,0].X+90*yvars[0,3,1].X\
+92.7*yvars[0,3,2].X+103*yvars[0,3,3].X+61.8*yvars[0,3,4].X\
+51.5*yvars[0,3,5].X+82.4*yvars[0,3,6].X+92.7*yvars[0,3,7].X\
+20.6*yvars[0,3,8].X+123.6*yvars[0,3,9].X+51.5*yvars[0,4,0].X\
+72.1*yvars[0,4,1].X+123.6*yvars[0,4,2].X+41.2*yvars[0,4,3].X\
+30.9*yvars[0,4,4].X+92.7*yvars[0,4,5].X+30.9*yvars[0,4,6].X\
+82.4*yvars[0,4,7].X+61.8*yvars[0,4,8].X+92.7*yvars[0,4,9].X\
+72.1*yvars[0,5,0].X+92.7*yvars[0,5,1].X+92.7*yvars[0,5,2].X\
+41.2*yvars[0,5,3].X+113.3*yvars[0,5,4].X+72.1*yvars[0,5,5].X\
+72.1*yvars[0,5,6].X+82.4*yvars[0,5,7].X+92.7*yvars[0,5,8].X\
+61.8*yvars[0,5,9].X+103*yvars[0,6,0].X+72.1*yvars[0,6,1].X\
+61.8*yvars[0,6,2].X+92.7*yvars[0,6,3].X+95.48*yvars[0,6,4].X\
+106.09*yvars[0,6,5].X+63.65*yvars[0,6,6].X+53.04*yvars[0,6,7].X\
+84.87*yvars[0,6,8].X+95.48*yvars[0,6,9].X+21.22*yvars[0,7,0].X\
+127.31*yvars[0,7,1].X+53.04*yvars[0,7,2].X+74.26*yvars[0,7,3].X\
+127.31*yvars[0,7,4].X+42.44*yvars[0,7,5].X+31.83*yvars[0,7,6].X\
+95.48*yvars[0,7,7].X+31.83*yvars[0,7,8].X+84.87*yvars[0,7,9].X\
+63.65*yvars[1,0,0].X+95.48*yvars[1,0,1].X+74.26*yvars[1,0,2].X\
+95.48*yvars[1,0,3].X+95.48*yvars[1,0,4].X+42.44*yvars[1,0,5].X\
+116.7*yvars[1,0,6].X+74.26*yvars[1,0,7].X+74.26*yvars[1,0,8].X\
+84.87*yvars[1,0,9].X+95.48*yvars[1,1,0].X+63.65*yvars[1,1,1].X\
+106.09*yvars[1,1,2].X+74.26*yvars[1,1,3].X+63.65*yvars[1,1,4].X\
+95.48*yvars[1,1,5].X+98.35*yvars[1,1,6].X+109.27*yvars[1,1,7].X\
+65.56*yvars[1,1,8].X+54.64*yvars[1,1,9].X+87.42*yvars[1,2,0].X\
+98.35*yvars[1,2,1].X+21.85*yvars[1,2,2].X+131.13*yvars[1,2,3].X\
+54.64*yvars[1,2,4].X+76.49*yvars[1,2,5].X+131.13*yvars[1,2,6].X\
+43.71*yvars[1,2,7].X+32.78*yvars[1,2,8].X+98.35*yvars[1,2,9].X\
+32.78*yvars[1,3,0].X+87.42*yvars[1,3,1].X+65.56*yvars[1,3,2].X\
+98.35*yvars[1,3,3].X+76.49*yvars[1,3,4].X+98.35*yvars[1,3,5].X\
+98.35*yvars[1,3,6].X+43.71*yvars[1,3,7].X+120.2*yvars[1,3,8].X\
+76.49*yvars[1,3,9].X+76.49*yvars[1,4,0].X+87.42*yvars[1,4,1].X\
+98.35*yvars[1,4,2].X+65.56*yvars[1,4,3].X+109.27*yvars[1,4,4].X\
+76.49*yvars[1,4,5].X+65.56*yvars[1,4,6].X+98.35*yvars[1,4,7].X\
+101.3*yvars[1,4,8].X+112.55*yvars[1,4,9].X+67.53*yvars[1,5,0].X\
+56.28*yvars[1,5,1].X+90.04*yvars[1,5,2].X+101.3*yvars[1,5,3].X\
+22.51*yvars[1,5,4].X+135.06*yvars[1,5,5].X+56.28*yvars[1,5,6].X\
+78.79*yvars[1,5,7].X+135.06*yvars[1,5,8].X+45.02*yvars[1,5,9].X\
+33.77*yvars[1,6,0].X+101.3*yvars[1,6,1].X+33.77*yvars[1,6,2].X\
+90.04*yvars[1,6,3].X+67.53*yvars[1,6,4].X+101.3*yvars[1,6,5].X\
+78.79*yvars[1,6,6].X+101.3*yvars[1,6,7].X+101.3*yvars[1,6,8].X\
+45.02*yvars[1,6,9].X+123.81*yvars[1,7,0].X+78.79*yvars[1,7,1].X\
+78.79*yvars[1,7,2].X+90.04*yvars[1,7,3].X+101.3*yvars[1,7,4].X\
+67.53*yvars[1,7,5].X+112.55*yvars[1,7,6].X+78.79*yvars[1,7,7].X\
+67.53*yvars[1,7,8].X+101.3*yvars[1,7,9].X+104.33*yvars[2,0,0].X\
+115.93*yvars[2,0,1].X+69.56*yvars[2,0,2].X+57.96*yvars[2,0,3].X\
+92.74*yvars[2,0,4].X+104.33*yvars[2,0,5].X+23.19*yvars[2,0,6].X\
+139.11*yvars[2,0,7].X+57.96*yvars[2,0,8].X+81.15*yvars[2,0,9].X\
+139.11*yvars[2,1,0].X+46.37*yvars[2,1,1].X+34.78*yvars[2,1,2].X\
+104.33*yvars[2,1,3].X+34.78*yvars[2,1,4].X+92.74*yvars[2,1,5].X\
+69.56*yvars[2,1,6].X+104.33*yvars[2,1,7].X+81.15*yvars[2,1,8].X\
+104.33*yvars[2,1,9].X+104.33*yvars[2,2,0].X+46.37*yvars[2,2,1].X\
+127.52*yvars[2,2,2].X+81.15*yvars[2,2,3].X+81.15*yvars[2,2,4].X\
+92.74*yvars[2,2,5].X+104.33*yvars[2,2,6].X+69.56*yvars[2,2,7].X\
+115.93*yvars[2,2,8].X+81.15*yvars[2,2,9].X+69.56*yvars[2,3,0].X\
+104.33*yvars[2,3,1].X+107.46*yvars[2,3,2].X+119.41*yvars[2,3,3].X\
+71.64*yvars[2,3,4].X+59.7*yvars[2,3,5].X+95.52*yvars[2,3,6].X\
+107.46*yvars[2,3,7].X+23.88*yvars[2,3,8].X+143.29*yvars[2,3,9].X\
+59.7*yvars[2,4,0].X+83.58*yvars[2,4,1].X+143.29*yvars[2,4,2].X\
+47.76*yvars[2,4,3].X+35.82*yvars[2,4,4].X+107.46*yvars[2,4,5].X\
+35.82*yvars[2,4,6].X+95.52*yvars[2,4,7].X+71.64*yvars[2,4,8].X\
+107.46*yvars[2,4,9].X+83.58*yvars[2,5,0].X+107.46*yvars[2,5,1].X\
+107.46*yvars[2,5,2].X+47.76*yvars[2,5,3].X+131.35*yvars[2,5,4].X\
+83.58*yvars[2,5,5].X+83.58*yvars[2,5,6].X+95.52*yvars[2,5,7].X\
+107.46*yvars[2,5,8].X+71.64*yvars[2,5,9].X+119.41*yvars[2,6,0].X\
+83.58*yvars[2,6,1].X+71.64*yvars[2,6,2].X+107.46*yvars[2,6,3].X\
+110.69*yvars[2,6,4].X+122.99*yvars[2,6,5].X+73.79*yvars[2,6,6].X\
+61.49*yvars[2,6,7].X+98.39*yvars[2,6,8].X+110.69*yvars[2,6,9].X\
+24.6*yvars[2,7,0].X+147.58*yvars[2,7,1].X+61.49*yvars[2,7,2].X\
+86.09*yvars[2,7,3].X+147.58*yvars[2,7,4].X+49.19*yvars[2,7,5].X\
+36.9*yvars[2,7,6].X+110.69*yvars[2,7,7].X+36.9*yvars[2,7,8].X\
+98.39*yvars[2,7,9].X+73.79*yvars[3,0,0].X+110.69*yvars[3,0,1].X\
+86.09*yvars[3,0,2].X+110.69*yvars[3,0,3].X+110.69*yvars[3,0,4].X\
+49.19*yvars[3,0,5].X+135.29*yvars[3,0,6].X+86.09*yvars[3,0,7].X\
+86.09*yvars[3,0,8].X+98.39*yvars[3,0,9].X+110.69*yvars[3,1,0].X\
+73.79*yvars[3,1,1].X+122.99*yvars[3,1,2].X+86.09*yvars[3,1,3].X\
+73.79*yvars[3,1,4].X+110.69*yvars[3,1,5].X+114.01*yvars[3,1,6].X\
+126.68*yvars[3,1,7].X+76.01*yvars[3,1,8].X+63.34*yvars[3,1,9].X\
+101.34*yvars[3,2,0].X+114.01*yvars[3,2,1].X+25.34*yvars[3,2,2].X\
+152.01*yvars[3,2,3].X+63.34*yvars[3,2,4].X+88.67*yvars[3,2,5].X\
+152.01*yvars[3,2,6].X+50.67*yvars[3,2,7].X+38*yvars[3,2,8].X\
+114.01*yvars[3,2,9].X+38*yvars[3,3,0].X+101.34*yvars[3,3,1].X\
+76.01*yvars[3,3,2].X+114.01*yvars[3,3,3].X+88.67*yvars[3,3,4].X\
+114.01*yvars[3,3,5].X+114.01*yvars[3,3,6].X+50.67*yvars[3,3,7].X\
+139.34*yvars[3,3,8].X+88.67*yvars[3,3,9].X+88.67*yvars[3,4,0].X\
+101.34*yvars[3,4,1].X+114.01*yvars[3,4,2].X+76.01*yvars[3,4,3].X\
+126.68*yvars[3,4,4].X+88.67*yvars[3,4,5].X+76.01*yvars[3,4,6].X\
+114.01*yvars[3,4,7].X+117.43*yvars[3,4,8].X+130.48*yvars[3,4,9].X\
+78.29*yvars[3,5,0].X+65.24*yvars[3,5,1].X+104.38*yvars[3,5,2].X\
+117.43*yvars[3,5,3].X+26.1*yvars[3,5,4].X+156.57*yvars[3,5,5].X\
+65.24*yvars[3,5,6].X+91.33*yvars[3,5,7].X+156.57*yvars[3,5,8].X\
+52.19*yvars[3,5,9].X+39.14*yvars[3,6,0].X+117.43*yvars[3,6,1].X\
+39.14*yvars[3,6,2].X+104.38*yvars[3,6,3].X+78.29*yvars[3,6,4].X\
+117.43*yvars[3,6,5].X+91.33*yvars[3,6,6].X+117.43*yvars[3,6,7].X\
+117.43*yvars[3,6,8].X+52.19*yvars[3,6,9].X+143.53*yvars[3,7,0].X\
+91.33*yvars[3,7,1].X+91.33*yvars[3,7,2].X+104.38*yvars[3,7,3].X\
+117.43*yvars[3,7,4].X+78.29*yvars[3,7,5].X+130.48*yvars[3,7,6].X\
+91.33*yvars[3,7,7].X+78.29*yvars[3,7,8].X+117.43*yvars[3,7,9].X\

plant_cost = 2e+06*bvars[0,0].X+1.6e+06*bvars[0,1].X+1.8e+06*bvars[0,2].X\
+900000*bvars[0,3].X+1.5e+06*bvars[0,4].X+2.06e+06*bvars[0,5].X\
+1.648e+06*bvars[0,6].X+1.854e+06*bvars[0,7].X+927000*bvars[0,8].X\
+1.545e+06*bvars[0,9].X+2.1218e+06*bvars[1,0].X+1.69744e+06*bvars[1,1].X\
+1.90962e+06*bvars[1,2].X+954810*bvars[1,3].X+1.59135e+06*bvars[1,4].X\
+2.185454e+06*bvars[1,5].X+1.7483632e+06*bvars[1,6].X\
+1.9669086000000001e+06*bvars[1,7].X+983454.3*bvars[1,8].X\
+1.6390905e+06*bvars[1,9].X+2.2510176200000001e+06*bvars[2,0].X\
+1.8008141000000001e+06*bvars[2,1].X+2.0259158600000001e+06*bvars[2,2].X\
+1.0129579300000001e+06*bvars[2,3].X+1.68826322e+06*bvars[2,4].X\
+2.3185481499999999e+06*bvars[2,5].X+1.85483852e+06*bvars[2,6].X\
+2.0866933300000001e+06*bvars[2,7].X+1.04334667e+06*bvars[2,8].X\
+1.7389111100000001e+06*bvars[2,9].X+2.3881045899999999e+06*bvars[3,0].X\
+1.9104836699999999e+06*bvars[3,1].X+2.1492941299999999e+06*bvars[3,2].X\
+1.0746470700000001e+06*bvars[3,3].X+1.7910784399999999e+06*bvars[3,4].X\
+2.45974773e+06*bvars[3,5].X+1.9677981799999999e+06*bvars[3,6].X\
+2.21377296e+06*bvars[3,7].X+1.10688648e+06*bvars[3,8].X\
+1.8448108e+06*bvars[3,9].X+2.5335401600000001e+06*bvars[4,0].X\
+2.0268321299999999e+06*bvars[4,1].X+2.2801861499999999e+06*bvars[4,2].X\
+1.1400930700000001e+06*bvars[4,3].X+1.9001551200000001e+06*bvars[4,4].X\
+2.6095463700000001e+06*bvars[4,5].X+2.0876370900000001e+06*bvars[4,6].X\
+2.34859173e+06*bvars[4,7].X+1.1742958700000001e+06*bvars[4,8].X\
+1.95715978e+06*bvars[4,9].X+420000*ovars[0,0].X+380000*ovars[0,1].X\
+460000*ovars[0,2].X+280000*ovars[0,3].X+340000*ovars[0,4].X\
+432600*ovars[0,5].X+391400*ovars[0,6].X+473800*ovars[0,7].X\
+288400*ovars[0,8].X+350200*ovars[0,9].X+445578*ovars[1,0].X\
+403142*ovars[1,1].X+488014*ovars[1,2].X+297052*ovars[1,3].X\
+360706*ovars[1,4].X+458945.34*ovars[1,5].X+415236.26*ovars[1,6].X\
+502654.42*ovars[1,7].X+305963.56*ovars[1,8].X+371527.18*ovars[1,9].X\
+472713.7*ovars[2,0].X+427693.35*ovars[2,1].X+517734.05*ovars[2,2].X\
+315142.47*ovars[2,3].X+382673*ovars[2,4].X+486895.11*ovars[2,5].X\
+440524.15*ovars[2,6].X+533266.0699999999*ovars[2,7].X\
+324596.74*ovars[2,8].X+394153.19*ovars[2,9].X+501501.96*ovars[3,0].X\
+453739.87*ovars[3,1].X+549264.0600000001*ovars[3,2].X\
+334334.64*ovars[3,3].X+405977.78*ovars[3,4].X+516547.02*ovars[3,5].X\
+467352.07*ovars[3,6].X+565741.98*ovars[3,7].X+344364.68*ovars[3,8].X\
+418157.11*ovars[3,9].X+532043.4300000001*ovars[4,0].X\
+481372.63*ovars[4,1].X+582714.24*ovars[4,2].X+354695.62*ovars[4,3].X\
+430701.83*ovars[4,4].X+548004.74*ovars[4,5].X+495813.81*ovars[4,6].X\
+600195.66*ovars[4,7].X+365336.49*ovars[4,8].X+443622.88*ovars[4,9].X\
+190000*rvars[0,0].X+150000*rvars[0,1].X+160000*rvars[0,2].X\
+100000*rvars[0,3].X+130000*rvars[0,4].X+195700*rvars[0,5].X\
+154500*rvars[0,6].X+164800*rvars[0,7].X+103000*rvars[0,8].X\
+133900*rvars[0,9].X+201571*rvars[1,0].X+159135*rvars[1,1].X\
+169744*rvars[1,2].X+106090*rvars[1,3].X+137917*rvars[1,4].X\
+207618.13*rvars[1,5].X+163909.05*rvars[1,6].X+174836.32*rvars[1,7].X\
+109272.7*rvars[1,8].X+142054.51*rvars[1,9].X+213846.67*rvars[2,0].X\
+168826.32*rvars[2,1].X+180081.41*rvars[2,2].X+112550.88*rvars[2,3].X\
+146316.15*rvars[2,4].X+220262.07*rvars[2,5].X+173891.11*rvars[2,6].X\
+185483.85*rvars[2,7].X+115927.41*rvars[2,8].X+150705.63*rvars[2,9].X\
+226869.94*rvars[3,0].X+179107.84*rvars[3,1].X+191048.37*rvars[3,2].X\
+119405.23*rvars[3,3].X+155226.8*rvars[3,4].X+233676.03*rvars[3,5].X\
+184481.08*rvars[3,6].X+196779.82*rvars[3,7].X+122987.39*rvars[3,8].X\
+159883.6*rvars[3,9].X+240686.32*rvars[4,0].X+190015.51*rvars[4,1].X\
+202683.21*rvars[4,2].X+126677.01*rvars[4,3].X+164680.11*rvars[4,4].X\
+247906.9*rvars[4,5].X+195715.98*rvars[4,6].X+208763.71*rvars[4,7].X\
+130477.32*rvars[4,8].X+169620.51*rvars[4,9].X+170000*svars[0,0].X\
+120000*svars[0,1].X+130000*svars[0,2].X+80000*svars[0,3].X\
+110000*svars[0,4].X+175100*svars[0,5].X+123600*svars[0,6].X\
+133900*svars[0,7].X+82400*svars[0,8].X+113300*svars[0,9].X\
+180353*svars[1,0].X+127308*svars[1,1].X+137917*svars[1,2].X\
+84872*svars[1,3].X+116699*svars[1,4].X+185763.59*svars[1,5].X\
+131127.24*svars[1,6].X+142054.51*svars[1,7].X+87418.16*svars[1,8].X\
+120199.97*svars[1,9].X+191336.5*svars[2,0].X+135061.06*svars[2,1].X\
+146316.15*svars[2,2].X+90040.7*svars[2,3].X+123805.97*svars[2,4].X\
+197076.59*svars[2,5].X+139112.89*svars[2,6].X+150705.63*svars[2,7].X\
+92741.92999999999*svars[2,8].X+127520.15*svars[2,9].X\
+202988.89*svars[3,0].X+143286.28*svars[3,1].X+155226.8*svars[3,2].X\
+95524.17999999999*svars[3,3].X+131345.75*svars[3,4].X\
+209078.56*svars[3,5].X+147584.86*svars[3,6].X+159883.6*svars[3,7].X\
+98389.91*svars[3,8].X+135286.13*svars[3,9].X+215350.91*svars[4,0].X\
+152012.41*svars[4,1].X+164680.11*svars[4,2].X+101341.61*svars[4,3].X\
+139344.71*svars[4,4].X+221811.44*svars[4,5].X+156572.78*svars[4,6].X\
+169620.51*svars[4,7].X+104381.85*svars[4,8].X+143525.05*svars[4,9].X\

widget_cost = 450000*lambda2[0,0].X+450000*lambda2[0,1].X+450000*lambda2[0,2].X\
+450000*lambda2[0,3].X+450000*lambda2[0,4].X+450000*lambda2[0,5].X\
+450000*lambda2[0,6].X+450000*lambda2[0,7].X+450000*lambda2[0,8].X\
+450000*lambda2[0,9].X+450000*lambda2[1,0].X+450000*lambda2[1,1].X\
+450000*lambda2[1,2].X+450000*lambda2[1,3].X+450000*lambda2[1,4].X\
+450000*lambda2[1,5].X+450000*lambda2[1,6].X+450000*lambda2[1,7].X\
+450000*lambda2[1,8].X+450000*lambda2[1,9].X+450000*lambda2[2,0].X\
+450000*lambda2[2,1].X+450000*lambda2[2,2].X+450000*lambda2[2,3].X\
+450000*lambda2[2,4].X+450000*lambda2[2,5].X+450000*lambda2[2,6].X\
+450000*lambda2[2,7].X+450000*lambda2[2,8].X+450000*lambda2[2,9].X\
+450000*lambda2[3,0].X+450000*lambda2[3,1].X+450000*lambda2[3,2].X\
+450000*lambda2[3,3].X+450000*lambda2[3,4].X+450000*lambda2[3,5].X\
+450000*lambda2[3,6].X+450000*lambda2[3,7].X+450000*lambda2[3,8].X\
+450000*lambda2[3,9].X+450000*lambda2[4,0].X+450000*lambda2[4,1].X\
+450000*lambda2[4,2].X+450000*lambda2[4,3].X+450000*lambda2[4,4].X\
+450000*lambda2[4,5].X+450000*lambda2[4,6].X+450000*lambda2[4,7].X\
+450000*lambda2[4,8].X+450000*lambda2[4,9].X+1.92e+06*lambda3[0,0].X\
+1.44e+06*lambda3[0,1].X+1.68e+06*lambda3[0,2].X+1.2e+06*lambda3[0,3].X\
+1.56e+06*lambda3[0,4].X+1.9776e+06*lambda3[0,5].X\
+1.4832e+06*lambda3[0,6].X+1.7304e+06*lambda3[0,7].X\
+1.236e+06*lambda3[0,8].X+1.6068e+06*lambda3[0,9].X\
+2.036928e+06*lambda3[1,0].X+1.527696e+06*lambda3[1,1].X\
+1.782312e+06*lambda3[1,2].X+1.27308e+06*lambda3[1,3].X\
+1.655004e+06*lambda3[1,4].X+2.0980358399999999e+06*lambda3[1,5].X\
+1.5735268799999999e+06*lambda3[1,6].X\
+1.8357813600000001e+06*lambda3[1,7].X\
+1.3112723999999999e+06*lambda3[1,8].X\
+1.7046541200000001e+06*lambda3[1,9].X\
+2.1609769199999999e+06*lambda3[2,0].X\
+1.6207326899999999e+06*lambda3[2,1].X+1.8908548e+06*lambda3[2,2].X\
+1.3506105700000001e+06*lambda3[2,3].X+1.75579374e+06*lambda3[2,4].X\
+2.2258062200000002e+06*lambda3[2,5].X\
+1.6693546699999999e+06*lambda3[2,6].X\
+1.9475804399999999e+06*lambda3[2,7].X\
+1.3911288899999999e+06*lambda3[2,8].X\
+1.8084675600000001e+06*lambda3[2,9].X\
+2.2925804100000001e+06*lambda3[3,0].X\
+1.7194353100000001e+06*lambda3[3,1].X\
+2.0060078600000001e+06*lambda3[3,2].X+1.43286276e+06*lambda3[3,3].X\
+1.8627215800000001e+06*lambda3[3,4].X\
+2.3613578199999998e+06*lambda3[3,5].X\
+1.7710183700000001e+06*lambda3[3,6].X\
+2.0661880900000001e+06*lambda3[3,7].X\
+1.4758486399999999e+06*lambda3[3,8].X+1.91860323e+06*lambda3[3,9].X\
+2.4321985600000001e+06*lambda3[4,0].X\
+1.8241489199999999e+06*lambda3[4,1].X\
+2.1281737400000002e+06*lambda3[4,2].X\
+1.5201241000000001e+06*lambda3[4,3].X\
+1.9761613300000001e+06*lambda3[4,4].X\
+2.5051645099999998e+06*lambda3[4,5].X\
+1.8788733799999999e+06*lambda3[4,6].X\
+2.1920189500000002e+06*lambda3[4,7].X\
+1.5657278200000001e+06*lambda3[4,8].X\
+2.0354461699999999e+06*lambda3[4,9].X+0*Y3[0,0].X+0*Y3[0,1].X\
+0*Y3[0,2].X+0*Y3[0,3].X+0*Y3[0,4].X+0*Y3[0,5].X+0*Y3[0,6].X+0*Y3[0,7].X\
+0*Y3[0,8].X+0*Y3[0,9].X+0*Y3[1,0].X+0*Y3[1,1].X+0*Y3[1,2].X+0*Y3[1,3].X\
+0*Y3[1,4].X+0*Y3[1,5].X+0*Y3[1,6].X+0*Y3[1,7].X+0*Y3[1,8].X+0*Y3[1,9].X\
+0*Y3[2,0].X+0*Y3[2,1].X+0*Y3[2,2].X+0*Y3[2,3].X+0*Y3[2,4].X+0*Y3[2,5].X\
+0*Y3[2,6].X+0*Y3[2,7].X+0*Y3[2,8].X+0*Y3[2,9].X+0*Y3[3,0].X+0*Y3[3,1].X\
+0*Y3[3,2].X+0*Y3[3,3].X+0*Y3[3,4].X+0*Y3[3,5].X+0*Y3[3,6].X+0*Y3[3,7].X\
+0*Y3[3,8].X+0*Y3[3,9].X+0*Y3[4,0].X+0*Y3[4,1].X+0*Y3[4,2].X+0*Y3[4,3].X\
+0*Y3[4,4].X+0*Y3[4,5].X+0*Y3[4,6].X+0*Y3[4,7].X+0*Y3[4,8].X+0*Y3[4,9].X\

print('xvar total cost:', xvar_cost)
print('alloy cost:', alloy_cost)
print('warehouse to retail total cost:', yvars_cost)
print('plant cost:', plant_cost)
print('widget cost:', widget_cost)

# Create an empty list of variable names
var_names = []
var_values = []
for v in m.getVars():
     if v.x >= 0:
         var_names.append((v.varName))
         var_values.append(v.X)

# Write variable names and corresponding values to CSV file
with open('Final Project Variables_Team 13.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerows(zip(var_names, var_values))

