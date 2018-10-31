#!/bin/bash
for i in `seq 1 10` ;
do
    echo $i;
    . run_1000.sh;
done
