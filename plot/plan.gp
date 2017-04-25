set terminal postscript eps color
set output "./plots/sarsa-minigammon-822-chooseroll.eps"
plot "../data/avg/sarsa-minigammon-822-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/sarsa-minigammon-822-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/sarsa-minigammon-822-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/sarsa-minigammon-822-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/sarsa-minigammon-822-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/sarsa-nannon-636-chooseroll.eps"
plot "../data/avg/sarsa-nannon-636-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/sarsa-nannon-636-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/sarsa-nannon-636-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/sarsa-nannon-636-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/sarsa-nannon-636-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/sarsa-midgammon-643-chooseroll.eps"
plot "../data/avg/sarsa-midgammon-643-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/sarsa-midgammon-643-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/sarsa-midgammon-643-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/sarsa-midgammon-643-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/sarsa-midgammon-643-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/sarsa-nohitgammon-843-chooseroll.eps"
plot "../data/avg/sarsa-nohitgammon-843-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/sarsa-nohitgammon-843-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/sarsa-nohitgammon-843-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/sarsa-nohitgammon-843-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/sarsa-nohitgammon-843-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/ntd-minigammon-822-chooseroll.eps"
plot "../data/avg/ntd-minigammon-822-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/ntd-minigammon-822-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/ntd-minigammon-822-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/ntd-minigammon-822-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/ntd-minigammon-822-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/ntd-nannon-636-chooseroll.eps"
plot "../data/avg/ntd-nannon-636-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/ntd-nannon-636-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/ntd-nannon-636-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/ntd-nannon-636-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/ntd-nannon-636-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/ntd-midgammon-643-chooseroll.eps"
plot "../data/avg/ntd-midgammon-643-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/ntd-midgammon-643-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/ntd-midgammon-643-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/ntd-midgammon-643-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/ntd-midgammon-643-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/ntd-nohitgammon-843-chooseroll.eps"
plot "../data/avg/ntd-nohitgammon-843-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/ntd-nohitgammon-843-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/ntd-nohitgammon-843-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/ntd-nohitgammon-843-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/ntd-nohitgammon-843-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/hc-minigammon-822-chooseroll.eps"
plot "../data/avg/hc-minigammon-822-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/hc-minigammon-822-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/hc-minigammon-822-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/hc-minigammon-822-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/hc-minigammon-822-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/hc-nannon-636-chooseroll.eps"
plot "../data/avg/hc-nannon-636-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/hc-nannon-636-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/hc-nannon-636-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/hc-nannon-636-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/hc-nannon-636-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/hc-midgammon-643-chooseroll.eps"
plot "../data/avg/hc-midgammon-643-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/hc-midgammon-643-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/hc-midgammon-643-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/hc-midgammon-643-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/hc-midgammon-643-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

set output "./plots/hc-nohitgammon-843-chooseroll.eps"
plot "../data/avg/hc-nohitgammon-843-chooseroll-0.0.txt" using 1:2 with lines title "chooseroll 0.0", \
     "../data/avg/hc-nohitgammon-843-chooseroll-0.1.txt" using 1:2 with lines title "chooseroll 0.1", \
     "../data/avg/hc-nohitgammon-843-chooseroll-0.5.txt" using 1:2 with lines title "chooseroll 0.5", \
     "../data/avg/hc-nohitgammon-843-chooseroll-0.9.txt" using 1:2 with lines title "chooseroll 0.9", \
     "../data/avg/hc-nohitgammon-843-chooseroll-1.0.txt" using 1:2 with lines title "chooseroll 1.0"

