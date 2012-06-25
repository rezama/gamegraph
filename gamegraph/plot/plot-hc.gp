
set terminal postscript eps color

set output "../plots/hc/hc-minigammon-offset.eps"
set xlabel "Generation"
set ylabel "Wins against Random Agent"
#set yrange [:.9]
plot "../data/avg/hc-minigammon-offset-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/avg/hc-minigammon-offset-1.txt" using 1:2 with lines title "Offset = 1", \
     "../data/avg/hc-minigammon-offset-2.txt" using 1:2 with lines title "Offset = 2", \
     "../data/avg/hc-minigammon-offset-3.txt" using 1:2 with lines title "Offset = 3", \
     "../data/avg/hc-minigammon-offset-4.txt" using 1:2 with lines title "Offset = 4"
#     "../data/avg/hc-minigammon-offset-5.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/avg/hc-minigammon-offset-6.txt" using 1:2 with lines title "Offset = 6"
set auto y

set output "../plots/hc/hc-minigammon-offset-0.eps"
plot "../data/avg/hc-minigammon-offset-0.txt" using 1:2 with lines title "HC-minigammon"


set output "../plots/hc/hc-nannon-offset.eps"
#set yrange [:.9]
plot "../data/avg/hc-nannon-offset-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/avg/hc-nannon-offset-1.txt" using 1:2 with lines title "Offset = 1", \
     "../data/avg/hc-nannon-offset-2.txt" using 1:2 with lines title "Offset = 2", \
     "../data/avg/hc-nannon-offset-3.txt" using 1:2 with lines title "Offset = 3", \
     "../data/avg/hc-nannon-offset-4.txt" using 1:2 with lines title "Offset = 4"
#     "../data/avg/hc-nannon-offset-5.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/avg/hc-nannon-offset-6.txt" using 1:2 with lines title "Offset = 6"
set auto y

set output "../plots/hc/hc-nannon-offset-0.eps"
plot "../data/avg/hc-nannon-offset-0.txt" using 1:2 with lines title "HC-nannon"

set output "../plots/hc/hc-minigammon-p.eps"
#set yrange [:.9]
plot "../data/avg/hc-minigammon-p-1.00.txt" using 1:2 with lines title "p = 1.00", \
     "../data/avg/hc-minigammon-p-0.75.txt" using 1:2 with lines title "p = 0.75", \
     "../data/avg/hc-minigammon-p-0.50.txt" using 1:2 with lines title "p = 0.50", \
     "../data/avg/hc-minigammon-p-0.25.txt" using 1:2 with lines title "p = 0.25", \
     "../data/avg/hc-minigammon-p-0.00.txt" using 1:2 with lines title "p = 0.00"
set auto y

set output "../plots/hc/hc-nannon-p.eps"
#set yrange [:.9]
plot "../data/avg/hc-nannon-p-1.00.txt" using 1:2 with lines title "p = 1.00", \
     "../data/avg/hc-nannon-p-0.75.txt" using 1:2 with lines title "p = 0.75", \
     "../data/avg/hc-nannon-p-0.50.txt" using 1:2 with lines title "p = 0.50", \
     "../data/avg/hc-nannon-p-0.25.txt" using 1:2 with lines title "p = 0.25", \
     "../data/avg/hc-nannon-p-0.00.txt" using 1:2 with lines title "p = 0.00"
set auto y


