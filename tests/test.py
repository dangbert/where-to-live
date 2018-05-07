import requests
import json
import pymysql

#https:#stackoverflow.com/questions/23226074/simulating-ajax-post-call-using-python-requests
#https:#stackoverflow.com/questions/31824222/python-request-post-to-php-server

def main():
	#data = formatData(False,0,False,0,False,0,True,True,True,True,True,True,True,True,False,0,0,0,False,0,False,60)
	data = {"schools":{"enabled":False,"value":0},"transportation":{"enabled":False,"value":0},"crime":{"enabled":False,"value":0},"recreation":{"enabled":True,"value":{"has_biking":True,"has_climbing":True,"has_camping":True,"has_hiking":True,"has_hunting":True,"has_wilderness":True,"has_swimming":True}},"climate":{"enabled":False,"value":{"temperature":0,"precipitation":0,"snowfall":0}},"healthcare":{"enabled":False,"value":0},"commute":{"enabled":False,"value":60}}
	# TO DO: fix buildQuery function
	sql = buildQuery(data)
	print(sql)
	#TO DO: write function to compare results from search and database query
	#cmpSearchDatabase()
	

#some functions to help with database connection
def getConnection():
	return pymysql.connect(host='localhost',
		user='code_fury',
		password='devpassword',
		db='code_fury')
		
		
def dbResults():
	connection = getConnection()
	try:
		with connection.cursor() as cursor:
			sql = "SELECT * from counties limit 10"
			cursor.execute(sql)
			result = cursor.fetchall()
			return result
 
	finally:
		connection.close()

def callSearch(data):
	url = 'http:#localhost/code_fury/controllers/search.php'
	
	headers = requests.utils.default_headers()
	#headers = {'content-type': 'application/json'} 

	s = requests.Session()

	#post request for search
	resp = s.post(url, data = json.dumps(data), headers = headers)
	#print(resp.text)
	
	print(resp.json()[0])
	
def buildQuery(data):
	first = True
	sql = ""
	# build the condition portion of the sql query string
    # SCHOOLS (0: low, 1: medium, 2:high)
	if (data["schools"]["enabled"] == True):
		sql += prepareCondition(data["schools"]["value"], ranges, "schools", "public_schools")
		first = False
    
    # TRANSPORTATION (0: low, 1: medium, 2: average)
	if (data["transportation"]["enabled"] == True):
		sql += ("" if first else " and ")
		sql += prepareCondition(data["transportation"]["value"], ranges, "transportation", "public_trans")
		first = False
    
    # CRIME (0: low, 1: average)
    # TODO: do we want "average" to include low as well?
	if (data["crime"]["enabled"] == True):
		sql += ("" if first else " and ")
		sql += prepareCondition(data["crime"]["value"], ranges, "crime", "crime_rates")
		first = False
		
    # CLIMATE
	if (data["climate"]["enabled"] == True):
        # TEMPERATURE (0: no preference, 1: hotter, 2: colder)
		if (data["climate"]["value"]["temperature"] != 0):
			symbol = ("<=" if data["climate"]["value"]["temperature"] == 2 else ">")
			sql += ("" if first else " and ")
			sql += " (avg_temp symbol " + ranges["temperature"][0] + ")"
			first = False
        
        # PRECIPITATION (0: low, 1: medium, 2: high)
		sql += ("" if first else " and ")
		sql += prepareCondition(data["climate"]["value"]["precipitation"], ranges, "precipitation", "precipitation")
		first = False
        # SNOWFALL (0: low, 1: medium, 2: high)
		sql += ("" if first else " and ")
		sql += prepareCondition(data["climate"]["value"]["snowfall"], ranges, "snowfall", "snow")
		first = False
    
    # HEALTHCARE (0: average, 1: high)
	if (data["healthcare"]["enabled"] == True):
		symbol = ("<=" if data["healthcare"]["value"] == 0 else ">")
		sql += ("" if first else " and ")
		sql += " (healthcare symbol " + ranges["healthcare"][0] + ")"
		first = False
    
    # COMMUTE (value: int 0-60) (ensures commute is <= value)
	if (data["commute"]["enabled"] == True):
		sql += ("" if first else " and ")
		sql += " (commute_time <= " + data["commute"]["value"] + ")"
		first = False
    
    # RECREATION:
	if (data["recreation"]["enabled"] == True):
		activities = ["biking", "climbing", "camping", "hiking", "hunting", "wilderness", "swimming"]
		for value in activities:
			if (data["recreation"]["value"]["has_value"] == True):
				sql += ("" if first else " and ")
				sql += "(value >= 1)"
				first = False
            
    # this part of the query combines the tables (counties, states, recareas) into a table of rows of counties with the added fields state (state name) and fields for the number of recareas in the county that provide each rec activity
	combineQuery = "(SELECT counties.*, states.name as state from counties join states on counties.state_id = states.id) t1 LEFT JOIN (select county_id, sum(has_biking) as biking, sum(has_climbing) as climbing, sum(has_camping) as camping, sum(has_hiking) as hiking, sum(has_hunting) as hunting, sum(has_wilderness) as wilderness, sum(has_swimming) as swimming from recareas group by county_id) t2 ON t1.id = t2.county_id"
					
    # final query string, apply the conditions to the combined table and just get the state and county name of the results
	sql = "SELECT state, name as county, public_schools, public_trans, commute_time, crime_rates, healthcare, precipitation, avg_temp, snow, biking, climbing, camping, hiking, hunting, wilderness, swimming, lat, lng FROM (combineQuery) WHERE sql"
    #echo sql . "\n\n"
	
