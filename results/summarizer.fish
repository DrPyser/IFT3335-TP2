#!/usr/bin/env fish

echo "algo, size, word, pos" > summary.csv

set -x algos "nb" "SMO" "J48" "mlp5" "mlp10" "mlp30"

for algo in $algos
    for i in (seq 1 10)
        for ts in "$algo-$i-word-context.txt"
            set wordresult (grep -A 2 "Stratified cross-validation" $ts | tail -n 1 | sed -r 's/.+ ([0-9]+(\.[0-9]+)?) *\%/\1/')
            for ts in "$algo-$i-pos-context.txt"
                set posresult (grep -A 2 "Stratified cross-validation" $ts | tail -n 1 | sed -r 's/.+ ([0-9]+(\.[0-9]+)?) *\%/\1/')
                echo "$algo,$i,$wordresult,$posresult" >> summary.csv
            end
        end
    end
end
