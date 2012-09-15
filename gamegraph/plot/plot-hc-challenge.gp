
set terminal postscript eps color

set output "./plots/hc-challenge/hc-challenge-minigammon-offset.eps"
set xlabel "Generation"
set ylabel "Number of 8-game trials used to find a successful challenger"
#set yrange [:.9]
plot "../data/avg/hc-challenge-minigammon-offset-0.txt" using 1:2 title "Offset = 0", \
     "../data/avg/hc-challenge-minigammon-offset-1.txt" using 1:2 title "Offset = 1", \
     "../data/avg/hc-challenge-minigammon-offset-2.txt" using 1:2 title "Offset = 2", \
     "../data/avg/hc-challenge-minigammon-offset-3.txt" using 1:2 title "Offset = 3", \
     "../data/avg/hc-challenge-minigammon-offset-4.txt" using 1:2 title "Offset = 4"
#     "../data/avg/hc-challenge-minigammon-offset-5.txt" using 1:2 title "Offset = 5", \
#     "../data/avg/hc-challenge-minigammon-offset-6.txt" using 1:2 title "Offset = 6"
set auto y

set output "./plots/hc-challenge/hc-challenge-minigammon-offset-0.eps"
plot "../data/avg/hc-challenge-minigammon-offset-0.txt" using 1:2 title "HC-minigammon"


set output "./plots/hc-challenge/hc-challenge-nannon-offset.eps"
#set yrange [:.9]
plot "../data/avg/hc-challenge-nannon-offset-0.txt" using 1:2 title "Offset = 0", \
     "../data/avg/hc-challenge-nannon-offset-1.txt" using 1:2 title "Offset = 1", \
     "../data/avg/hc-challenge-nannon-offset-2.txt" using 1:2 title "Offset = 2", \
     "../data/avg/hc-challenge-nannon-offset-3.txt" using 1:2 title "Offset = 3", \
     "../data/avg/hc-challenge-nannon-offset-4.txt" using 1:2 title "Offset = 4"
#     "../data/avg/hc-challenge-nannon-offset-5.txt" using 1:2 title "Offset = 5", \
#     "../data/avg/hc-challenge-nannon-offset-6.txt" using 1:2 title "Offset = 6"
set auto y

set output "./plots/hc-challenge/hc-challenge-nannon-offset-0.eps"
plot "../data/avg/hc-challenge-nannon-offset-0.txt" using 1:2 title "HC-nannon"

set output "./plots/hc-challenge/hc-challenge-minigammon-p.eps"
#set yrange [:.9]
plot "../data/avg/hc-challenge-minigammon-p-1.00.txt" using 1:2 title "p = 1.00", \
     "../data/avg/hc-challenge-minigammon-p-0.75.txt" using 1:2 title "p = 0.75", \
     "../data/avg/hc-challenge-minigammon-p-0.50.txt" using 1:2 title "p = 0.50", \
     "../data/avg/hc-challenge-minigammon-p-0.25.txt" using 1:2 title "p = 0.25", \
     "../data/avg/hc-challenge-minigammon-p-0.00.txt" using 1:2 title "p = 0.00"
set auto y

set output "./plots/hc-challenge/hc-challenge-nannon-p.eps"
#set yrange [:.9]
plot "../data/avg/hc-challenge-nannon-p-1.00.txt" using 1:2 title "p = 1.00", \
     "../data/avg/hc-challenge-nannon-p-0.75.txt" using 1:2 title "p = 0.75", \
     "../data/avg/hc-challenge-nannon-p-0.50.txt" using 1:2 title "p = 0.50", \
     "../data/avg/hc-challenge-nannon-p-0.25.txt" using 1:2 title "p = 0.25", \
     "../data/avg/hc-challenge-nannon-p-0.00.txt" using 1:2 title "p = 0.00"
set auto y


