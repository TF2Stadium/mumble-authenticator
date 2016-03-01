#!/bin/sh

sed -i 's|username|'${DB_USERNAME}$'|g' /mumble-authenticator/config.ini
sed -i 's|password|'${DB_PASSWORD}$'|g' /mumble-authenticator/config.ini
sed -i 's|dbhost|'${DB_URL}$'|g' /mumble-authenticator/config.ini
sed -i 's|database|'${DB_NAME}$'|g' /mumble-authenticator/config.ini
sed -i 's|icesecret|'${ICE_SECRET}$'|g' /mumble-authenticator/config.ini
sed -i 's|mumblehost|'${ICE_HOST}$'|g' /mumble-authenticator/config.ini
sed -i 's|DEBUG|'${DEBUG}$'|g' /mumble-authenticator/config.ini
