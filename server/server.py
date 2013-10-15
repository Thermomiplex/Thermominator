######################################################################
#                         RnCrete Server                             #
######################################################################

from paste.request import parse_formvars #Server imports
from paste import httpserver #Server imports
import ntplib, datetime #for utc timestamp
#import modules.makeresponce as makeresponce #Modules imports

import re # Parse String (url path)
import string # Parse String (url path)

pydict = {}
def app(environ, start_response):
  fields = parse_formvars(environ)

  path = environ['PATH_INFO']
  Separators = re.compile('/')
  PathList = Separators.split(path)
  #print len(PathList)


  if path == "/":

    start_response('200 OK', [('content-type', 'text/html')])
    return ['<center> Welcome to Hot-Pi. </br> Call /pi#/set/<number> to set a temp </br> Call /pi#/get to get the temp</center>']

  elif PathList[1] == "set":

    ############################ Fields and time catcher #####################################
    pinum = PathList[2]
    temp = float(PathList[3])
    start_response('200 OK', [('content-type', 'text/xml')])
    pydict[pinum] = temp

    return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>'+ str(temp)+'</temp></pi>']

  elif PathList[1] == "get":

    start_response('200 OK', [('content-type', 'text/xml')])

    pinum = PathList[2]
    if pinum in pydict:
      return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>'+ str(pydict[pinum])+'</temp></pi>']
    else:
      return ['<pi>'+'<pinumber>'+str(pinum)+'</pinumber><temp>NO TEMP</temp></pi>']
    return [responseHtml]

  else:

    start_response('200 OK', [('content-type', 'text/xml')])
    return ['<error> Not a valid request. For information about our API service please check our web site at http://www.intelligence.tuc.gr/renes. </error>']



if __name__ == '__main__':
  httpserver.serve(app, host='127.0.0.1', port='11884')

