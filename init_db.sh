#!/bin/sh

echo "Waiting for MySQL to start"

while true
do
    netstat -uplnt | grep :3306 | grep LISTEN > /dev/null
    verifier=$?
    if [ 0 = $verifier ]
        then
            python3 init_db.py
            break
        else
            echo "Waiting..."
            sleep 5
    fi
done
