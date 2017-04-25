set terminal postscript eps color

set output "./plots/ntd-nim.eps"
set xlabel "Iteration (128 training games each)"
set ylabel "Wins against Optimal Agent"
#set yrange [0:1900]
plot "../data/trials/ntd-nim-0123-0.txt" using 1:2 with lines title "Neural TD"



