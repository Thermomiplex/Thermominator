import redis
from control import get_temperature

ip = "152.78.101.87:8083"
def pi_names():
	pis = list(set(r.keys("*:set_point")) | set(r.keys("*:ambient_set_point")))
	return [pi.split(":")[0] for pi in pis]

def log_temp(temp, pi, name):
	n = datetime.datetime.now()
	unix_time = time.mktime(n.timetuple())
	key = ":".join([pi, name])
	key_recent = key + "_latest"
	return r.hset(key, unix_time, temp) & r.set(key_recent, temp)

r = redis.StrictRedis()
for pi in pi_names():
	temp = get_temperature(ip, pi)
	log_temp(temp, pi, "temperature_history")



