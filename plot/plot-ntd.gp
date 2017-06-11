set terminal postscript eps color

set xlabel "Iteration"
set ylabel "Wins against evaluation opponent"
#set yrange [0:1900]
#set auto y

set output "../data/plots/ntd-nim-013-14-chooseroll.eps"
plot "../data/avg/ntd-nim-013-14-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/ntd-nim-013-14-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/ntd-nim-013-14-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/ntd-nim-013-14-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/ntd-nim-013-14-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "../data/plots/ntd-minigammon-622-chooseroll.eps"
plot "../data/avg/ntd-minigammon-622-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/ntd-minigammon-622-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/ntd-minigammon-622-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/ntd-minigammon-622-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/ntd-minigammon-622-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"
