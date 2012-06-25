
set terminal postscript eps color

set output "../plots/domainstats/games-discovered-states-count-minigammon-offset.eps"
set xlabel "Games Played"
set ylabel "States Discovered"
#set yrange [0:1900]
plot "../data/domainstats/games-discovered-states-count-minigammon-offset-0-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/domainstats/games-discovered-states-count-minigammon-offset-1-0.txt" using 1:2 with lines title "Offset = 1", \
     "../data/domainstats/games-discovered-states-count-minigammon-offset-2-0.txt" using 1:2 with lines title "Offset = 2", \
     "../data/domainstats/games-discovered-states-count-minigammon-offset-3-0.txt" using 1:2 with lines title "Offset = 3", \
     "../data/domainstats/games-discovered-states-count-minigammon-offset-4-0.txt" using 1:2 with lines title "Offset = 4"
#     "../data/domainstats/games-discovered-states-count-minigammon-offset-5-0.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/domainstats/games-discovered-states-count-minigammon-offset-6-0.txt" using 1:2 with lines title "Offset = 6"
set auto y

#set output "../plots/domainstats/games-new-discovered-states-count-minigammon-offset.eps"
#set xlabel "Game Number"
#set ylabel "States Discovered in Last Game"
#plot "../data/domainstats/games-new-discovered-states-count-minigammon-offset-0-0.txt" using 1:2 title "Offset = 0", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-offset-1-0.txt" using 1:2 title "Offset = 1", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-offset-2-0.txt" using 1:2 title "Offset = 2", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-offset-3-0.txt" using 1:2 title "Offset = 3", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-offset-4-0.txt" using 1:2 title "Offset = 4"
##     "../data/domainstats/games-new-discovered-states-count-minigammon-offset-5-0.txt" using 1:2 title "Offset = 5", \
##     "../data/domainstats/games-new-discovered-states-count-minigammon-offset-6-0.txt" using 1:2 title "Offset = 6"

set output "../plots/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset.eps"
set xlabel "Games Played"
set ylabel "States Discovered per 1000 Plies"
#set yrange [0:60]
plot "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-0-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-1-0.txt" using 1:2 with lines title "Offset = 1", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-2-0.txt" using 1:2 with lines title "Offset = 2", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-3-0.txt" using 1:2 with lines title "Offset = 3", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-4-0.txt" using 1:2 with lines title "Offset = 4"
#     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-5-0.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-offset-6-0.txt" using 1:2 with lines title "Offset = 6"
set auto y

set xlabel "States (Sorted by Earliest Visit Time)"
set ylabel "Visit Count"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-minigammon-offset-0.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-minigammon-offset-0-0.txt" using 1:2 title "Offset = 0"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-minigammon-offset-2.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-minigammon-offset-2-0.txt" using 1:2 title "Offset = 2"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-minigammon-offset-4.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-minigammon-offset-4-0.txt" using 1:2 title "Offset = 4"
     
set ylabel "Visit Count per 1000 Plies"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-offset-0.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-offset-0-0.txt" using 1:2 title "Offset = 0"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-offset-2.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-offset-2-0.txt" using 1:2 title "Offset = 2"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-offset-4.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-offset-4-0.txt" using 1:2 title "Offset = 4"


set output "../plots/domainstats/games-discovered-states-count-minigammon-p.eps"
set xlabel "Games Played"
set ylabel "States Discovered"
#set yrange [0:1900]
plot "../data/domainstats/games-discovered-states-count-minigammon-p-1.00-0.txt" using 1:2 with lines title "p = 1.00", \
     "../data/domainstats/games-discovered-states-count-minigammon-p-0.75-0.txt" using 1:2 with lines title "p = 0.75", \
     "../data/domainstats/games-discovered-states-count-minigammon-p-0.50-0.txt" using 1:2 with lines title "p = 0.50", \
     "../data/domainstats/games-discovered-states-count-minigammon-p-0.25-0.txt" using 1:2 with lines title "p = 0.25", \
     "../data/domainstats/games-discovered-states-count-minigammon-p-0.00-0.txt" using 1:2 with lines title "p = 0.00"
set auto y

