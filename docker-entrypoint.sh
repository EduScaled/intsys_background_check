#!/bin/bash
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>

# DynIP
IP=$(cat /etc/hosts|grep $HOSTNAME |awk '{print $1}')
echo "IP $IP"

export DB_HOST=${DB_HOST:-"postgres"}
export DB_PORT=${DB_PORT:-"5432"}
export DB_NAME=${DB_NAME:-"root"}
export DB_USER=${DB_USER:-"root"}
export DB_PASSWORD=${DB_PASSWORD:-"root"}

echo starting

exec "$@"