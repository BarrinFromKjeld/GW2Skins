import json
import requests

defaultParams   = {'lang': 'en'}
defaultHeaders  = {}

##########################################
#               XHR Access               #
##########################################
def getBinViaXHR (url,params=defaultParams,headers=defaultHeaders):
	#print 'Request: {}, {}, {}'.format(url,params,headers)
	response = requests.get(url, params=params, headers=headers)
	if (response.status_code == 200):
		return response.content
	else:
		print "Error during XHR {}: {}".format(url,str(response.status_code))
		return ''
	return

def getJSONObjectsViaXHR (url,params=defaultParams,headers=defaultHeaders):
	#print 'Request: {}, {}, {}'.format(url,params,headers)
	response = requests.get(url, params=params, headers=headers)
	if (response.status_code == 200):
		return response.json()
	else:
		print "Error during XHR {}: {}".format(url,str(response.status_code))
		return {}
	return

def getJSONObjectsViaXHRbyId(baseUrl,id,params=defaultParams,headers=defaultHeaders):
	url = baseUrl
	url += '/'
	url += str(id)
	return getJSONObjectsViaXHR(url,params,headers)

def getJSONObjectsViaXHRbyIdList(baseUrl,idList,params=defaultParams,headers=defaultHeaders,singleRequest=False):
	if (singleRequest):
		idListStr=''
		first=True
		for id in idList:
			if (not(first)):
				idListStr += ','
			else:
				first = False
			idListStr += str(id)
		#params["ids"] = idListStr
		url = baseUrl
		url += '?ids='
		url += idListStr
		return getJSONObjectsViaXHR(url,params,headers)
	else:
		objects = []
		i = 0
		aim = len(idList)
		for id in idList:
			i += 1
			#print 'Single-Request {} of {}'.format(i,aim)
			objects.append(getJSONObjectsViaXHRbyId(baseUrl,id,params,headers))
		return objects