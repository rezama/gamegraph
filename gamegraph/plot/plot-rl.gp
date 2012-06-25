
set terminal postscript eps color

set output "../plots/rl/rl-minigammon-offset.eps"
set xlabel "Training Episode"
set ylabel "Wins against Random Agent"
set yrange [0.45:0.90]
plot "../data/rl/rl-minigammon-offset-0-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/rl/rl-minigammon-offset-1-0.txt" using 1:2 with lines title "Offset = 1", \
     "../data/rl/rl-minigammon-offset-2-0.txt" using 1:2 with lines title "Offset = 2", \
     "../data/rl/rl-minigammon-offset-3-0.txt" using 1:2 with lines title "Offset = 3", \
     "../data/rl/rl-minigammon-offset-4-0.txt" using 1:2 with lines title "Offset = 4"
#     "../data/rl/rl-minigammon-offset-5-0.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/rl/rl-minigammon-offset-6-0.txt" using 1:2 with lines title "Offset = 6"
#set auto y

set output "../plots/rl/rl-minigammon-offset-0.eps"
plot "../data/rl/rl-minigammon-offset-0-0.txt" using 1:2 with lines title "rl-minigammon"


set output "../plots/rl/rl-nannon-offset.eps"
set yrange [0.45:0.90]
plot "../data/rl/rl-nannon-offset-0-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/rl/rl-nannon-offset-1-0.txt" using 1:2 with lines title "Offset = 1", \
     "../data/rl/rl-nannon-offset-2-0.txt" using 1:2 with lines title "Offset = 2", \
     "../data/rl/rl-nannon-offset-3-0.txt" using 1:2 with lines title "Offset = 3", \
     "../data/rl/rl-nannon-offset-4-0.txt" using 1:2 with lines title "Offset = 4"
#     "../data/rl/rl-nannon-offset-5-0.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/rl/rl-nannon-offset-6-0.txt" using 1:2 with lines title "Offset = 6"
#set auto y

set output "../plots/rl/rl-nannon-offset-0.eps"
plot "../data/rl/rl-nannon-offset-0-0.txt" using 1:2 with lines title "rl-nannon"

set output "../plots/rl/rl-minigammon-p.eps"
set yrange [0.45:0.90]
plot "../data/rl/rl-minigammon-p-1.00-0.txt" using 1:2 with lines title "p = 1.00", \
     "../data/rl/rl-minigammon-p-0.75-0.txt" using 1:2 with lines title "p = 0.75", \
     "../data/rl/rl-minigammon-p-0.50-0.txt" using 1:2 with lines title "p = 0.50", \
     "../data/rl/rl-minigammon-p-0.25-0.txt" using 1:2 with lines title "p = 0.25", \
     "../data/rl/rl-minigammon-p-0.00-0.txt" using 1:2 with lines title "p = 0.00"
#set auto y

set output "../plots/rl/rl-nannon-p.eps"
set yrange [0.45:0.90]
plot "../data/rl/rl-nannon-p-1.00-0.txt" using 1:2 with lines title "p = 1.00", \
     "../data/rl/rl-nannon-p-0.75-0.txt" using 1:2 with lines title "p = 0.75", \
     "../data/rl/rl-nannon-p-0.50-0.txt" using 1:2 with lines title "p = 0.50", \
     "../data/rl/rl-nannon-p-0.25-0.txt" using 1:2 with lines title "p = 0.25", \
     "../data/rl/rl-nannon-p-0.00-0.txt" using 1:2 with lines title "p = 0.00"
#set auto y


