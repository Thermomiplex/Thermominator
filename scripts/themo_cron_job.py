import redis
import urllib2 as url
import datetime
import time
# from control import get_temperature

ip = "152.78.101.204:8083"
def pi_names():
	pis = list(set(r.keys("*:setpoint")) | set(r.keys("*:ambient_set_point")))
	return [pi.split(":")[0] for pi in pis]

def log_temp(temp, pi, name):
	n = datetime.datetime.now()
	unix_time = time.mktime(n.timetuple())
	key = ":".join([pi, name])
	key_recent = key + "_latest"
	return r.hset(key, unix_time, temp) & r.set(key_recent, temp)

def get_temperature(ip, deviceNumber):
    myurl = "http://"+ip+"/ZWaveAPI/Run/devices["+str(deviceNumber)+"].instances[0].SensorMultilevel.data[1].val.value"
    print myurl
    return url.urlopen("http://"+ip+"/ZWaveAPI/Run/devices["+str(deviceNumber)+"].instances[0].SensorMultilevel.data[1].val.value").read()

r = redis.StrictRedis()
for pi in pi_names():
	temp = get_temperature(ip, pi)
	log_temp(temp, pi, "temperature_history")



