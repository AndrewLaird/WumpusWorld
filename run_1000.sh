#!/bin/bash
make
SUM=0
SUCCESS=0
NONSTART=0
for i in `seq 1 1000`;
do
    value=$(python3 bin/Main.pyc | awk '{print $4}')
    if [ $value -gt 0 ]
    then
        SUCCESS=$((SUCCESS+1))
    fi
    if [ $value -eq -1 ]
    then
        NONSTART=$((NONSTART+1))
    #else
    #    echo $value
    fi
    SUM=$((SUM+value))
done    
echo "Average Value:"
echo $((SUM/1000))
echo "number of gt 0"
echo $SUCCESS
echo "Number of unsafe starts"
echo $NONSTART
