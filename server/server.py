######################################################################
#                         RnCrete Server                             #
######################################################################

from paste.request import parse_formvars #Server imports
from paste import httpserver #Server imports
import ntplib, datetime #for utc timestamp
from xml.dom import minidom
import urllib
import numpy as np

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

	Wundergroundforecastarray = np.zeros((25,1))
	for i in range(0, 25):
		forecast=hourly_forecast.getElementsByTagName('forecast')[i]
		FCTTIME=forecast.getElementsByTagName('FCTTIME')[0]

		pretty=FCTTIME.getElementsByTagName('pretty')[0]

		temp=forecast.getElementsByTagName('temp')[0]
		metric=temp.getElementsByTagName('metric')[0]
		Wundergroundforecastarray[i][0] = float(metric.firstChild.data) ##Temp in C


	#Linear Interpolation
	TemperatureArray=np.zeros((144,1))
	for i in range(0, 24):
		for j in range(0, 6):
			TemperatureArray[i*6+j][0]=(Wundergroundforecastarray[i][0]*(6-j)+Wundergroundforecastarray[i+1][0]*(j))/6
	return TemperatureArray
####



#### SERVER
pydict = {} #Thermostat Request
pydictA = {} #Ambient Temperature
def app(environ, start_response):
	fields = parse_formvars(environ)

	path = environ['PATH_INFO']
	Separators = re.compile('/')
	PathList = Separators.split(path)
	#print len(PathList)


	if path == "/":

		start_response('200 OK', [('content-type', 'text/html')])
		return ['<center> Welcome to Hot-Pi. </br> Call set/pi#/<number>/ to set a temp </br> Call get/pi# to get the temp</br> Call get_plan/pi# to get the policy</center>']

	elif PathList[1] == "set":

		pinum = PathList[2]
		temp = float(PathList[3])
		start_response('200 OK', [('content-type', 'text/xml')])
		pydict[pinum] = temp

		return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>'+ str(temp)+'</temp></pi>']


	elif PathList[1] == "set_ambient_temperature":

		pinum = PathList[2]
		temp = float(PathList[3])
		start_response('200 OK', [('content-type', 'text/xml')])
		pydictA[pinum] = temp

		return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><AmbientTemp>'+ str(temp)+'</AmbientTemp></pi>']


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

	else:
		start_response('200 OK', [('content-type', 'text/xml')])
		return ['<error> Not a valid request. For information about our API service please check our web site at http://www.intelligence.tuc.gr/renes. </error>']



if __name__ == '__main__':
	httpserver.serve(app, host='152.78.200.94', port='11884')

