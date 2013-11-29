######################################################################
#                         RnCrete Server                             #
######################################################################

from paste.request import parse_formvars #Server imports
from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from paste.fileapp import DirectoryApp
from paste import httpserver #Server imports
import ntplib, datetime #for utc timestamp
from xml.dom import minidom
import urllib
import redis
from jinja2 import Environment, PackageLoader
import time
import datetime
import pprint
import re # Parse String (url path)
import string # Parse String (url path)


#### GET WEATHER
def getWeatherUndergroundForecastArray(latitude_deg=50.8970,longitude_deg=-1.4042):

	dom = minidom.parse(urllib.urlopen('http://api.wunderground.com/api/40e8ef22c98c9d17/geolookup/hourly7day/q/'+str(latitude_deg)+','+str(longitude_deg)+'.xml'))

	location = dom.getElementsByTagName('location')[0]
	nearby_weather_stations=location.getElementsByTagName('nearby_weather_stations')[0]
	pws=nearby_weather_stations.getElementsByTagName('pws')[0]
	airport=nearby_weather_stations.getElementsByTagName('airport')[0]
	try:
		station=pws.getElementsByTagName('station')[0]
	except:
		distancefromstation="N/a"
		try:
			station=airport.getElementsByTagName('station')[0]
		except:
			stationcity="N/a"
		else:
			city=station.getElementsByTagName('city')[0]
			stationcity= str(city.firstChild.data) # Station City Name
	else:
		city=station.getElementsByTagName('city')[0]
		stationcity= str(city.firstChild.data) # Station City Name
		distance_km=station.getElementsByTagName('distance_km')[0]
		distancefromstation= str((float(distance_km.firstChild.data)*10)/36) # Distance From Station in km/h to m/s

	hourly_forecast=dom.getElementsByTagName('hourly_forecast')[0]

	Wundergroundforecastarray = [0]*25
	for i in range(0, 25):
		forecast=hourly_forecast.getElementsByTagName('forecast')[i]
		FCTTIME=forecast.getElementsByTagName('FCTTIME')[0]

		pretty=FCTTIME.getElementsByTagName('pretty')[0]

		temp=forecast.getElementsByTagName('temp')[0]
		metric=temp.getElementsByTagName('metric')[0]
		Wundergroundforecastarray[i][0] = float(metric.firstChild.data) ##Temp in C


	#Linear Interpolation
	TemperatureArray=[0] * 144
	for i in range(0, 24):
		for j in range(0, 6):
			TemperatureArray[i*6+j][0]=(Wundergroundforecastarray[i][0]*(6-j)+Wundergroundforecastarray[i+1][0]*(j))/6
	return TemperatureArray
####


def pi_names():
	pis = list(set(r.keys("*:set_point")) | set(r.keys("*:ambient_set_point")))
	return [pi.split(":")[0] for pi in pis]

def log_temp(temp, pi, name):
	n = datetime.datetime.now()
	unix_time = time.mktime(n.timetuple())
	key = ":".join([pi, name])
	key_recent = key + "_latest"
	return r.hset(key, unix_time, temp) & r.set(key_recent, temp)

def get_temp_log(pi, name):
	key = ":".join([pi, name])
	time_temp = r.hgetall(key)
	sorted_keys = sorted([float(key) for key in time_temp.keys()])
	float_keys = {float(key): time_temp[key] for key in time_temp.keys()}
	sorted_dict = OrderedDict()
	for key in sorted_keys:
		sorted_dict[key] = float_keys[key]
	return sorted_dict

def get_temp_recent(pi, name):
	key_recent = ":".join([pi, name]) + "_latest"
	return r.get(key_recent)

#### SERVER
pydict = {} #Thermostat Request
pydictA = {} #Ambient Temperature
def app(environ, start_response):
	fields = parse_formvars(environ)

	path = environ['PATH_INFO']
	PathList = path.split("/")

	if path == "/":

		start_response('200 OK', [('content-type', 'text/html')])
		message = "Welcome etc"
		template = env.get_template('index.html')
		pis = pi_names()
		return template.render(pis=pis, message=message)

	elif PathList[1] == "history":
		pinum = PathList[2]
		start_response('200 OK', [('content-type', 'text/html')])
		template = env.get_template('test.html')
		history = get_temp_log(pinum, "setpoint")
		return template.render(history=history)

	elif PathList[1] == "set":

		pinum = PathList[2]
		temp = float(PathList[3])
		start_response('200 OK', [('content-type', 'text/xml')])
		pydict[pinum] = temp
		log_temp(temp, pinum, "setpoint")
		return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>'+ str(temp)+'</temp></pi>']

	elif PathList[1] == "set_ambient_temperature":

		pinum = PathList[2]
		temp = float(PathList[3])
		start_response('200 OK', [('content-type', 'text/xml')])
		pydictA[pinum] = temp
		log_temp(temp, pinum, "ambient_set_point")

		return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><AmbientTemp>'+ str(temp)+'</AmbientTemp></pi>']

	elif PathList[1] == "get_setpoint_history":
		pinum = PathList[2]
		start_response('200 OK', [('content-type', 'text/json')])
		return pprint.pformat(get_temp_log(pinum, "setpoint"))

	elif PathList[1] == "get_ambient_history":
		pinum = PathList[2]
		start_response('200 OK', [('content-type', 'text/json')])
		return pprint.pformat(get_temp_log(pinum, "ambient_set_point"))

	elif PathList[1] == "get_temperature_history":
		pinum = PathList[2]
		start_response('200 OK', [('content-type', 'text/json')])
		return pprint.pformat(get_temp_log(pinum, "temperature_history"))


	elif PathList[1] == "get":
		start_response('200 OK', [('content-type', 'text/xml')])
		pinum = PathList[2]
		if pinum in pydict:
			return [str(pydict[pinum])] #['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>'+ str(pydict[pinum])+'</temp></pi>']
		else:
			return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>NO TEMP</temp></pi>']

	elif PathList[1] == "get_plan":
		start_response('200 OK', [('content-type', 'text/xml')])
		pinum = PathList[2]
		if pinum in pydict:
			print getWeatherUndergroundForecastArray()
			return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>'+ str(pydict[pinum])+'</temp></pi>']
		else:
			return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>NO Policy</temp></pi>']

	# else:
	# 	start_response('200 OK', [('content-type', 'text/xml')])
	# 	return ['<error> Not a valid request. For information about our API service please check our web site at http://www.intelligence.tuc.gr/renes. </error>']


static_app = StaticURLParser("static/")
full_app = Cascade([static_app, app])

if __name__ == '__main__':
	r = redis.StrictRedis()
	env = Environment(loader=PackageLoader('templates', 'files'))

	httpserver.serve(full_app, host='0.0.0.0', port='11884')

