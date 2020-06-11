#!/bin/bash

# Works for cinnamon.

PID=$(pgrep cinnamon-sessio)
export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)

echo $DBUS_SESSION_BUS_ADDRESS
echo "$@"

python3 pointlessarrow.py "$@"

