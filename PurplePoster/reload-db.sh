#!/bin/bash

mysql <<END
drop database PurplePoster;
create database PurplePoster;
END

./manage.py syncdb