#create portion of search string for given column
#value:  int value representing the search preference
#ranges: array of predefined ranges for the possible values
#label:  name of key in ranges array
#col:    name of column in counties table
def prepareCondition(value, ranges, label, col):
	str = "";
	#value = data[label]["value"]
	if (value == 0):
		str += " (col < " + ranges[label][0] + ")"
	
	if (value == 1):
		str += " (col > " + ranges[label][0] + " and $col < " + ranges["label"][1] + ")"
	
	if (value == 2):
		str += " (col >= " + ranges[label][1] + ")"
	
	return str;
	


ranges = {"schools":{
			0: 0.84,							# low:     values <= [0]        (33rd percentile)
            1: 0.907                          	# medium:  [0] < values < [1]   (66th percentile)
												# high:    values >= [1]
		},
        "transportation":{
            0 :	0.0018959374599999991,         # low:     values <= [0]        (33rd percentile)
            1 : 0.005931874919999998           # medium:  [0] < values < [1]   (66th percentile)
                                                # high:    values >= [1]
        },
        "crime" :{
            0 : 142.4358816,                   # low:     values <= [0]        (33rd percentile)
            1 : 275.06529279999995             # average: [0] < values < [1]   (66th percentile)
        },
        "temperature":{
            0: 544.5,                         # colder:  values <= [0]        (50th percentile)
                                                # hotter:  values > [0]
        },
        "precipitation" :{
            0: 3408.4737999999998,            # low:     values <= [0]        (33rd percentile)
            1 : 4620.48952                     # medium:  [0] < values < [1]   (66th percentile)
                                                # high:    values >= [1]
        },
        "snowfall":{
            0 : 51.98951999999986,             # low:     values <= [0]        (33rd percentile)
            1 : 266.374                        # medium:  [0] < values < [1]   (66th percentile)
                                                # high:    values >= [1]
        },
        "healthcare" :{
            0 : 64.0,                          # average: values <= [0]        (66th percentile)
                                                # high:    values > [1]
        }
    }

'''
def formatData(sch_enb, sch_val, trans_enb, trans_val, cri_enb, cri_val,
				rec_enb, rec_bike, rec_clim, rec_camp, rec_hik, rec_hunt, 
				rec_wild, rec_swim, clim_enb, clim_temp, clim_prec, clim_snow, 
				health_enb, health_val, comm_enb, comm_val):
	data = {"schools":{
				"enabled":sch_enb,
				"value":sch_val
			},
			"transportation":{
				"enabled":trans_enb,
				"value":trans_val
			},
			"crime":{
				"enabled":cri_enb,
				"value":cri_val
			},
			"recreation":{
				"enabled":rec_enb,
				"value":{
					"has_biking":rec_bike,
					"has_climbing":rec_clim,
					"has_camping":rec_camp,
					"has_hiking":rec_hik,
					"has_hunting":rec_hunt,
					"has_wilderness":rec_wild,
					"has_swimming":rec_swim
				}
			},
			"climate":{
				"enabled":clim_enb,
				"value":{
					"temperature":clim_temp,
					"precipitation":clim_prec,
					"snowfall":clim_snow
				}
			},
			"healthcare":{
				"enabled":health_enb,
				"value":health_val
			},
			"commute":{
				"enabled":comm_enb,
				"value":comm_val
			}
	}
	return data
'''

if __name__ == "__main__":
	main()
