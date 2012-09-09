
set terminal postscript eps color
#
set output "../plots/rl/rl-midgammon-back.eps"
set xlabel "Training Episode"
set ylabel "Wins against Random Agent"
set yrange [0.45:0.90]

plot "../data/avg/rl-midgammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges", \
     "../data/avg/rl-midgammon-graph-base-20back.txt" using 1:2 with lines title "20% back edges", \
     "../data/avg/rl-midgammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/rl-midgammon-graph-base-80back.txt" using 1:2 with lines title "80% back edges", \
     "../data/avg/rl-midgammon-graph-base-100back.txt" using 1:2 with lines title "100% back edges"

set output "../plots/rl/rl-midgammon-hit.eps"
set xlabel "Training Episode"
set ylabel "Wins against Random Agent"
set yrange [0.45:0.90]

plot "../data/avg/rl-midgammon-graph-base-0hit.txt" using 1:2 with lines title "0% hit edges", \
     "../data/avg/rl-midgammon-graph-base-20hit.txt" using 1:2 with lines title "20% hit edges", \
     "../data/avg/rl-midgammon-graph-base-50hit.txt" using 1:2 with lines title "50% hit edges", \
     "../data/avg/rl-midgammon-graph-base-80hit.txt" using 1:2 with lines title "80% hit edges", \
     "../data/avg/rl-midgammon-graph-base-100hit.txt" using 1:2 with lines title "100% hit edges"

