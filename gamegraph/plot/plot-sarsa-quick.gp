set terminal postscript eps color
#
set output "./plots/sarsa-nohitgammon-graph.eps"
set xlabel "Training Episode"
set ylabel "Wins against Random Agent"
set yrange [0.45:0.90]

plot "../data/avg/sarsa-nohitgammon-graph-base.txt" using 1:2 with lines title "Original Graph", \
     "../data/avg/sarsa-nohitgammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges"

