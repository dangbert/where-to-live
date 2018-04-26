#!/usr/bin/env python3
import csv
# had to use virtual env to get working: (mysqlclient==1.3.12)
import MySQLdb  # https://github.com/PyMySQL/mysqlclient-python

# this script reads in info about rec areas from (modified) csv files downloaded from https://ridb.recreation.gov/
# and adds them to a new table in the database called 'recareas'
# also removes Puerto Rico from the database
def main():
    # create list of locations of rec centers
    allLocs = getLocations()
    print(str(len(allLocs)) + " total locations processed")

    # populate the county field in the locations and remove invalid locations
    validateLocations(allLocs)
    print(str(len(allLocs)) + " total locations remaining after validation")

    # now connect to the database and insert this data
    updateDatabase(allLocs)


# https://mysqlclient.readthedocs.io/user_guide.html#introduction
def updateDatabase(allLocs):
    # connect to database
    db = MySQLdb.connect(user="code_fury", passwd="devpassword", db="code_fury")
    c = db.cursor()                             # needed to query

    # check DB version
    c.execute("SELECT version FROM db_version order by id desc limit 1")
    res = c.fetchone()
    if res == None or res[0] != 2:
        print("\nthis script is meant to be run on db version 2. Aborting")
        return

    # drop puerto Rico from tables
    c.execute("delete from states where id=28;")
    c.execute("delete from counties where state_id=28;")

    # fix name of Dona Ana County in database (the 'n' was a special character)
    c.execute("update counties set name = 'Dona Ana County' where id=483;")

    # create new table recareas
    sql = """
    CREATE table recareas(
    id INT( 11 ) AUTO_INCREMENT PRIMARY KEY,
    entity_id INT( 11 ) NOT NULL,
    county_id INT( 11 ) NOT NULL,
    has_biking INT( 1) NOT NULL,
    has_climbing INT( 1 ) NOT NULL,
    has_camping INT( 1) NOT NULL,
    has_hiking INT( 1) NOT NULL,
    has_hunting INT( 1) NOT NULL,
    has_wilderness INT( 1) NOT NULL,
    has_swimming INT( 1) NOT NULL);
    """
    c.execute(sql);
    db.commit()

    # iterate over all the locations and insert them into recareas
    for loc in allLocs:
        c.execute("select * from states where name = %s", (stateAbrevs[loc.state],))
        res = c.fetchone()
        if res != None:
            state_id = int(res[0])

            if loc.county == "Carson City":     # special case: handle "Carson City"
                loc.county = "Carson City County"

            if loc.zip in [88005, 88001, 88052]:# special case: handle locations with incompatible character
                #print("special case " + loc.county + ", " + loc.state)
                # 483 is the id of Dona Ana county (special character on n)
                county_id = 483
            else:
                # get the id of this county in the database
                c.execute("select * from counties where state_id = %s and name = %s", (state_id, loc.county,))
                res = c.fetchone()
                if res != None:
                    county_id = int(res[0])
                else:
                    print("couldn't find: " + loc.county + ", " + loc.state + " (skipping)")
                    continue

            # now make use of county_id (insert this loc into the database)
            sql = "insert into recareas (entity_id, county_id, has_biking, has_climbing, has_camping, has_hiking, has_hunting, has_wilderness, has_swimming) values (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            # (the IDs for each activity are defined in Activities_API_v1.csv)
            # 5: biking,    7: climbing,     9: camping, 14: hiking
            # 16: hunting, 28: wilderness, 106: swimming
            c.execute(sql, (loc.ID, county_id, int(5 in loc.activities), int(7 in loc.activities), int(9 in loc.activities), int(14 in loc.activities), int(16 in loc.activities), int(28 in loc.activities), int(106 in loc.activities),))

    # update DB version
    c.execute("insert into db_version(version) values(3);")
    # commit changes to database
    db.commit()
    print("Upgraded database to version 3.")


# populate the county field for each location
# and remove locations where the zipcode is invalid or doesn't agree with the state
def validateLocations(allLocs):
    # create zip map:
    zipMap = getZipMap()

    # match each location to its corresponding county:
    i = 0
    while 1:
        if i >= len(allLocs):
            break

        # check if this location's zipcode corresponds to a county
        if allLocs[i].getZipString() not in zipMap:
            # zipcode is invalid (happens to 29 of the locations)
            del allLocs[i]                      # discard this location
            continue

        pair = zipMap[allLocs[i].getZipString()]
        # make sure zipcode matches the given state (and the state is valid)
        if pair[0] != allLocs[i].state or pair[0] not in stateAbrevs:
            # (happens to 41 locations) (likely zipcode typos in the provided data)
            del allLocs[i]                      # discard this location
            continue
        allLocs[i].county = pair[1]
        i += 1

# read from the zip_count.csv file and create a dict mapping zip codes to (state, county) objects
def getZipMap():
    zmap = dict()
    with open('zip_county.csv','r') as zipFile:
        zips = csv.reader(zipFile, delimiter=',')
        next(zips)
        for row in zips:
            zipCode = int(row[0])
            state = row[6].strip()
            county = row[7].strip()
            # zip code to string:
            tmp = str(zipCode)
            while len(tmp) < 5:
                tmp = "0" + tmp

            zmap[tmp] = (state, county)
    return zmap

# reads from the CSV files and creates Location objects
# (adds all the activities for each location to its corresponding object)
# return: list of Location objects
def getLocations():
    allLocs = []
    # ['ENTITYID', 'ADDRESSSTATECODE', 'POSTALCODE']
    with open('AllAddresses.csv','r') as addsFile:         # addresses
        adds = csv.reader(addsFile, delimiter=',')
        next(adds)         # skip over column labels

        # ['ACTIVITYID', 'ENTITYID']
        with open('AllActivities.csv','r') as actsFile:    # activities
            acts = csv.reader(actsFile, delimiter=',')
            next(acts)     # skip over column labels
            curr = next(acts) # get first activity

            while 1:
                try:
                    # get current location (RecArea/Facility)
                    row = next(adds)
                    # create location object for this row
                    loc = Location(row[0], row[1], row[2])
                except StopIteration:
                    # we're finished
                    return allLocs

                # advance through activities until the entityID > loc.ID
                while 1:
                    try:
                        curr = next(acts)
                    except StopIteration:
                        # we're finished
                        if len(loc.activities) > 0 and len(loc.state) == 2:     # we only care about locations that have activities
                            return allLocs

                    if int(curr[1]) < loc.ID:
                        continue
                    if int(curr[1]) > loc.ID:
                        break                   # we need to advance through the locations to catch up
                    else:
                        # this activity corresponds to loc (so add it to loc)
                        activityID = int(curr[0])
                        loc.activities[activityID] = True

                # we only care about locations that have activities
                # (also discard the 3 locations without states that appear to be international)
                if len(loc.activities) > 0 and len(loc.state) == 2:
                    allLocs.append(loc)         # we're done with this location, append it to the full list

class Location:
    def __init__(self, entityID, state, postcode):
        self.ID = int(entityID)
        self.state = state.strip()
        self.zip = int(postcode)
        self.activities = dict()
        self.county = ""

    def __repr__(self):
        return str(self.ID) + "\tstate: " + self.state + "\tzip:=" + self.getZipString() + "\tcounty: " + self.county + "\n" + str(self.activities)

    def getZipString(self):
        tmp = str(self.zip)
        while len(tmp) < 5:
            tmp = "0" + tmp
        return tmp

stateAbrevs = dict()
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
