#!/bin/sh

HOST=localhost
PORT=49000

qpidd -p $PORT --auth=no &
sleep 2
printf "Starting matahari agents\n"

if [ "$1" == "-d" ];
then
    MATAHARI_PATH=/home/radek/matahari/matahari_master

    $MATAHARI_PATH/build/src/host/matahari-qmf-hostd -b $HOST -p $PORT &
    $MATAHARI_PATH/build/src/net/matahari-qmf-netd -b $HOST -p $PORT &
    $MATAHARI_PATH/build/src/service/matahari-qmf-serviced -b $HOST -p $PORT &

    $MATAHARI_PATH/build/src/host/matahari-dbus-hostd &
    $MATAHARI_PATH/build/src/net/matahari-dbus-netd &
    $MATAHARI_PATH/build/src/service/matahari-dbus-serviced &
else
    /usr/sbin/matahari-qmf-hostd -b $HOST -p $PORT &
    /usr/sbin/matahari-qmf-netd -b $HOST -p $PORT &
    /usr/sbin/matahari-qmf-serviced -b $HOST -p $PORT &

    /usr/sbin/matahari-dbus-hostd &
    /usr/sbin/matahari-dbus-netd &
    /usr/sbin/matahari-dbus-serviced &
fi
sleep 2
printf "Running tests\n"
./matahari_test.py $HOST:$PORT

kill %1 %2 %3 %4 %5 %6 %7

