import requests
import json

#https://stackoverflow.com/questions/23226074/simulating-ajax-post-call-using-python-requests
#https://stackoverflow.com/questions/31824222/python-request-post-to-php-server
url = 'http://localhost/code_fury/controllers/search.php'
data = {"schools":{"enabled":False,"value":0},"transportation":{"enabled":False,"value":0},"crime":{"enabled":False,"value":0},"recreation":{"enabled":True,"value":{"has_biking":True,"has_climbing":True,"has_camping":True,"has_hiking":True,"has_hunting":True,"has_wilderness":True,"has_swimming":True}},"climate":{"enabled":False,"value":{"temperature":0,"precipitation":0,"snowfall":0}},"healthcare":{"enabled":False,"value":0},"commute":{"enabled":False,"value":60}}
#headers = {'User-Agent': "test.py", 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

#headers = requests.utils.default_headers()
headers = {'content-type': 'application/json'} 

s = requests.Session()
resp = s.post(url, data = json.dumps(data), headers = headers)

print(resp.text)