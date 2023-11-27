#!/bin/bash

while true; do
    raw_data_files=$(yq eval '.raw_data_files' conf/production.yml)

    for i in $(find $raw_data_files -type f -name "*.txt" -o -name "*.git"); do # Not recommended, will break on whitespace
        if grep -q "\]\[" "$i"; then
            sed -i 's/\]\[/,/g' $i
            echo "Processing $i"
        else
            sleep 0.5
        fi
    done
    sleep 1;
done;