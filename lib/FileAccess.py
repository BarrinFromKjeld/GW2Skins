import os.path
import json

##########################################
#              File Access               #
##########################################
def getStrFromFile (fileName):
	content = ''
	if(os.path.exists(fileName)):
		with open (fileName,'r') as file:
			content = file.read()
	#else:
		#throw ('File {} not found'.format(fileName))
	return content

def getBinFromFile (fileName):
	content = b''
	if(os.path.exists(fileName)):
		with open (fileName,'rb') as file:
			content = file.read()
	#else:
		#throw ('File {} not found'.format(fileName))
	return content

def writeBinToFile (fileName, content):
	#print 'Writing to {}'.format(fileName)
	with open (fileName,'wb') as file:
		file.truncate()
		file.write(content)
		
def getObjectsFromJSONFile (fileName):
	objects = []
	if(os.path.exists(fileName)):
		with open (fileName,'r') as file:
			objects = json.load(file)
	#else:
		#throw ('File {} not found'.format(fileName))
	return objects

def writeJSONToFile (fileName, object):
	#print 'Writing to {}'.format(fileName)
	with open (fileName,'w') as file:
		file.truncate()
		json.dump(object,file)