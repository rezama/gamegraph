
set terminal postscript eps color

set output "../plots/td/td-midgammon-base-back.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-midgammon-graph-base-0back.txt" using 1:2 with lines title "0% back edges", \
     "../data/avg/td-midgammon-graph-base-20back.txt" using 1:2 with lines title "20% back edges", \
     "../data/avg/td-midgammon-graph-base-50back.txt" using 1:2 with lines title "50% back edges", \
     "../data/avg/td-midgammon-graph-base-80back.txt" using 1:2 with lines title "80% back edges", \
     "../data/avg/td-midgammon-graph-base-100back.txt" using 1:2 with lines title "100% back edges"

set output "../plots/td/td-midgammon-base-hit.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-midgammon-graph-base-0hit.txt" using 1:2 with lines title "0% hit edges", \
     "../data/avg/td-midgammon-graph-base-20hit.txt" using 1:2 with lines title "20% hit edges", \
     "../data/avg/td-midgammon-graph-base-50hit.txt" using 1:2 with lines title "50% hit edges", \
     "../data/avg/td-midgammon-graph-base-80hit.txt" using 1:2 with lines title "80% hit edges", \
     "../data/avg/td-midgammon-graph-base-100hit.txt" using 1:2 with lines title "100% hit edges"


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


