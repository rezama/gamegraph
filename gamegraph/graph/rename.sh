#for i in 0 10 20 30 40 50 60 70 80 90 100
#do
#  echo $i
#  mv minigammon-base-ergo$i minigammon-graph-base-ergo$i
#done

for i in `ls minigammon-base* midgammon-base* nannon-base*`
do
    newname=$i
    newname=${newname/minigammon-base/minigammon-graph-base}
    newname=${newname/midgammon-base/midgammon-graph-base}
    newname=${newname/nannon-base/nannon-graph-base}
    echo "Renaming $i -> $newname"
    mv "$i" "$newname"
done
