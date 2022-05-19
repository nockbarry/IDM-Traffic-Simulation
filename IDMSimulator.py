## AMS 553 Simulation and Modeling Final Project
## By Nicholas Barrett

import numpy as np
from numpy.random import randint
from numpy import random
from copy import deepcopy
import pygame
from pygame import gfxdraw
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
from collections import deque


class Simulation:
    def __init__(self, config={}):
        # Set defaults
        self.t = 0.0            # Time
        self.frame_count = 0    # keep track of frames
        self.dt = 1/60          # Size of time step
        self.roads = []         
        self.generators = []
        self.signals = []
        self.timelimit = 750 #time limit in seconds
        self.total_cars_list = []
        self.total_cars = 0
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def make_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def make_roads(self, road_list):
        for road in road_list:
            self.make_road(*road)

    def make_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        return gen

    def make_signal(self, roads, config={}):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, config)
        self.signals.append(sig)
        return sig

    def update(self):
        for road in self.roads:
            road.update(self.dt)

        for gen in self.generators:
            gen.update()

        for signal in self.signals:
            signal.update(self)

        total_cars = 0.0
        for road in self.roads:
            total_cars += len(road.vehicles)
            if len(road.vehicles) == 0: continue
            vehicle = road.vehicles[0]

            if vehicle.x >= road.length:

                if vehicle.road_index + 1 < len(vehicle.path):

                    vehicle.road_index += 1
                    newvehicle = deepcopy(vehicle)
                    newvehicle.x = 0
                    next_road_index = vehicle.path[vehicle.road_index]
                    self.roads[next_road_index].vehicles.append(newvehicle)

                road.vehicles.popleft() 

        self.t += self.dt
        self.frame_count += 1
        self.total_cars_list.append(total_cars)
        self.total_cars = total_cars


    def run(self, steps):
        for _ in range(steps):
            self.update()

class Vehicle:
    def __init__(self, config={}):
        # Set defaults
        self.l = 4
        self.s0 = 4
        self.T = 1
        self.v_0 = 15
        self.a_max = 1.44
        self.b_max = 4.61
        self.Name = "A"
        self.path = []
        self.road_index = 0

        self.x = 0
        self.v = self.v_0
        self.a = 0
        self.stopped = False

        for attr, val in config.items():
            setattr(self, attr, val)

        self.sqrt_ab = 2*np.sqrt(self.a_max*self.b_max)
        self._v_0 = self.v_0



    def update(self, lead, dt):
        
        if self.v + self.a*dt < 0:
            self.x -= 1/2*self.v*self.v/self.a
            self.v = 0
        else:
            self.v += self.a*dt
            self.x += self.v*dt + self.a*dt*dt/2
        
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.l
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T*self.v + delta_v*self.v/self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1-(self.v/self.v_0)**4 - alpha**2)

        if self.stopped: 
            self.a = -self.b_max*self.v/self.v_0
        
    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_0 = v

    def unslow(self):
        self.v_0 = self._v_0
        
class Road:
    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.vehicles = deque()
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1]-self.start[1]) / self.length
        self.angle_cos = (self.end[0]-self.start[0]) / self.length        
        self.has_traffic_signal = False


    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def update(self, dt):
        n = len(self.vehicles)

        if n > 0:
       
            self.vehicles[0].update(None, dt)
            for i in range(1, n):
                lead = self.vehicles[i-1]
                self.vehicles[i].update(lead, dt)

            if self.traffic_signal_state: 
                self.vehicles[0].unstop()
                for vehicle in self.vehicles:
                    vehicle.unslow()
            else: 
                
                if self.vehicles[0].x >= self.length - self.traffic_signal.slow_distance:
    
                    self.vehicles[0].slow(self.traffic_signal.slow_factor*self.vehicles[0]._v_0)
                if self.vehicles[0].x >= self.length - self.traffic_signal.stop_distance and\
                   self.vehicles[0].x <= self.length - self.traffic_signal.stop_distance / 2:
                    self.vehicles[0].stop()


