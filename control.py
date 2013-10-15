'''
Created on 15 Oct 2013

@author: frede_000
'''

import urllib2 as url
import time

defIp = "152.78.101.87:8083"
defServerAddress = "152.78.200.94:11884"


def get_temperature(ip, deviceNumber):
    return url.urlopen("http://"+ip+"/ZWaveAPI/Run/devices["+str(deviceNumber)+"].instances[0].SensorMultilevel.data[1].val.value").read()

def get_current_setpoint(ip, deviceNumber):
    return url.urlopen("http://"+ip+"/ZWaveAPI/Run/devices["+str(deviceNumber)+"].ThermostatSetPoint.data[1].setVal.value").read()

def set_setpoint(ip, deviceNumber, setpoint):
    url.urlopen("http://"+ip+"/ZWaveAPI/Run/devices["+str(deviceNumber)+"].instances[0].ThermostatSetPoint.Set(1,"+str(setpoint)+")").read()

def get_setpoint_from_server(serverIp, deviceNumber):
    return url.urlopen("http://"+serverIp+"/get/"+str(deviceNumber)).read()

def get_optimised_setpoint_from_server(serverIp, deviceNumber):
    return url.urlopen("http://"+serverIp+"/get_plan/"+str(deviceNumber)).read()
    
def set_setpoint_at_server(serverIp, deviceNumber, newSetPoint):
    url.urlopen("http://"+serverIp+"/set/"+str(deviceNumber)+"/"+str(newSetPoint))
    
def set_ambient_temperature(serverIp, deviceNumber, temperature):
    url.urlopen("http://"+serverIp+"/set_ambient_temperature/"+str(deviceNumber)+"/"+str(temperature))
    
def loop(serverAddress,piAddress,deviceNumber):
    while True:
        #try:
            #get current values from thermostat
            currentSetpoint = get_current_setpoint(piAddress, deviceNumber)
            currentTemp = get_temperature(piAddress, deviceNumber)
            print("Current Setpoint: " + str(currentSetpoint) + "; current Temperature: " + str(currentTemp))
            
            #tell server about current stuff
            #set_setpoint_at_server(serverAddress, deviceNumber, currentSetpoint)
            set_ambient_temperature(serverAddress, deviceNumber, currentTemp)
            time.sleep(5)
            
            
            #get new value from server
            newTemp = get_setpoint_from_server(serverAddress, deviceNumber)
            print("Suggested Setpoint: " + str(newTemp))
            
            # apply changes
            if newTemp != currentSetpoint:
                set_setpoint(piAddress, deviceNumber, newTemp)
            
            time.sleep(5)
        #except:
        #    print("Error, trying again in 256 seconds")
        #    time.sleep(256)
        
#run main loop
loop(defServerAddress,defIp,2)