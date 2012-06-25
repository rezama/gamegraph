
set terminal postscript eps color

set output "../plots/td/td-minigammon-offset.eps"
set xlabel "Iteration (16 training games each)"
set ylabel "Wins against Random Agent"
#set yrange [0:1900]
plot "../data/avg/td-minigammon-offset-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/avg/td-minigammon-offset-1.txt" using 1:2 with lines title "Offset = 1", \
     "../data/avg/td-minigammon-offset-2.txt" using 1:2 with lines title "Offset = 2", \
     "../data/avg/td-minigammon-offset-3.txt" using 1:2 with lines title "Offset = 3", \
     "../data/avg/td-minigammon-offset-4.txt" using 1:2 with lines title "Offset = 4"
#     "../data/avg/td-minigammon-offset-5.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/avg/td-minigammon-offset-6.txt" using 1:2 with lines title "Offset = 6"
set auto y

set output "../plots/td/td-minigammon-offset-0.eps"
plot "../data/avg/td-minigammon-offset-0.txt" using 1:2 with lines title "TD-minigammon"


set output "../plots/td/td-nannon-offset.eps"
#set yrange [0:1900]
plot "../data/avg/td-nannon-offset-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/avg/td-nannon-offset-1.txt" using 1:2 with lines title "Offset = 1", \
     "../data/avg/td-nannon-offset-2.txt" using 1:2 with lines title "Offset = 2", \
     "../data/avg/td-nannon-offset-3.txt" using 1:2 with lines title "Offset = 3", \
     "../data/avg/td-nannon-offset-4.txt" using 1:2 with lines title "Offset = 4"
#     "../data/avg/td-nannon-offset-5.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/avg/td-nannon-offset-6.txt" using 1:2 with lines title "Offset = 6"
set auto y

set output "../plots/td/td-nannon-offset-0.eps"
plot "../data/avg/td-nannon-offset-0.txt" using 1:2 with lines title "TD-nannon"

set output "../plots/td/td-minigammon-p.eps"
#set yrange [0:1900]
plot "../data/avg/td-minigammon-p-1.00.txt" using 1:2 with lines title "p = 1.00", \
     "../data/avg/td-minigammon-p-0.75.txt" using 1:2 with lines title "p = 0.75", \
     "../data/avg/td-minigammon-p-0.50.txt" using 1:2 with lines title "p = 0.50", \
     "../data/avg/td-minigammon-p-0.25.txt" using 1:2 with lines title "p = 0.25", \
     "../data/avg/td-minigammon-p-0.00.txt" using 1:2 with lines title "p = 0.00"
set auto y

set output "../plots/td/td-nannon-p.eps"
#set yrange [0:1900]
plot "../data/avg/td-nannon-p-1.00.txt" using 1:2 with lines title "p = 1.00", \
     "../data/avg/td-nannon-p-0.75.txt" using 1:2 with lines title "p = 0.75", \
     "../data/avg/td-nannon-p-0.50.txt" using 1:2 with lines title "p = 0.50", \
     "../data/avg/td-nannon-p-0.25.txt" using 1:2 with lines title "p = 0.25", \
     "../data/avg/td-nannon-p-0.00.txt" using 1:2 with lines title "p = 0.00"
set auto y