#set output "../plots/domainstats/games-new-discovered-states-count-minigammon-p.eps"
#set xlabel "Game Number"
#set ylabel "States Discovered in Last Game"
#plot "../data/domainstats/games-new-discovered-states-count-minigammon-p-0.00-0.txt" using 1:2 title "p = 0.00", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-p-0.25-0.txt" using 1:2 title "p = 0.25", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-p-0.50-0.txt" using 1:2 title "p = 0.50", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-p-0.75-0.txt" using 1:2 title "p = 0.75", \
#     "../data/domainstats/games-new-discovered-states-count-minigammon-p-1.00-0.txt" using 1:2 title "p = 1.00"

set output "../plots/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-p.eps"
set xlabel "Games Played"
set ylabel "States Discovered per 1000 Plies"
#set yrange [0:60]
plot "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-p-1.00-0.txt" using 1:2 with lines title "p = 1.00", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-p-0.25-0.txt" using 1:2 with lines title "p = 0.25", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-p-0.50-0.txt" using 1:2 with lines title "p = 0.50", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-p-0.75-0.txt" using 1:2 with lines title "p = 0.75", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-minigammon-p-0.00-0.txt" using 1:2 with lines title "p = 0.00"
set auto y

set xlabel "States (Sorted by Earliest Visit Time)"
set ylabel "Visit Count"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-minigammon-p-0.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-minigammon-p-0.00-0.txt" using 1:2 title "p = 0.00"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-minigammon-p-0.50.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-minigammon-p-0.50-0.txt" using 1:2 title "p = 0.50"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-minigammon-p-1.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-minigammon-p-1.00-0.txt" using 1:2 title "p = 1.00"
     
set ylabel "Visit Count per 1000 Plies"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-p-0.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-p-0.00-0.txt" using 1:2 title "p = 0.00"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-p-0.50.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-p-0.50-0.txt" using 1:2 title "p = 0.50"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-p-1.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-minigammon-p-1.00-0.txt" using 1:2 title "p = 1.00"

# Nannon

set output "../plots/domainstats/games-discovered-states-count-nannon-offset.eps"
set xlabel "Games Played"
set ylabel "States Discovered"
#set yrange [0:1900]
plot "../data/domainstats/games-discovered-states-count-nannon-offset-0-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/domainstats/games-discovered-states-count-nannon-offset-1-0.txt" using 1:2 with lines title "Offset = 1", \
     "../data/domainstats/games-discovered-states-count-nannon-offset-2-0.txt" using 1:2 with lines title "Offset = 2", \
     "../data/domainstats/games-discovered-states-count-nannon-offset-3-0.txt" using 1:2 with lines title "Offset = 3", \
     "../data/domainstats/games-discovered-states-count-nannon-offset-4-0.txt" using 1:2 with lines title "Offset = 4"
#     "../data/domainstats/games-discovered-states-count-nannon-offset-5-0.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/domainstats/games-discovered-states-count-nannon-offset-6-0.txt" using 1:2 with lines title "Offset = 6"
set auto y

#set output "../plots/domainstats/games-new-discovered-states-count-nannon-offset.eps"
#set xlabel "Game Number"
#set ylabel "States Discovered in Last Game"
#plot "../data/domainstats/games-new-discovered-states-count-nannon-offset-0-0.txt" using 1:2 title "Offset = 0", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-offset-1-0.txt" using 1:2 title "Offset = 1", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-offset-2-0.txt" using 1:2 title "Offset = 2", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-offset-3-0.txt" using 1:2 title "Offset = 3", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-offset-4-0.txt" using 1:2 title "Offset = 4"
##     "../data/domainstats/games-new-discovered-states-count-nannon-offset-5-0.txt" using 1:2 title "Offset = 5", \
##     "../data/domainstats/games-new-discovered-states-count-nannon-offset-6-0.txt" using 1:2 title "Offset = 6"

