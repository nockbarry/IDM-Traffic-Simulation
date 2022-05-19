# This one is just 1 simulation so if you want to play around with it then this is better then the other ones
from numpy.lib.function_base import average
from IDMSimulator import *
from matplotlib import pyplot as plt
import random
 
steps_per_update = 10 #make this low (~10) to see the simulation in action 
sim = Simulation()
averages = {}

interarrival_times = [int(random.uniform(2,6)) for i in range(100)] + [int(random.uniform(0,4)) for i in range(100)] 
Cautious1 = {"path": [0, 1],"v_0": 12.0,"a_max": 1.4,"b_max": 2.0, "s0": 2,"l" :4.0,"T":1.8,"Name":"Cautious"}
Cautious2 = {"path": [ 3, 2, 1],"v_0": 12.0,"a_max": 1.4,"b_max": 2.0, "s0": 2,"l" :4.0,"T":1.8,"Name":"Cautious"}
Aggresive1 = {"path": [0, 1],"v_0": 18.0,"a_max": 2.0,"b_max": 3.0, "s0": 2,"l" :4.0,"T":1.2,"Name":"Aggresive"}
Aggresive2 = {"path": [ 3, 2, 1],"v_0": 18.0,"a_max": 2.0,"b_max": 3.0, "s0": 2,"l" :4.0,"T":1.2,"Name":"Aggresive"}
Truck1 = {"path": [0, 1],"v_0": 8.0,"a_max": 0.9,"b_max": 1.0, "s0": 2,"l" :9.0,"T":1.8,"Name":"Truck"}
Truck2 = {"path": [ 3, 2, 1],"v_0": 8.0,"a_max": 0.9,"b_max": 1.0, "s0": 2,"l" :9.0,"T":1.8,"Name":"Truck"}
## Sim1

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
win = Window(sim)
win.offset = (-145, -95)
win.zoom = 8
win.run(steps_per_update)
plt.plot(sim.total_cars_list,'b',label = 'Cautious')
averages["Cautious"] = (np.average(sim.total_cars_list[10000:]))

plt.legend()
print(averages)

plt.xlabel("Time Steps (1s/60)")
plt.ylabel("Cars in System")
plt.show()

