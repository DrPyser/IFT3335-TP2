#!/usr/bin/env sh

export WEKAPATH="/usr/share/java/";
export CP="$CLASSPATH:/usr/share/java/:$WEKAPATH/mysql-connector-java-5.0.5-bin.jar:$WEKAPATH/weka.jar";

python disambiguation.py interest.acl94.txt &&
    for i in training-set/*.arff; do
        #echo "$CP"
        FILTERED="${i%.*}-filtered.arff"
        OUTPUT="$(basename $i .arff).txt"
        java -cp $CP weka.filters.unsupervised.attribute.StringToNominal -R "first-last" -i "$i" -o "$FILTERED" && {
            #NaiveBayes
            { java -cp $CP weka.classifiers.bayes.NaiveBayes -c "last" -t "$FILTERED" > results/"nb-$OUTPUT" &&
                  echo "NaiveBayes done for $i" &
              PID1=$!;
            } && { # decision tree j48
                java -cp $CP weka.classifiers.trees.J48 -c "last" -t "$FILTERED" > results/"J48-$OUTPUT" &&
                    echo "trees.J48 done for $i" &
                PID2=$!;
            } && { # SVM/SMO
                java -cp $CP weka.classifiers.functions.SMO -C 1.0 -L 0.001 -P 1.0E-12 -N 0 -V -1 -W 1 \
                     -K "weka.classifiers.functions.supportVector.PolyKernel -C 250007 -E 1.0" -c "last" \
                     -t "$FILTERED" > results/"SMO-$OUTPUT" && echo "SMO done for $i" &
                PID3=$!; 
            } && wait $PID1 && wait $PID2 && wait $PID3 && rm "$FILTERED";
        } && echo "Done for $i";
    done

exit 0
