
set terminal postscript eps color
#
set output "../plots/rl/rl-minigammon-graph.eps"
set xlabel "Training Episode"
set ylabel "Wins against Random Agent"
set yrange [0.45:0.90]

plot "../data/avg/rl-minigammon-graph-base.txt" using 1:2 with lines title "Original Graph", \
     "../data/avg/rl-minigammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges", \
     "../data/avg/rl-minigammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/rl-minigammon-graph-base-0hit.txt" using 1:2 with lines title "0% hit edges", \
     "../data/avg/rl-minigammon-graph-base-50hit.txt" using 1:2 with lines title "50% hit edges"

