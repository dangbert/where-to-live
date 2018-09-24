# Where to Live (aka. code_fury)
## What is it?
* This is a website that suggests potential counties for the user to live in based off their search preferences.
  * This was a group project for UMBC CMSC447 (Software Engineering).
* The core of this project is a custom SQL database we created using data from:
  * [datausa.io API](https://github.com/DataUSA/datausa-api/wiki/Data-API)
  * https://ridb.recreation.gov/
  * [NOAA Weather Data](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/climate-normals/1981-2010-normals-data)
  
## How we did it:
* We designed a database schema and populated it by creating PHP and python scripts to scrape the datausa.io API, and to ingest CSV and TXT files.
* Website backend uses Apache, PHP, SQL
* Website frontend created with HTML, CSS, JS.  Serves as a UI for a user to indicate search preferences and see the results on a map using the Google Maps Javascript API.


# How to Setup the Site:
## Apache/PHP Installation:
### Windows Setup:
* Download and install wampserver: http://www.wampserver.com/en/
* Once installed, place where-to-live repo into wamp server /www/ directory
* Start up wamp server and go to http://localhost/where-to-live/views/home.html in browser

### Ubuntu Setup:
If you are using ubuntu check out [https://www.vultr.com/docs/how-to-install-apache-mysql-and-php-on-ubuntu-16-04](this)

### Fedora Setup:
````bash
sudo dnf install httpd
sudo systemctl enable httpd.service
sudo systemctl start httd
sudo dnf install mysql-server
sudo dnf install php
sudo dnf install php-mcrypt.x86_64 php-mbstring.x86_64
sudo firewall-cmd --permanent --add-port=80/tcp
sudo setsebool -P httpd_can_network_connect 1
sudo systemctl restart httd

sudo dnf install yum-utils
sudo dnf install php-mysqlnd

# on AWS:
sudo yum install mariadb-server mariadb-client
# (then removed previously installed php stuff)
sudo yum install php php-gd php-mysql php-mcrypt
````
Note that the configuation file for apache is located at: /etc/httpd/conf/httpd.conf

## Database setup
### Create the database and database user with the mysql cli:
start the database on linux:
````bash
systemctl start mariadb.service
````

````bash
mysql -u root -p
GRANT ALL PRIVILEGES ON *.* TO 'code_fury'@'localhost' IDENTIFIED BY 'devpassword';
create database code_fury;
use code_fury;
````

to view the database later through the cli:
````bash
mysql code_fury -u code_fury -p   # then type in 'devpassword' when prompted.
````

Note: linux php error log is located at /var/log/php-fpm/www-error.log

### Now Import the Database Data:
````bash
mysql code_fury -u code_fury -p < data/db_backupv5.sql
````

#### Note: How Database was made initially (no need to do this again):

````bash
sudo setsebool -P httpd_can_network_connect 1  # allow apache to make network calls (for curl)
````
1. Now create the tables by navigating to http://localhost/controllers/db_upgrade.php (takes a few hours)
2. Then run the python script data/recareas/processActivities.py to upgrade the database to version 3 (which contains the recarea data)
3. Then run the python script data/weather/weather_parse.py to upgrade the database to version 4 (which contains the weather data)
4. Then run the python script data/geocodes/GeocodeCounties.py to upgrade the database to version 5 (adds the lat and long of each county to the database)

Then a backup of the database was made by:
````bash
mysqldump code_fury -u code_fury -p > db_backupv5.sql    # backup database
````

## Now Get the Site Running:
* clone this github repository in /var/www so that /var/www/html/where-to-live exists
* navigate to http://localhost/where-to-live/views in your browser 

## Project Contributors:
* Brian S.
* Dan E.
* Doug G.
* Jon D.
* Kyle C.
* Rushmie K.
* Tyler K.
