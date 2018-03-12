# code_fury
Software Engineering Group1:
* Dan
* Kyle
* Rushmie
* Jon Danko

# Apache / PHP Installation:
### Windows Setup:
TODO: Someone explain how to install on windows

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
sudo systemctl restart httd
````
Note that the configuation file for apache is located at: /etc/httpd/conf/httpd.conf

# Now Get the Site Running:
* clone this github repository into /var/www and rename it to "html" so that /var/www/html/ exists
* navigate to localhost in your browser (you should see a page that says "hello world" in bold and has a button if everything is set up properly
