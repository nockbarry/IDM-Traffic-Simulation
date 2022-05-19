
from numpy.lib.function_base import average
from IDMSimulator import *
from matplotlib import pyplot as plt
import random

steps_per_update = 500 #make this low (~10) to see the simulation in action
sim = Simulation()
averages = {}

interarrival_times =  [int(random.uniform(1,4)) for i in range(20)]
Cautious1 = {"path": [0, 1],"v_0": 12.0,"a_max": 1.4,"b_max": 2.0, "s0": 2,"l" :4.0,"T":1.8,"Name":"Cautious"}
Cautious2 = {"path": [ 3, 2, 1],"v_0": 12.0,"a_max": 1.4,"b_max": 2.0, "s0": 2,"l" :4.0,"T":1.8,"Name":"Cautious"}
Aggresive1 = {"path": [0, 1],"v_0": 18.0,"a_max": 2.0,"b_max": 3.0, "s0": 2,"l" :4.0,"T":1.2,"Name":"Aggresive"}
Aggresive2 = {"path": [ 3, 2, 1],"v_0": 18.0,"a_max": 2.0,"b_max": 3.0, "s0": 2,"l" :4.0,"T":1.2,"Name":"Aggresive"}
Truck1 = {"path": [0, 1],"v_0": 9.0,"a_max": 0.9,"b_max": 1.0, "s0": 2,"l" :9.0,"T":1.8,"Name":"Truck"}
Truck2 = {"path": [ 3, 2, 1],"v_0": 9.0,"a_max": 0.9,"b_max": 1.0, "s0": 2,"l" :9.0,"T":1.8,"Name":"Truck"}
# Add multiple roads
sim.make_roads([
   ((350, 95), (80, 95)),
    ((80, 95), (-80, 95)),
    ((101, 90), (80, 95)),
    ((350, 90), (100, 90)),
])

sim.make_gen({
    'vehicles': [
        [1, Cautious1],
        [1, Cautious2]
    ],
    'interarrival': interarrival_times
})


# Start simulation
win = Window(sim)
win.offset = (-145, -95)
win.zoom = 8
win.run(steps_per_update)

plt.plot(sim.total_cars_list,'b',label = 'Cautious')
averages["Cautious"] = (np.average(sim.total_cars_list[10000:]))

sim = Simulation()
sim.make_roads([
   ((350, 95), (80, 95)),
    ((80, 95), (-80, 95)),
    ((101, 90), (80, 95)),
    ((350, 90), (100, 90)),
])

sim.make_gen({
    'vehicles': [
        [1, Aggresive1],
        [1, Aggresive2]
    ],
    'interarrival': interarrival_times
})



win = Window(sim)
win.offset = (-145, -95)
win.zoom = 8
win.run(steps_per_update)

plt.plot(sim.total_cars_list, 'r', label = 'Aggresive')
averages["Aggresive"] = (np.average(sim.total_cars_list[10000:]))
##
sim = Simulation()
sim.make_roads([
   ((350, 95), (80, 95)),
    ((80, 95), (-80, 95)),
    ((101, 90), (80, 95)),
    ((350, 90), (100, 90)),
])

sim.make_gen({
    'vehicles': [
        [1, Aggresive1],
        [1, Aggresive2],
        [1, Truck1],
        [1, Truck2]
    ],
    'interarrival': interarrival_times
})


# Start simulation
win = Window(sim)
win.offset = (-145, -95)
win.zoom = 8
win.run(steps_per_update)
plt.plot(sim.total_cars_list, 'g', label = 'Agg+Truck')

averages["Agg+Truck"] = (np.average(sim.total_cars_list[10000:]))
##
sim = Simulation()
sim.make_roads([
   ((350, 95), (80, 95)),
    ((80, 95), (-80, 95)),
    ((101, 90), (80, 95)),
    ((350, 90), (100, 90)),
])

sim.make_gen({
    'vehicles': [
        [1, Truck1],
        [1, Truck2],
        [4, Cautious1],
        [4, Cautious2]
    ],
    'interarrival': interarrival_times
})


# Start simulation
win = Window(sim)
win.offset = (-145, -95)
win.zoom = 8
win.run(steps_per_update)
plt.plot(sim.total_cars_list, label = 'Mostly Cautious')

averages["Mostly Cautious"] = (np.average(sim.total_cars_list[10000:]))

##
sim = Simulation()
sim.make_roads([

   ((350, 95), (80, 95)),
    ((80, 95), (-80, 95)),

    ((101, 90), (80, 95)),
    ((350, 90), (100, 90)),

])

sim.make_gen({
    'vehicles': [
        [1, Truck1],
        [1, Truck2],
        [1, Cautious1],
        [1, Cautious2]
    ],
    'interarrival': interarrival_times
})


# Start simulation
win = Window(sim)
win.offset = (-145, -95)
win.zoom = 8
win.run(steps_per_update)
plt.plot(sim.total_cars_list, label = 'Cautious+Truck')

averages["Cautious+Truck"] = (np.average(sim.total_cars_list[10000:]))
plt.legend()
plt.xlabel("Time Steps (1s/60)")
plt.ylabel("Cars in System")
print(averages)
plt.show()