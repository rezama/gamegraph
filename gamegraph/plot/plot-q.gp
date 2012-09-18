set terminal postscript eps color

set output "./plots/minigammon/q-minigammon-graph-back.eps"
set xlabel "Training Episode"
set ylabel "Wins against evaluation opponent"
set yrange [0.65:0.87]

plot "../data/avg/q-minigammon-graph-base-100back.txt" using 1:2 with lines title "100% back edges", \
     "../data/avg/q-minigammon-graph-base-85back.txt" using 1:2 with lines title "85% back edges", \
     "../data/avg/q-minigammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/q-minigammon-graph-base-15back.txt" using 1:2 with lines title "15% back edges", \
     "../data/avg/q-minigammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges"


