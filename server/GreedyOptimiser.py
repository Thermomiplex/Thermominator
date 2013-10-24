import copy
import numpy as np
import random


MAX_ITERATIONS = 200

class GreedyOptimiser:

	def optimise(self, home):
		
		home.ResetHeater()	
		home.UpdateInternalTemperature()

		bestAvgDeviation = float("inf")
		bestMaxDeviation = float("inf")
		
		testHome = copy.deepcopy(home)
		
		bestTimeToSwitchOn = -1
		iteration = 0
		
		while (iteration < MAX_ITERATIONS and  (home.AvgTempDeviation() > home.tolerance or  home.MaxTempDeviation() > home.tolerance)):

			for time in range (0, home.time_slots):
				
				testHome.heater = home.heater			
				testHome.heater[time] = True
				testHome.UpdateInternalTemperature()

				testAvgDeviation = testHome.AvgTempDeviation()
				testMaxDeviation = testHome.MaxTempDeviation()

				if (testAvgDeviation < bestAvgDeviation and testMaxDeviation < bestMaxDeviation):
					bestAvgDeviation = testAvgDeviation
					bestMaxDeviation = testMaxDeviation
					bestTimeToSwitchOn = time
				

			if bestTimeToSwitchOn > -1:
				home.heater[bestTimeToSwitchOn] = True
				home.UpdateInternalTemperature()

			iteration+=1
		
		home.UpdateInternalTemperature()


#########################################################################################




class Home:

	def __init__(self, time_resolution=10):

		self.leakage_rate = 90
		self.air_mass = 1500
		self.heat_capacity = 1000
		self.set_point = 23.5
		self.tolerance = 3
		
		self.omega1 = 1
		self.omega2 = 1
		self.phi1 = 2
		self.phi2 = 2
		self.gamma = 0.8

		self.heater_power = 2000;

		self.time_slots = int(60 * 24 / time_resolution)
		self.comfort_period_start = 0
		self.comfort_period_end = self.time_slots
		self.internal_temp = [0] * self.time_slots
		self.external_temp = [0] * self.time_slots
		self.heater = [False] * self.time_slots

	def ResetHeater(self):
		self.heater = [False] * self.time_slots

	def AirMass(self, width, length, height):
		return width * length * height * 1.249

	def UpdateInternalTemperature(self):
		for t in range(1,self.time_slots):
			self.internal_temp[t] += self.internal_temp[t-1] + float(self.time_slots * self.TotalHeatInput(t) / (self.heat_capacity*self.air_mass) )

	def TotalHeatInput(self, time):
		FLAG = 0
		if self.heater[time - 1]==True:
			FLAG=1

		control = FLAG * self.heater_power
		control -= self.leakage_rate * abs(self.internal_temp[time - 1] - self.external_temp[time - 1])
		return control

	def ComsuptionAtSlot(self, time):
		return int(self.heater[time]) * ( self.heater_power)

	def Satisfied(self):
		return AvgTempDeviation() <= self.tolerance & MaxTempDeviation() <= self.tolerance

	def AvgTempDeviation(self):
		diff = [abs(internal - self.set_point) for internal in (self.comfort_period_start, self.comfort_period_end)]
		return np.mean(diff)

	def MaxTempDeviation(self):
		diff = [abs(internal - self.set_point) for internal in (self.comfort_period_start, self.comfort_period_end)]
		return max(diff)

   	def RandomTemp(self):
		self.internal_temp[0] = 19
		self.external_temp[0] = 5
		for t in range(1, self.time_slots):
			r = random.random()
			if r > 0.5:
				self.external_temp[t] = 5 + 1 * random.random() * 2
			else:
				self.external_temp[t] = 5 -1 * random.random() * 2

	def TotalDiscomfort(self):
		TotalDiscomfort = 0
		start = np.max(1, self.comfort_period_start)

		for t in range (start, self.comfort_period_end):
			TotalDiscomfort += self.omega1 * self.phi1 *(self.internal_temp[t] - self.set_point)

		return TotalDiscomfort

	def Consumption(self):
		consumption = 0
		for t in range(0, self.time_slots):
			if heater[t]:
				consumption += 1 * heater_power
			else:
				consumption += 0 * heater_power
		return consumption


home = Home()
home.RandomTemp()
home.UpdateInternalTemperature()
home.comfort_period_start=12*6
home.comfort_period_end=14*6
GreedyOptimiserA = GreedyOptimiser()
#print home.internal_temp 
GreedyOptimiserA.optimise(home)
#print home.internal_temp 




import matplotlib.pyplot as plt
import time
fig = plt.figure()
ax = fig.add_subplot(111)
x_points = xrange(0,144)

p = ax.plot(x_points,home.internal_temp, 'b')
p = ax.plot(x_points,home.external_temp, 'g')
ax.set_xlabel('x-points')
ax.set_ylabel('y-points')
ax.set_title('Simple XY point plot')
fig.show()
time.sleep(10000)

