set terminal postscript eps color

set output "./plots/ntd-nohitgammon.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/ntd-nohitgammon-graph-base.txt" using 1:2 with lines title "Original Graph", \
     "../data/avg/ntd-nohitgammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges"



