#!/bin/bash

for file in `ls ./archive/plan-run1-no-chooseroll1.0/*eps`
do
    echo $file
    base=${file%.*}
    convert -density 120 $file $base.png
done

