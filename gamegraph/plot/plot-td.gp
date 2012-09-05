
set terminal postscript eps color

set output "../plots/td/td-midgammon-d4s8-ergo.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-midgammon-graph-d4s8-ergo0.txt" using 1:2 with lines title "ergo 0", \
     "../data/avg/td-midgammon-graph-d4s8-ergo20.txt" using 1:2 with lines title "ergo 20", \
     "../data/avg/td-midgammon-graph-d4s8-ergo50.txt" using 1:2 with lines title "ergo 50", \
     "../data/avg/td-midgammon-graph-d4s8-ergo80.txt" using 1:2 with lines title "ergo 80", \
     "../data/avg/td-midgammon-graph-d4s8-ergo100.txt" using 1:2 with lines title "ergo 100"

set output "../plots/td/td-minigammon-base-ergo.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-minigammon-graph-base-ergo0.txt" using 1:2 with lines title "ergo 0", \
     "../data/avg/td-minigammon-graph-base-ergo20.txt" using 1:2 with lines title "ergo 20", \
     "../data/avg/td-minigammon-graph-base-ergo50.txt" using 1:2 with lines title "ergo 50", \
     "../data/avg/td-minigammon-graph-base-ergo80.txt" using 1:2 with lines title "ergo 80", \
     "../data/avg/td-minigammon-graph-base-ergo100.txt" using 1:2 with lines title "ergo 100"

#plot "../data/avg/td-midgammon-graph-d4s8-ergo0.txt" using 1:2 with lines title "ergo 0", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo10.txt" using 1:2 with lines title "ergo 10", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo20.txt" using 1:2 with lines title "ergo 20", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo30.txt" using 1:2 with lines title "ergo 30", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo40.txt" using 1:2 with lines title "ergo 40", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo50.txt" using 1:2 with lines title "ergo 50", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo60.txt" using 1:2 with lines title "ergo 60", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo70.txt" using 1:2 with lines title "ergo 70", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo80.txt" using 1:2 with lines title "ergo 80", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo90.txt" using 1:2 with lines title "ergo 90", \
#     "../data/avg/td-midgammon-graph-d4s8-ergo100.txt" using 1:2 with lines title "ergo 100"

set auto y


