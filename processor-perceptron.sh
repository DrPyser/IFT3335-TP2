#!/usr/bin/env sh

export WEKAPATH="/usr/share/java/";
export CP="$CLASSPATH:/usr/share/java/:$WEKAPATH/mysql-connector-java-5.0.5-bin.jar:$WEKAPATH/weka.jar";
mkdir results
if [ ! -e "training-set" ] ; then
    exit 1
fi
python disambiguation.py interest.acl94.txt &&
    for i in training-set/*.arff; do
        #echo "$CP"
        export BINARY="${i%.*}-binary.arff"
        export FILTERED="${i%.*}-filtered.arff"
        export OUTPUT="$(basename $i .arff).txt"
        
        java -cp $CP weka.filters.unsupervised.attribute.StringToNominal -R "first-last" -i "$i" | 
            java -cp $CP weka.filters.supervised.attribute.NominalToBinary -c "last" -o "$BINARY" && 
            if [ `grep -c "@attribute" "$BINARY"` -lt 101 ]; then
                export NBATTR="$(expr `grep -c "@attribute" "$BINARY"` - 1)"
                java -cp $CP weka.filters.supervised.attribute.AttributeSelection -E "weka.attributeSelection.InfoGainAttributeEval "\
                     -S "weka.attributeSelection.Ranker -T -1.7976931348623157E308 -N $NBATTR" -c "last" -i "$BINARY" -o "$FILTERED"
            else
                export NBATTR="100"
                java -cp $CP weka.filters.supervised.attribute.AttributeSelection -E "weka.attributeSelection.InfoGainAttributeEval "\
                     -S "weka.attributeSelection.Ranker -T -1.7976931348623157E308 -N $NBATTR" -c "last" -i "$BINARY" -o "$FILTERED" 
            fi &&
        {
            {
                echo "Training with $NBATTR attributes and 5 layers" &&
                    java -cp $CP weka.classifiers.functions.MultilayerPerceptron -L 0.3 -M 0.2 -N 500 -V 0 -S 0 -E 20 -H 5 -t "$FILTERED" -o \
                         > results/"mlp5-$OUTPUT" &&
                    echo "Done for $i with 5 layers and $NBATTR attributes" &
                PID1=$!;
            } && {
                echo "Training with $NBATTR attributes and 10 layers" &&
                    java -cp $CP weka.classifiers.functions.MultilayerPerceptron -L 0.3 -M 0.2 -N 500 -V 0 -S 0 -E 20 -H 10 -t "$FILTERED" -o \
                         > results/"mlp10-$OUTPUT" &&
                    echo "Done for $i with 10 layers and $NBATTR attributes" &
                PID2=$!;
            } && {
                echo "Training with $NBATTR attributes and 30 layers" &&
                    java -cp $CP weka.classifiers.functions.MultilayerPerceptron -L 0.3 -M 0.2 -N 500 -V 0 -S 0 -E 20 -H 30 -t "$FILTERED" -o \
                         > results/"mlp30-$OUTPUT" &&
                    echo "Done for $i with 30 layers and $NBATTR attributes" &
                PID3=$!;
            } && wait $PID1 && wait $PID2 && wait $PID3 && rm "$FILTERED" "$BINARY";
            
            
        } &&
            echo "Done for $i";
    done

exit 0