class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim
        self.interarrival = []
        self.arrivals =[]
        self.interarrival_ind = 0
        self.vehicles = [
            (0, {})
        ]
        self.interarrival = [int(random.uniform(2,6)) for i in range(10)]
        
        self.last_added_time = 0
        for attr, val in config.items():
            setattr(self, attr, val)

        print(self.interarrival)
        self.upcoming_vehicle = self.generate_vehicle()

       
    def generate_vehicle(self):
        total_vehicles = sum(pair[0] for pair in self.vehicles)
        r = randint(1, total_vehicles+1)
        for (weight, config) in self.vehicles:
            r -= weight
            if r <= 0:
                return Vehicle(config)

    def update(self):
        """Add vehicles"""
        
        if self.sim.t - self.last_added_time >= self.interarrival[self.interarrival_ind]:
            #print("Arrival at:",self.sim.t)
            #print("Next Arrival in: ", self.interarrival[self.interarrival_ind])

            road = self.sim.roads[self.upcoming_vehicle.path[0]]      
            if len(road.vehicles) == 0\
               or road.vehicles[-1].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:

                # If there is space for next vehicle, add it
                self.upcoming_vehicle.time_added = self.sim.t
                road.vehicles.append(self.upcoming_vehicle)
                
                self.last_added_time = self.sim.t
            self.upcoming_vehicle = self.generate_vehicle()
            self.interarrival_ind += 1 
            if self.interarrival_ind+1 > len(self.interarrival): self.interarrival_ind = 0


