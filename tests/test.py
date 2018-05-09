import requests
import json
import pymysql
import subprocess
import csv
import time

#https:#stackoverflow.com/questions/23226074/simulating-ajax-post-call-using-python-requests
#https:#stackoverflow.com/questions/31824222/python-request-post-to-php-server

def main():
	#data = formatData(False,0,False,0,False,0,True,True,True,True,True,True,True,True,False,0,0,0,False,0,False,60)
	data = {"schools":{"enabled":False,"value":0},"transportation":{"enabled":False,"value":0},"crime":{"enabled":False,"value":0},"recreation":{"enabled":True,"value":{"has_biking":True,"has_climbing":True,"has_camping":True,"has_hiking":True,"has_hunting":True,"has_wilderness":True,"has_swimming":True}},"climate":{"enabled":False,"value":{"temperature":0,"precipitation":0,"snowfall":0}},"healthcare":{"enabled":False,"value":0},"commute":{"enabled":False,"value":60}}
	
	callSearch(data)
	weather_test()
	datausa_test()
	
	
	
def weather_test():
	#creates a DictReader of all our hardcoded testdata
	manualData = csv.DictReader(open('ManualCountyData.csv', 'r'))
	try:
		for row in manualData:
			result = weatherResults(row['countyName'], row['state'])
			assert result[0] == float(row['precipitation'])
			assert result[1] == float(row['avg_temp'])
			assert result[2] == float(row['snow'])
		print("Weather Test Passed")
	except:
		print("Weather Test Failed")
		

#TO DO: compare csv 
def datausa_test():
	manualData = csv.DictReader(open('ManualCountyData.csv', 'r'))
	
	#This returns None in the loop
	#result = callTestPhp('05000US05043')
	#print(result)
	
	#I dont know why the last 5 ish 
	for row in manualData:
		result = callTestPhp(row['geo_id'])
		print(result)
		#print(row['geo_id'])
		#result = callTestPhp('05000US35061')
		#print(result)
			#assert result[0] == float(row['precipitation'])
			#assert result[1] == float(row['avg_temp'])
			#assert result[2] == float(row['snow'])
		
	#except:
	#	print("Failed")

	
#some functions to help with database connection
def getConnection():
	return pymysql.connect(host='localhost',
		user='code_fury',
		password='devpassword',
		db='code_fury')
		

def weatherResults(countyName, state):
	connection = getConnection()
	try:
		with connection.cursor() as cursor:
			sql = """SELECT precipitation, avg_temp, snow from counties where name =%s and state_id = (select id from states where name = %s);"""
			cursor.execute(sql, (countyName, state))
			result = cursor.fetchone()
			return result
 
	finally:
		connection.close()
	
def dbResults(countyName, state):
	connection = getConnection()
	try:
		with connection.cursor() as cursor:
			sql = """SELECT * from counties where name =%s and state_id = (select id from states where name = %s);"""
			cursor.execute(sql, (countyName, state))
			result = cursor.fetchall()
			return result
 
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
 
# TO DO: run test.php and get results
def callTestPhp(geo_id):
	#proc = subprocess.call(["php /code_fury/controllers/test.php", '05000US19001'])
	url = 'http://localhost/code_fury/controllers/test.php?geo_id=' + geo_id
	#print(url)
	s = requests.Session()
	headers = requests.utils.default_headers()
	resp = s.get(url)
	
	if resp.status_code == 200:
		return(resp.json())
	else:
		return 'error'
	
	
if __name__ == "__main__":
	main()
