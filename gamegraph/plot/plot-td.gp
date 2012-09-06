
set terminal postscript eps color

set output "../plots/td/td-minigammon.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-minigammon-graph-base.txt" using 1:2 with lines title "Original Graph", \
     "../data/avg/td-minigammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges", \
     "../data/avg/td-minigammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/td-minigammon-graph-base-0hit.txt" using 1:2 with lines title "0% hit edges", \
     "../data/avg/td-minigammon-graph-base-50hit.txt" using 1:2 with lines title "50% hit edges"



