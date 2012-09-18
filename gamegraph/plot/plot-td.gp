set terminal postscript eps color

set output "./plots/minigammon/td-minigammon-graph-back.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against evaluation opponent"
#set yrange [0:1900]
#set auto y

plot "../data/avg/td-minigammon-graph-base-100back.txt" using 1:2 with lines title "100% back edges", \
     "../data/avg/td-minigammon-graph-base-85back.txt" using 1:2 with lines title "85% back edges", \
     "../data/avg/td-minigammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/td-minigammon-graph-base-15back.txt" using 1:2 with lines title "15% back edges", \
     "../data/avg/td-minigammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges"


