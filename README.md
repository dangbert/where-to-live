# code_fury
Software Engineering Group1:
* Dan
* Kyle
* Rushmie
* Jon Danko
* Tyler
* Doug

# Apache / PHP Installation:
### Windows Setup:
TODO: Someone explain how to install on windows
Maybe this https://www.znetlive.com/blog/how-to-install-apache-php-and-mysql-on-windows-10-machine/
Havent run through it yet though

### Ubuntu Setup:
If you are using ubuntu check out: https://www.vultr.com/docs/how-to-install-apache-mysql-and-php-on-ubuntu-16-04

### Fedora Setup:
(I installed this on fedora, if you are using ubuntu follow the instructions above)
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
````
Note that the configuation file for apache is located at: /etc/httpd/conf/httpd.conf

# Now Get the Site Running:
* clone this github repository into /var/www and rename it to "html" so that /var/www/html/ exists
* navigate to localhost in your browser (you should see a page that says "hello world" in bold and has a button if everything is set up properly


# Database setup
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

### Script to create tables in database:
On linux you might have to allow apache to make network calls (for curl):
````bash
sudo setsebool -P httpd_can_network_connect 1
````

Now create the tables by navigating to http://localhost/controllers/db_upgrade.php

# Notes on Database Stuff:
````bash
mysqldump code_fury -u code_fury -p > db_backup.sql    # backup database
mysql code_fury -u code_fury -p < db_backup.sql        # import database
````
