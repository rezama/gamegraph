#!/bin/bash

for file in `ls ../plots/*eps`
do
    echo $file
    base=${file%.*}
    convert -density 120 $file $base.png
done

