import requests
import json
import pymysql

#https:#stackoverflow.com/questions/23226074/simulating-ajax-post-call-using-python-requests
#https:#stackoverflow.com/questions/31824222/python-request-post-to-php-server

def main():
	#data = formatData(False,0,False,0,False,0,True,True,True,True,True,True,True,True,False,0,0,0,False,0,False,60)
	data = {"schools":{"enabled":False,"value":0},"transportation":{"enabled":False,"value":0},"crime":{"enabled":False,"value":0},"recreation":{"enabled":True,"value":{"has_biking":True,"has_climbing":True,"has_camping":True,"has_hiking":True,"has_hunting":True,"has_wilderness":True,"has_swimming":True}},"climate":{"enabled":False,"value":{"temperature":0,"precipitation":0,"snowfall":0}},"healthcare":{"enabled":False,"value":0},"commute":{"enabled":False,"value":60}}
	callSearch(data)
	dbResults()
	#print(sql)
	#TO DO: write function to compare results from search and database query
	#cmpSearchDatabase()
	

#some functions to help with database connection
def getConnection():
	return pymysql.connect(host='localhost',
		user='code_fury',
		password='devpassword',
		db='code_fury')
		
		
def dbResults(countyName, state):
	connection = getConnection()
	try:
		with connection.cursor() as cursor:
			sql = """SELECT * from counties where name =%s and state_id = (select id from states where name = %s);"""
			cursor.execute(sql)
			result = cursor.fetchall()
			print(result)
 
	finally:
		connection.close()

def callSearch(data):
	url = 'http://localhost/code_fury/controllers/search.php'
	
	headers = requests.utils.default_headers()
	#headers = {'content-type': 'application/json'} 

	s = requests.Session()

	#post request for search
	resp = s.post(url, data = json.dumps(data), headers = headers)
	#print entire result
	print(resp.text)
	#prints the first result
	#print(resp.json()[0])


if __name__ == "__main__":
	main()
