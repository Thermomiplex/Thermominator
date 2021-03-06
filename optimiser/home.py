class Home:

	def __init__(self, home_id, time_resolution):

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

		self.time_slots = 60 * 24 / time_resolution
		self.comfort_period_start = 0
		self.comfort_period_end = self.time_slots
		self.set_points = [0] * self.time_slots
		self.internal_temp = [25] * self.time_slots
		self.external_temp = [25] * self.time_slots
		self.heater = [False] * self.time_slots
		self.id = home_id

	def ResetHeater(self):
		self.heater = [False] * self.time_slots

	def AirMass(self, width, length, height):
		return width * length * height * 1.249

	def UpdateInternalTemperature(self):
		internal_temp = [temp + self.time_slots * t /
					 (self.heat_capacity * self.air_mass) for (t, temp) in enumerate(self.internal_temp)] 

	def TotalHeatInput(self, time):
		control = -1 * int(self.heater[time - 1]) * self.heater_power
		control -= self.leakage_rate * (self.internal_temp[time - 1] - self.external_temp[time - 1])
		return control

	def ComsuptionAtSlot(self, time):
		return int(self.heater[time]) * ( self.heater_power)

	def Satisfied(self):
		return AvgTempDeviation() <= self.tolerance && MaxTempDeviation() <= self.tolerance

	def AvgTempDeviation(self):
		diff = [abs(internal - setpoint) for internal,  in zip(self.internal_temp, self.set_points)]
		return mean(diff)

	def MaxTempDeviation(self):
		diff = [abs(internal - setpoint) for internal,  in zip(self.internal_temp, self.set_points)]
		return max(diff)


