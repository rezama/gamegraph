set terminal postscript eps color

set xlabel "Iteration"
set ylabel "Value"

set output "../data/plots/value-tracker-nim-wins.eps"
plot "../data/trials/ntd-nim-013-14-chooseroll-1.0-0.txt" using 1:2 with lines title "Win Ratio"

set xlabel "Games"
value_file = "../data/value-tracker/ntd-nim-013-14-chooseroll-1.0-0.txt"

set output "../data/plots/value-tracker-nim-w-14.eps"
plot value_file using 1:2 with lines title "w-14-1-0", \
     value_file using 1:3 with lines title "w-14-2-0", \
     value_file using 1:4 with lines title "w-14-3-0"

set output "../data/plots/value-tracker-nim-w-11.eps"
plot value_file using 1:5 with lines title "w-11-1-0", \
     value_file using 1:6 with lines title "w-11-2-0", \
     value_file using 1:7 with lines title "w-11-3-0"

set output "../data/plots/value-tracker-nim-b-11.eps"
plot value_file using 1:8 with lines title "b-11-1-0", \
     value_file using 1:9 with lines title "b-11-2-0", \
     value_file using 1:10 with lines title "b-11-3-0"

set output "../data/plots/value-tracker-nim-w-8.eps"
plot value_file using 1:11 with lines title "w-8-1-0", \
     value_file using 1:12 with lines title "w-8-2-0", \
     value_file using 1:13 with lines title "w-8-3-0"

set output "../data/plots/value-tracker-nim-b-8.eps"
plot value_file using 1:14 with lines title "b-8-1-0", \
     value_file using 1:15 with lines title "b-8-2-0", \
     value_file using 1:16 with lines title "b-8-3-0"

set output "../data/plots/value-tracker-nim-w-5.eps"
plot value_file using 1:17 with lines title "w-5-1-0", \
     value_file using 1:18 with lines title "w-5-2-0", \
     value_file using 1:19 with lines title "w-5-3-0"

set output "../data/plots/value-tracker-nim-b-5.eps"
plot value_file using 1:20 with lines title "b-5-1-0", \
     value_file using 1:21 with lines title "b-5-2-0", \
     value_file using 1:22 with lines title "b-5-3-0"

set output "../data/plots/value-tracker-nim-w-3.eps"
plot value_file using 1:23 with lines title "w-3-3-0", \
     value_file using 1:24 with lines title "w-3-2-0", \
     value_file using 1:25 with lines title "w-3-1-0"

set output "../data/plots/value-tracker-nim-b-3.eps"
plot value_file using 1:26 with lines title "b-3-3-0", \
     value_file using 1:27 with lines title "b-3-2-0", \
     value_file using 1:28 with lines title "b-3-1-0"

set output "../data/plots/value-tracker-nim-w-2.eps"
plot value_file using 1:29 with lines title "w-2-2-0", \
     value_file using 1:30 with lines title "w-2-1-0"
