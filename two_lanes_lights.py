from numpy.lib.function_base import average
from IDMSimulator import *
from matplotlib import pyplot as plt
import random

steps_per_update=500 #make this low (~10) to see the simulation in action
a = 3
b = 15
l = 500
averages = {}
# Roads
WEST_IN = ((-b-l, a), (-b, a))
EAST_IN = ((b+l, -a), (b, -a))
WEST_OUT = ((-b, -a), (-b-l, -a))
EAST_OUT  = ((b, a), (b+l, a))
WEST_MID = ((-b, a), (b, a))
EAST_MID = ((b, -a), (-b, -a))


interarrival_times = [int(random.uniform(2,6)) for i in range(10)] + [int(random.uniform(1,4)) for i in range(10)]
Cautious1 = {"path": [0, 4, 3],"v_0": 12.0,"a_max": 1.4,"b_max": 4.0, "s0": 2,"l" :4.0,"T":1.8,"Name":"Cautious"}
Cautious2 = {"path": [1, 5, 2],"v_0": 12.0,"a_max": 1.4,"b_max": 4.0, "s0": 2,"l" :4.0,"T":1.8,"Name":"Cautious"}
Aggresive1 = {"path": [0, 4, 3],"v_0": 18.0,"a_max": 2.0,"b_max": 5.0, "s0": 2,"l" :4.0,"T":1.2,"Name":"Aggresive"}
Aggresive2 = {"path": [1, 5, 2],"v_0": 18.0,"a_max": 2.0,"b_max": 5.0, "s0": 2,"l" :4.0,"T":1.2,"Name":"Aggresive"}
Truck1 = {"path": [0, 4, 3],"v_0": 9.0,"a_max": 0.9,"b_max": 5.0, "s0": 2,"l" :9.0,"T":1.8,"Name":"Truck"}
Truck2 = {"path": [1, 5, 2],"v_0": 9.0,"a_max": 0.9,"b_max": 5.0, "s0": 2,"l" :9.0,"T":1.8,"Name":"Truck"}

##
sim = Simulation()
sim.make_roads([
    WEST_IN,
    EAST_IN,
    WEST_OUT,
    EAST_OUT,
    WEST_MID,
    EAST_MID,
])

sim.make_gen({
'vehicles':[
    [1, Cautious1],
    [1, Cautious2],
],
'interarrival': interarrival_times
})

sim.make_signal([[0, 2], [1, 3]])

win = Window(sim)
win.zoom = 10
win.run(steps_per_update)

plt.plot(sim.total_cars_list,'b',label = 'Cautious')
averages["Cautious"] = (np.average(sim.total_cars_list[10000:]))

##
sim = Simulation()
sim.make_roads([
    WEST_IN,
    EAST_IN,
    WEST_OUT,
    EAST_OUT,
    WEST_MID,
    EAST_MID,
])

sim.make_gen({
'vehicles':[
    [1, Aggresive1],
    [1, Aggresive2],
],
'interarrival': interarrival_times
})

sim.make_signal([[0, 2], [1, 3]])

win = Window(sim)
win.zoom = 10
win.run(steps_per_update)

plt.plot(sim.total_cars_list,'r',label = 'Aggresive')
averages["Aggresive"] = (np.average(sim.total_cars_list[10000:]))

##
sim = Simulation()
sim.make_roads([
    WEST_IN,
    EAST_IN,
    WEST_OUT,
    EAST_OUT,
    WEST_MID,
    EAST_MID,
])

sim.make_gen({
'vehicles':[
    [1, Aggresive1],
    [1, Aggresive2],
    [1, Cautious1],
    [1, Cautious2]
],
'interarrival': interarrival_times
})

sim.make_signal([[0, 2], [1, 3]])

win = Window(sim)
win.zoom = 10
win.run(steps_per_update)

plt.plot(sim.total_cars_list,'g',label = 'Mixed')
averages["Mixed"] = (np.average(sim.total_cars_list[10000:]))

##
sim = Simulation()
sim.make_roads([
    WEST_IN,
    EAST_IN,
    WEST_OUT,
    EAST_OUT,
    WEST_MID,
    EAST_MID,
])

sim.make_gen({
'vehicles':[
    [1, Truck1],
    [1, Truck2],
    [1, Cautious1],
    [1, Cautious2]
],
'interarrival': interarrival_times
})

sim.make_signal([[0, 2], [1, 3]])

win = Window(sim)
win.zoom = 10
win.run(steps_per_update)

plt.plot(sim.total_cars_list,label = 'Cautious + Trucks')
averages["Cautious + Trucks"] = (np.average(sim.total_cars_list[10000:]))

##
sim = Simulation()
sim.make_roads([
    WEST_IN,
    EAST_IN,
    WEST_OUT,
    EAST_OUT,
    WEST_MID,
    EAST_MID,
])

sim.make_gen({
'vehicles':[
    [1, Truck1],
    [1, Truck2],
    [1, Aggresive1],
    [1, Aggresive2]
],
'interarrival': interarrival_times
})

sim.make_signal([[0, 2], [1, 3]])

win = Window(sim)
win.zoom = 10
win.run(steps_per_update)

plt.plot(sim.total_cars_list,label = 'Aggresive + Trucks')
averages["Aggresive + Trucks"] = (np.average(sim.total_cars_list[10000:]))

plt.xlabel("Time Steps (1s/60)")
plt.ylabel("Cars in System")
print(averages)
plt.legend()
plt.show()
