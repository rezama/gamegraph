
for i in `ls minigammon-base* midgammon-base* nannon-base* nohitgammon-base*`
do
    newname=$i
    newname=${newname/base/graph-base}
    echo "Renaming $i -> $newname"
    mv "$i" "$newname"
done
