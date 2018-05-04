
# coding: utf-8

# In[39]:


#https://gist.github.com/shanealynn/033c8a3cacdba8ce03cbe116225ced31


# In[53]:


import pandas as pd
import requests
import logging
import time
import MySQLdb


# In[54]:


API_KEY = 'AIzaSyAbzToWwyvwuRG5xYmLdH11JYVfF7x_2aE'


# In[55]:


db = MySQLdb.connect(user="code_fury", passwd="devpassword", db="code_fury")
c = db.cursor()


# In[62]:


#add columns for lat/lng of each county
def addlatlngCol():
    add_latlng = """ALTER TABLE counties 
                        ADD lat FLOAT(10), 
                        ADD lng FLOAT(10);"""
    c.execute(add_latlng)
    db.commit()


# In[63]:


#drop columns for lat/lng of each county
def droplatlngCol():
    drop_latlng = """ALTER TABLE counties 
                        DROP COLUMN lat, 
                        DROP COLUMN lng;"""
    c.execute(drop_latlng)
    db.commit()


# In[24]:


#DONT NEED THIS
# Build list of counties to geocode
#searchList = []
#count = 0
#for county in res:
#    searchString = county[0] + ' ' + county[1]
#    searchList.append(searchString)
#    count+=1
#print(searchList)
#print(count)'''


# In[59]:


def insertIntoDatabase(county, state, lat, long):
    latlong = """UPDATE counties 
                    SET lat = %s, lng = %s 
                    WHERE name = %s AND state_id = (select id from states where name = %s);"""
    c.execute(latlong, (lat, long, county, state))
    db.commit()


# In[60]:


#from https://gist.github.com/shanealynn/033c8a3cacdba8ce03cbe116225ced31
def get_google_results(address, api_key):
    """
    Get geocode results from Google Maps Geocoding API.
    
    Note, that in the case of multiple google geocode reuslts, this function returns details of the FIRST result.
    
    @param address: String address as accurate as possible. For Example "18 Grafton Street, Dublin, Ireland"
    @param api_key: String API key if present from google. 
                    If supplied, requests will use your allowance from the Google API. If not, you
                    will be limited to the free usage of 2500 requests per day.
    @param return_full_response: Boolean to indicate if you'd like to return the full response from google. This
                    is useful if you'd like additional location details for storage or parsing later.
    """
    # Set up your Geocoding url
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)
    if api_key is not None:
        geocode_url = geocode_url + "&key={}".format(api_key)
        
    # Ping google for the reuslts:
    results = requests.get(geocode_url)
    # Results will be in JSON format - convert to dict using requests functionality
    results = results.json()
    
    # if there's no results or an error, return empty results.
    if len(results['results']) == 0:
        output = {
            #"formatted_address" : None,
            "latitude": None,
            "longitude": None
            #"accuracy": None,
            #"google_place_id": None,
            #"type": None,
            #"postcode": None
        }
    else:    
        answer = results['results'][0]
        output = {
            #"formatted_address" : answer.get('formatted_address'),
            "latitude": answer.get('geometry').get('location').get('lat'),
            "longitude": answer.get('geometry').get('location').get('lng')
            #"accuracy": answer.get('geometry').get('location_type'),
            #"google_place_id": answer.get("place_id"),
            #"type": ",".join(answer.get('types')),
            #"postcode": ",".join([x['long_name'] for x in answer.get('address_components') 
            #                      if 'postal_code' in x.get('types')])
        }
        
    # Append some other details:    
    output['input_string'] = address
    output['number_of_results'] = len(results['results'])
    output['status'] = results.get('status')
    #if return_full_response is True:
    #    output['response'] = results
    
    return output


# In[36]:


#test_result = get_google_results(res[0], API_KEY)
#if (test_result['status'] != 'OK'):
#    logger.warning("There was an error when testing the Google Geocoder.")
#    raise ConnectionError('Problem with test results from Google Geocode - check your API key and internet connection.')
#print(test_result)


# In[51]:


#loop through searchList and geocode each county until we hit the limit
def get_latlong(api_key):
    getCounties = """SELECT counties.name, states.name
                    FROM counties, states WHERE
                    counties.state_id = states.id;"""
    c.execute(getCounties)
    res = c.fetchall()
    for county in res:
        result = get_google_results(county, api_key)
        if result['status'] == 'OVER_QUERY_LIMIT':
            break
        insertIntoDatabase(result['input_string'][0], result['input_string'][1], result['latitude'], result['longitude'])


# In[61]:


def get_rest(api_key):
    getNullCounties = """SELECT counties.name, states.name
                    FROM counties, states WHERE
                    (counties.state_id = states.id) AND
                    (counties.lat is NULL OR counties.lng is NULL);"""
    c.execute(getNullCounties)
    res = c.fetchall()
    #print(res)
    for county in res:
        result = get_google_results(county, api_key)
        if result['status'] == 'OVER_QUERY_LIMIT':
            break
        insertIntoDatabase(result['input_string'][0], result['input_string'][1], result['latitude'], result['longitude'])


# In[ ]:


#Run this
#addlatlngCol()
#droplatlngCol()
#get_latlong(API_KEY)
#get_rest(API_KEY)

