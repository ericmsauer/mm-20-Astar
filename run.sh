#!/bin/bash
if hash python2 2>/dev/null; then
        python2 client/scheduler_client.py $1 $2
    else
        python client/scheduler_client.py $1 $2
    fi
