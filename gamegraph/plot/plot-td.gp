
set terminal postscript eps color

set output "./plots/td/td-nohitgammon.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-nohitgammon-graph-base.txt" using 1:2 with lines title "Original Graph", \
     "../data/avg/td-nohitgammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges"



