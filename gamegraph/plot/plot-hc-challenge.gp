set terminal postscript eps color

set output "./plots/minigammon/hc-challenge-minigammon-graph-back.eps"
set xlabel "Generation"
set ylabel "Number of 8-game trials used to find a successful challenger"
#set yrange [:.9]

plot "../data/avg/hc-challenge-minigammon-graph-base-100back.txt" using 1:2 with lines title "100% back edges", \
     "../data/avg/hc-challenge-minigammon-graph-base-85back.txt" using 1:2 with lines title "85% back edges", \
     "../data/avg/hc-challenge-minigammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/hc-challenge-minigammon-graph-base-15back.txt" using 1:2 with lines title "15% back edges", \
     "../data/avg/hc-challenge-minigammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges"
