dir=$1

plots=`ls $dir/*.png`

out=$dir/index.html
rm $out

echo "<div class=\"ext-box\">" >> $out
echo "<TABLE border= \"1\">" >> $out

i=0
for p in $plots;
do

    name=${p##*/}
    echo $name
    echo $i

    if [ $(($i%2)) = 0 ]; then
        if [ $i -gt 0 ]; then
            echo "</TR>" >> $out
        fi
        echo "<TR>" >> $out
    fi

    echo "<TD><CENTER>" >> $out
#    echo "<img src=\"$name\" height=\"250\" width=\"500\">" >> $out
    echo "<img src=\"$name\" height=\"450\" width=\"600\">" >> $out   
    echo "</CENTER></TD>" >> $out

    i=$(($i+1))
done
