set terminal postscript eps color

set xlabel "Iteration"
set ylabel "Value"

set output "../data/plots/value-tracker-minigammon-wins.eps"
plot "../data/trials/ntd-minigammon-522-0.txt" using 1:2 with lines title "Win Ratio"

set xlabel "Games"
value_file = "../data/value-tracker/ntd-minigammon-522-0.txt"

set output "../data/plots/value-tracker-minigammon-522.eps"
plot value_file using 1:2 with lines title "b-4656-1-0", \
     value_file using 1:3 with lines title "b-1116-1-0", \
     value_file using 1:4 with lines title "w-1111-1-0", \
     value_file using 1:5 with lines title "b-1615-1-0", \
     value_file using 1:6 with lines title "w-5646-1-0"