set output "../plots/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset.eps"
set xlabel "Games Played"
set ylabel "States Discovered per 1000 Plies"
#set yrange [0:60]
plot "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-0-0.txt" using 1:2 with lines title "Offset = 0", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-1-0.txt" using 1:2 with lines title "Offset = 1", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-2-0.txt" using 1:2 with lines title "Offset = 2", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-3-0.txt" using 1:2 with lines title "Offset = 3", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-4-0.txt" using 1:2 with lines title "Offset = 4"
#     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-5-0.txt" using 1:2 with lines title "Offset = 5", \
#     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-offset-6-0.txt" using 1:2 with lines title "Offset = 6"
set auto y

set xlabel "States (Sorted by Earliest Visit Time)"
set ylabel "Visit Count"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-nannon-offset-0.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-nannon-offset-0-0.txt" using 1:2 title "Offset = 0"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-nannon-offset-2.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-nannon-offset-2-0.txt" using 1:2 title "Offset = 2"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-nannon-offset-4.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-nannon-offset-4-0.txt" using 1:2 title "Offset = 4"
     
set ylabel "Visit Count per 1000 Plies"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-offset-0.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-offset-0-0.txt" using 1:2 title "Offset = 0"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-offset-2.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-offset-2-0.txt" using 1:2 title "Offset = 2"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-offset-4.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-offset-4-0.txt" using 1:2 title "Offset = 4"


set output "../plots/domainstats/games-discovered-states-count-nannon-p.eps"
set xlabel "Games Played"
set ylabel "States Discovered"
#set yrange [0:1900]
plot "../data/domainstats/games-discovered-states-count-nannon-p-1.00-0.txt" using 1:2 with lines title "p = 1.00", \
     "../data/domainstats/games-discovered-states-count-nannon-p-0.75-0.txt" using 1:2 with lines title "p = 0.75", \
     "../data/domainstats/games-discovered-states-count-nannon-p-0.50-0.txt" using 1:2 with lines title "p = 0.50", \
     "../data/domainstats/games-discovered-states-count-nannon-p-0.25-0.txt" using 1:2 with lines title "p = 0.25", \
     "../data/domainstats/games-discovered-states-count-nannon-p-0.00-0.txt" using 1:2 with lines title "p = 0.00"
set auto y

#set output "../plots/domainstats/games-new-discovered-states-count-nannon-p.eps"
#set xlabel "Game Number"
#set ylabel "States Discovered in Last Game"
#plot "../data/domainstats/games-new-discovered-states-count-nannon-p-0.00-0.txt" using 1:2 title "p = 0.00", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-p-0.25-0.txt" using 1:2 title "p = 0.25", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-p-0.50-0.txt" using 1:2 title "p = 0.50", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-p-0.75-0.txt" using 1:2 title "p = 0.75", \
#     "../data/domainstats/games-new-discovered-states-count-nannon-p-1.00-0.txt" using 1:2 title "p = 1.00"

set output "../plots/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-p.eps"
set xlabel "Games Played"
set ylabel "States Discovered per 1000 Plies"
#set yrange [0:60]
plot "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-p-1.00-0.txt" using 1:2 with lines title "p = 1.00", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-p-0.75-0.txt" using 1:2 with lines title "p = 0.75", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-p-0.50-0.txt" using 1:2 with lines title "p = 0.50", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-p-0.25-0.txt" using 1:2 with lines title "p = 0.25", \
     "../data/domainstats/games-discovered-states-count-over-avg-num-plies-nannon-p-0.00-0.txt" using 1:2 with lines title "p = 0.00"
set auto y

set xlabel "States (Sorted by Earliest Visit Time)"
set ylabel "Visit Count"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-nannon-p-0.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-nannon-p-0.00-0.txt" using 1:2 title "p = 0.00"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-nannon-p-0.50.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-nannon-p-0.50-0.txt" using 1:2 title "p = 0.50"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-nannon-p-1.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-nannon-p-1.00-0.txt" using 1:2 title "p = 1.00"
     
set ylabel "Visit Count per 1000 Plies"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-p-0.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-p-0.00-0.txt" using 1:2 title "p = 0.00"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-p-0.50.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-p-0.50-0.txt" using 1:2 title "p = 0.50"
set output "../plots/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-p-1.00.eps"
plot "../data/domainstats/states-sorted-by-ply-visit-count-over-avg-num-plies-nannon-p-1.00-0.txt" using 1:2 title "p = 1.00"



