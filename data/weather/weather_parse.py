# Reads in weather csv data, merges, groups by state, county and inserts into database
# Also replaces nulls with average from entire state
import pandas as pd

# Ran this from jupyter notebook
# I couldn't couldn't figure out how to get MySQLdb installed on my computer
import MySQLdb
from functools import reduce


def main():
    # read in weather data csvs, returns table with mean data for each county
    groupedCounties = readCsv()

    # drop the columns if you already have them and want to readd
    #dropCols()

    # insert data into database and update null data with average for state
    insertData(groupedCounties)


def readCsv():
    '''
    tmax = pd.read_csv("ann-tmax-normal.csv", header = None)
    tmax.columns = ["station_id", "orig_tmax", "t_max(0.1F)"]
    tmax = tmax.drop(columns = ['orig_tmax'])
    #print(tmax)


    tmin = pd.read_csv("ann-tmin-normal.csv", header = None)
    tmin.columns = ["station_id", "orig_tmin", "t_min(0.1F)"]
    tmin = tmin.drop(columns = ['orig_tmin'])
    #print(tmin)
    '''

    precip = pd.read_csv("ann-prcp-normal.csv", header = None)
    precip.columns = ["station_id", "orig_precip", "precip(0.01in)"]
    precip = precip.drop(columns = ['orig_precip'])
    #print(precip)


    snow = pd.read_csv("ann-snow-normal.csv", header = None)
    snow.columns = ["station_id", "orig_snow", "snow(0.1in)"]
    snow = snow.drop(columns = ['orig_snow'])
    #print(snow)


    tavg = pd.read_csv("ann-tavg-normal.csv", header = None)
    tavg.columns = ["station_id", "orig_tavg", "t_avg(0.1F)"]
    tavg = tavg.drop(columns = ['orig_tavg'])
    #print(tavg)


    zip_norm = pd.read_csv("zipcodes-normals-stations.csv", header = None)
    zip_norm.columns = ["station_id", "zip", "po_name"]
    zip_norm = zip_norm.drop(columns = ['po_name'])
    #print(zip_norm)

    # merge csvs on station_id(so we have zip code)

    weather_dat = [zip_norm, precip, tavg, snow]
    weather_dat = reduce(lambda left,right: pd.merge(left,right, how = 'outer', on='station_id'), weather_dat)
    #print(weather_dat)


    zip_county = pd.read_csv("zip_county.csv", encoding = 'latin-1')
    zip_county = zip_county.drop(columns = ['country', 'type', 'decommissioned', 'primary_city', 'acceptable_cities', 'unacceptable_cities', 'timezone', 'area_codes', 'world_region', 'latitude', 'longitude', 'irs_estimated_population_2015', 'timezone'])
    #print(zip_county)


    #
    final= weather_dat.merge(zip_county, on= 'zip')

    # replace non-zero values that round to 0
    final = final.replace(to_replace =-7777.0, value = 0.0)
    #print(final)

    #df = final.groupby(['county', 'state'])['station_id'].nunique()
    #print(df)


    grouped = final.groupby(['county', 'state']).mean()
    # grouped_merge = grouped.merge(stateid, on= 'state')
    # print(grouped)
    return grouped


