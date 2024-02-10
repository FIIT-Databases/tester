#!/bin/bash

RUNNING_WORKER_PROCESS_COUNT=$(pgrep -f ".*rq" --count)

echo "$RUNNING_WORKER_PROCESS_COUNT/$WORKER_PROCESS_COUNT processes running "

if [ ${RUNNING_WORKER_PROCESS_COUNT} == ${WORKER_PROCESS_COUNT} ]
then
    exit 0
else
    exit 1
fi
