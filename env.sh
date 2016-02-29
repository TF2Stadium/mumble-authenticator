#!/bin/sh

sed -i 's|username|'${DB_USERNAME}$'|g' config.ini
sed -i 's|password|'${DB_PASSWORD}$'|g' config.ini
sed -i 's|127.0.0.1|'${DB_URL}$'|g' config.ini
sed -i 's|database|'${DB_NAME}$'|g' config.ini
sed -i 's|icesecret|'${DB_NAME}$'|g' config.ini