def insertData(groupedCounties):
    # connect to databasese
    db = MySQLdb.connect(user="code_fury", passwd="devpassword", db="code_fury")
    c = db.cursor()


    #add columns for weather info
    add_weather_col = """ALTER TABLE counties 
                            ADD precipitation FLOAT(6), 
                            ADD avg_temp FLOAT(6), 
                            ADD snow FLOAT(6);"""
    c.execute(add_weather_col)
    db.commit()

    set_precip = """UPDATE counties
                SET precipitation = %s
                WHERE name = %s AND state_id = (select id from states where name = %s);"""
    set_avg_temp = """UPDATE counties
                SET avg_temp = %s
                WHERE name = %s AND state_id = (select id from states where name = %s);"""
    set_snow = """UPDATE counties
                SET snow = %s
                WHERE name = %s AND state_id = (select id from states where name = %s);"""

    # wont update for PR and when no data
    for county, state in groupedCounties.iterrows():
        z = county,state 		#z[0] = (county, state abbrev), z[1][1] = precipitation, z[1][2] = avg_temp, z[1][3] = snowfall
        # try to update precipitation
        try:
            c.execute(set_precip, (z[1][1], z[0][0], stateAbrevs[z[0][1]]))
            db.commit()
            #print(z[1][1], z[0][0], stateAbrevs[z[0][1]])
        except:
            print("COULD NOT UPDATE precip: ", z[1][1], z[0][0], z[0][1])

        # try to update avg_temp
        try:
            c.execute(set_avg_temp, (z[1][2], z[0][0], stateAbrevs[z[0][1]]))
            db.commit()
            #print(z[1][2], z[0][0], stateAbrevs[z[0][1]])
        except:
            print("COULD NOT UPDATE avg_temp: ", z[1][2], z[0][0], z[0][1])

        # try to update snow
        try:
            c.execute(set_snow, (z[1][3], z[0][0], stateAbrevs[z[0][1]]))
            #print(z[1][3], z[0][0], stateAbrevs[z[0][1]])
            db.commit()
        except:
            print("COULD NOT UPDATE snow: ", z[1][3], z[0][0], z[0][1])
            continue

    # fill in null weather values with state-wide average
    fix_null_precip = """UPDATE counties
                SET precipitation = %s
                WHERE precipitation is NULL AND state_id = %s;"""
    fix_null_temp = """UPDATE counties
                SET avg_temp = %s
                WHERE avg_temp is NULL AND state_id = %s;"""
    fix_null_snow = """UPDATE counties
                SET snow = %s
                WHERE snow is NULL AND state_id = %s;"""

    #c.execute("select count(*) from states;")
    #state_rows = c.fetchone()[0]
    #print(state_rows)

    # compute average snow, precipitation and temp for each state
    c.execute("select avg(precipitation), avg(avg_temp), avg(snow), state_id from counties group by state_id;")
    res = c.fetchall() 		#[avg(precipitation), avg(temp), avg(snow), state_id)]
    #print(res)
    for i in res:
        #print(i)
        c.execute(fix_null_precip, (i[0], i[3]))
        c.execute(fix_null_temp, (i[1], i[3]))
        c.execute(fix_null_snow, (i[2], i[3]))
        db.commit()


def dropCols():
    db = MySQLdb.connect(user="code_fury", passwd="devpassword", db="code_fury")
    c = db.cursor()

    # drop columns for weather info
    drop_weather_col = """ALTER TABLE counties
                DROP COLUMN precipitation,
                DROP COLUMN avg_temp,
                DROP COLUMN snow;"""

    c.execute(drop_weather_col)
    db.commit()

stateAbrevs = {}
stateAbrevs["AL"] = "Alabama"
stateAbrevs["AK"] = "Alaska"
stateAbrevs["AZ"] = "Arizona"
stateAbrevs["AR"] = "Arkansas"
stateAbrevs["CA"] = "California"
stateAbrevs["CO"] = "Colorado"
stateAbrevs["CT"] = "Connecticut"
stateAbrevs["DE"] = "Delaware"
stateAbrevs["FL"] = "Florida"
stateAbrevs["GA"] = "Georgia"
stateAbrevs["HI"] = "Hawaii"
stateAbrevs["ID"] = "Idaho"
stateAbrevs["IL"] = "Illinois"
stateAbrevs["IN"] = "Indiana"
stateAbrevs["IA"] = "Iowa"
stateAbrevs["KS"] = "Kansas"
stateAbrevs["KY"] = "Kentucky"
stateAbrevs["LA"] = "Louisiana"
stateAbrevs["ME"] = "Maine"
stateAbrevs["MD"] = "Maryland"
stateAbrevs["MA"] = "Massachusetts"
stateAbrevs["MI"] = "Michigan"
stateAbrevs["MN"] = "Minnesota"
stateAbrevs["MS"] = "Mississippi"
stateAbrevs["MO"] = "Missouri"
stateAbrevs["MT"] = "Montana"
stateAbrevs["NE"] = "Nebraska"
stateAbrevs["NV"] = "Nevada"
stateAbrevs["NH"] = "New Hampshire"
stateAbrevs["NJ"] = "New Jersey"
stateAbrevs["NM"] = "New Mexico"
stateAbrevs["NY"] = "New York"
stateAbrevs["NC"] = "North Carolina"
stateAbrevs["ND"] = "North Dakota"
stateAbrevs["OH"] = "Ohio"
stateAbrevs["OK"] = "Oklahoma"
stateAbrevs["OR"] = "Oregon"
stateAbrevs["PA"] = "Pennsylvania"
stateAbrevs["RI"] = "Rhode Island"
stateAbrevs["SC"] = "South Carolina"
stateAbrevs["SD"] = "South Dakota"
stateAbrevs["TN"] = "Tennessee"
stateAbrevs["TX"] = "Texas"
stateAbrevs["UT"] = "Utah"
stateAbrevs["VT"] = "Vermont"
stateAbrevs["VA"] = "Virginia"
stateAbrevs["WA"] = "Washington"
stateAbrevs["WV"] = "West Virginia"
stateAbrevs["WI"] = "Wisconsin"
stateAbrevs["WY"] = "Wyoming"
# also include DC and Puerto Rico
#stateAbrevs["PR"] = "Puerto Rico"
stateAbrevs["DC"] = "District of Columbia"

if __name__ == "__main__":
    main()