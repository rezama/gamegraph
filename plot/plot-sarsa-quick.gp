set terminal postscript eps color
#
set output "./plots/sarsa-nim.eps"
set xlabel "Training Episode"
set ylabel "Wins against Optimal Agent"
#set yrange [0.45:0.90]

plot "../data/trials/sarsa-nim-0123-0.txt" using 1:2 with lines title "Sarsa"