class TrafficSignal:
    def __init__(self, roads, config={}):
       # set defaults
        self.roads = roads
        self.cycle = [(False, True), (True, False)]
        self.slow_distance = 45
        self.slow_factor = 0.35
        self.stop_distance = 10

       
        self.cycle_index = 0

        self.last_t = 0
        # make any updates
        for attr, val in config.items():
            setattr(self, attr, val)

        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)



    @property
    def current_cycle(self):
        return self.cycle[self.cycle_index]
    
    def update(self, sim):
        cycle_length = 45
        k = (sim.t // cycle_length) % 2
        self.cycle_index = int(k)

#most of this  class is standard and copied
class Window:
    def __init__(self, sim, config={}):
        # pass sim into self
        self.sim = sim
        # Set defaults
        self.width = 1400
        self.height = 900
        self.bg_color = (250, 250, 250)
        self.fps = 60
        self.zoom = 5
        self.offset = (0, 0)
        self.mouse_last = (0, 0)
        self.mouse_down = False
      
        for attr, val in config.items():
            setattr(self, attr, val)
        

    def loop(self, loop=None):
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()
        clock = pygame.time.Clock()
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Arial', 16)
        running = True
        while running:
            if loop: loop(self.sim)
            self.draw()
            pygame.display.update()
            clock.tick(self.fps)
            if self.sim.t > self.sim.timelimit:
                running = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:
                        x, y = pygame.mouse.get_pos()
                        x0, y0 = self.offset
                        self.mouse_last = (x-x0*self.zoom, y-y0*self.zoom)
                        self.mouse_down = True
                    if event.button == 4:
                        self.zoom *=  (self.zoom**2+self.zoom/4+1) / (self.zoom**2+1)
                    if event.button == 5:
                        self.zoom *= (self.zoom**2+1) / (self.zoom**2+self.zoom/4+1)
                elif event.type == pygame.MOUSEMOTION:
                    if self.mouse_down:
                        x1, y1 = self.mouse_last
                        x2, y2 = pygame.mouse.get_pos()
                        self.offset = ((x2-x1)/self.zoom, (y2-y1)/self.zoom)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False           

    def run(self, steps_per_update=1):
        """Runs the simulation by updating in every loop."""
        def loop(sim):
            sim.run(steps_per_update)
        self.loop(loop)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width/2 + (x + self.offset[0])*self.zoom),
            int(self.height/2 + (y + self.offset[1])*self.zoom)
        )

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(-self.offset[0] + (x - self.width/2)/self.zoom),
            int(-self.offset[1] + (y - self.height/2)/self.zoom)
        )


    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))

    def line(self, start_pos, end_pos, color):
        """Draws a line."""
        gfxdraw.line(
            self.screen,
            *start_pos,
            *end_pos,
            color
        )

    def rect(self, pos, size, color):
        """Draws a rectangle."""
        gfxdraw.rectangle(self.screen, (*pos, *size), color)

    def box(self, pos, size, color):
        """Draws a rectangle."""
        gfxdraw.box(self.screen, (*pos, *size), color)

    def polygon(self, vertices, color, filled=True):
        gfxdraw.aapolygon(self.screen, vertices, color)
        if filled:
            gfxdraw.filled_polygon(self.screen, vertices, color)


    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255), filled=True):
        """Draws a rectangle centered at *pos* with size *size* and rotated counter-clockwise by *angle*."""
        x, y = pos
        l, h = size
        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        vertex = lambda e1, e2: (
            x + (e1*l*cos + e2*h*sin)/2,
            y + (e1*l*sin - e2*h*cos)/2
        )
        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(-1,-1), (-1, 1), (1,1), (1,-1)]]
            )
        else:
            vertices = self.convert(
                [vertex(*e) for e in [(0,-1), (0, 1), (2,1), (2,-1)]]
            )

        self.polygon(vertices, color, filled=filled)

    def rotated_rect(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 255, 0)):
        self.rotated_box(pos, size, angle=angle, cos=cos, sin=sin, centered=centered, color=color, filled=False)


    def draw_axes(self, color=(100, 100, 100)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)
        self.line(
            self.convert((0, y_start)),
            self.convert((0, y_end)),
            color
        )
        self.line(
            self.convert((x_start, 0)),
            self.convert((x_end, 0)),
            color
        )

    

    def draw_roads(self):
        for road in self.sim.roads:
            # Draw road background
            self.rotated_box(
                road.start,
                (road.length, 3.75),
                cos=road.angle_cos,
                sin=road.angle_sin,
                color=(180, 180, 220),
                centered=False
            )
         
    def draw_vehicle(self, vehicle, road):
        l, h = vehicle.l,  2
        sin, cos = road.angle_sin, road.angle_cos

        x = road.start[0] + cos * vehicle.x 
        y = road.start[1] + sin * vehicle.x 
        color = (0,0,255)
        if vehicle.Name == "Cautious": color = (0,0,255)
        if vehicle.Name == "Aggresive": color = (255,0,0)
        if vehicle.Name == "Truck": color = (255,0,255)
        self.rotated_box((x, y), (l, h), cos=cos, sin=sin, centered=True, color = color)

    def draw_vehicles(self):
        for road in self.sim.roads:
            # Draw vehicles
            for vehicle in road.vehicles:
                self.draw_vehicle(vehicle, road)

    def draw_signals(self):
        for signal in self.sim.signals:
            for i in range(len(signal.roads)):
                color = (0, 255, 0) if signal.current_cycle[i] else (255, 0, 0)
                for road in signal.roads[i]:
                    a = 0
                    position = (
                        (1-a)*road.end[0] + a*road.start[0],        
                        (1-a)*road.end[1] + a*road.start[1]
                    )
                    self.rotated_box(
                        position,
                        (1, 3),
                        cos=road.angle_cos, sin=road.angle_sin,
                        color=color)

    def draw_status(self):
        text_fps = self.text_font.render(f't={self.sim.t:.5}', False, (0, 0, 0))
        text_frc = self.text_font.render(f'step={self.sim.frame_count}', False, (0, 0, 0))
        text_veh = self.text_font.render(f'# Cars ={self.sim.total_cars}', False, (0, 0, 0))

        self.screen.blit(text_fps, (0, 0))
        self.screen.blit(text_frc, (100, 0))
        self.screen.blit(text_veh, (200, 0))


    def draw(self):
        self.background(*self.bg_color)

        self.draw_roads()
        self.draw_vehicles()
        self.draw_signals()

        self.draw_status()
        