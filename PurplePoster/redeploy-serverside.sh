#!/bin/bash

git pull
bash reload-db.sh
./manage.py collectstatic
sudo /etc/init.d/apache2 restart

