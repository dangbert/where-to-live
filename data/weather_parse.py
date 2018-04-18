
# coding: utf-8

# In[60]:


import pandas as pd
from functools import reduce


# In[76]:


tmax = pd.read_csv("ann-tmax-normal.csv", header = None)
tmax.columns = ["station_id", "orig_tmax", "t_max"]
tmax = tmax.drop(columns = ['orig_tmax'])
#print(tmax)


# In[77]:


tmin = pd.read_csv("ann-tmin-normal.csv", header = None)
tmin.columns = ["station_id", "orig_tmin", "t_min"]
tmin = tmin.drop(columns = ['orig_tmin'])
#print(tmin)


# In[78]:


precip = pd.read_csv("ann-prcp-normal.csv", header = None)
precip.columns = ["station_id", "orig_precip", "precip"]
precip = precip.drop(columns = ['orig_precip'])
#print(precip)


# In[79]:


zip_norm = pd.read_csv("zipcodes-normals-stations.csv", header = None)
zip_norm.columns = ["station_id", "zip", "po_name"]
zip_norm = zip_norm.drop(columns = ['po_name'])
#print(zip_norm)


# In[80]:


weather_dat = [tmax, tmin, precip, zip_norm]

#https://stackoverflow.com/questions/23668427/pandas-joining-multiple-dataframes-on-columns
weather_dat = reduce(lambda left,right: pd.merge(left,right,on='station_id'), weather_dat)
#print(weather_dat)


# In[91]:

# Data from: https://www.unitedstateszipcodes.org/zip-code-database/
zip_county = pd.read_csv("zip_county.csv", encoding = 'latin-1')
zip_county = zip_county.drop(columns = ['country', 'type', 'decommissioned', 'primary_city', 'acceptable_cities', 'unacceptable_cities', 'timezone', 'area_codes', 'world_region', 'latitude', 'longitude', 'irs_estimated_population_2015', 'timezone'])
#print(zip_county)


# In[93]:


final= weather_dat.merge(zip_county, on= 'zip')
print(final.head(10))

