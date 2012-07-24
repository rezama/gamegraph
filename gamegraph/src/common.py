'''
Created on Dec 11, 2011

@author: reza
'''
import sys

DEFAULT_P = 1.0
DEFAULT_REENTRY_OFFSET = 0
DEFAULT_TRIAL = 0

NUM_TRIALS = 10

EXP_VARY_P = 'p'
EXP_VARY_REENTRY = 'offset'

ALTERNATE_SEATS = True
USE_SEEDS = True

COLLECT_STATS = True

RECENT_WINNERS_LIST_SIZE = 3000

NUM_STATS_GAMES = 10000

PRINT_GAME_DETAIL = False
PRINT_GAME_RESULTS = False
#PRINT_GAME_DETAIL = True
#PRINT_GAME_RESULTS = True

class Experiment:
    exp = None
    p = None
    offset = None
    trial = None
    
    @classmethod
    def get_file_suffix(cls):
        if cls.exp == EXP_VARY_P:
            return '%s-%1.2f-%d' % (cls.exp, cls.p, cls.trial)
        else:
            return '%s-%d-%d' % (cls.exp, cls.offset, cls.trial)

    @classmethod
    def get_command_line_args(cls):
        if len(sys.argv) < 4:
            print 'You can specify an experiment mode with:'
            print 'python %s p <p> <trial>' % sys.argv[0]
            print 'python %s offset <offset> <trial>' % sys.argv[0]
            exp = EXP_VARY_REENTRY
            p = DEFAULT_P
            offset = DEFAULT_REENTRY_OFFSET
            trial = DEFAULT_TRIAL
        else:
            p = DEFAULT_P
            offset = DEFAULT_REENTRY_OFFSET
        
            exp = sys.argv[1]
            if exp == EXP_VARY_P:
                p = float(sys.argv[2])
            else:
                offset = int(sys.argv[2])
            
            trial = int(sys.argv[3])
    
        cls.exp = exp
        cls.p = p
        cls.offset = offset
        cls.trial = trial
        print 'Using: p = %.2f, offset = %d, trial = %d' % (p, offset, trial)
        print 
        return (p, offset) 
    
    @classmethod
    def write_stats(cls, state_class, domain_name):
        if not COLLECT_STATS:
            return
    #    # visit counts to individual states        
    #    filename = '../data/states-visit-count-%1.2f.txt' % state_class.p
    #    f = open(filename, 'w')
    #    for state, count_visits in sorted(state_class.states_visit_count.iteritems(), key=lambda (k,v): (v,k)):
    #        f.write('%s %d\n' % (state, count_visits))
    ##        print '%s: %d' % (state, count_visits)
    #    f.close()
    
        # number of states discovered by game
        filename = '../data/games-discovered-states-count-%s-%s.txt' % (domain_name, cls.get_file_suffix())
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count)):
            f.write('%d %d\n' % (game_number, state_class.games_discovered_states_count[game_number])) 
        f.close()
    
        # number of states discovered by game over average number of plies per game      
        filename = '../data/games-discovered-states-count-over-avg-num-plies-%s-%s.txt' % (domain_name, cls.get_file_suffix())
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count_over_avg_num_plies)):
            f.write('%d %f\n' % (game_number, state_class.games_discovered_states_count_over_avg_num_plies[game_number])) 
        f.close()
    
        filename = '../data/games-new-discovered-states-count-%s-%s.txt' % (domain_name, cls.get_file_suffix())
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count)):
            newly_discovered_count = state_class.games_discovered_states_count[game_number]
            if game_number != 0:
                newly_discovered_count -= state_class.games_discovered_states_count[game_number - 1]
            f.write('%d %d\n' % (game_number, newly_discovered_count)) 
        f.close()
    
        # number of visits to game states sorted by first ply of visit    
        filename = '../data/states-sorted-by-ply-visit-count-%s-%s.txt' % (domain_name, cls.get_file_suffix())
        f = open(filename, 'w')
        for i in range(len(state_class.states_sorted_by_ply_visit_count)):
            state_sorted_by_ply_visit_count = state_class.states_sorted_by_ply_visit_count[i]
            f.write('%d: %d\n' % (i, state_sorted_by_ply_visit_count))
        f.close()        
    
        # same as above, over average num of plies per game   
        filename = '../data/states-sorted-by-ply-visit-count-over-avg-num-plies-%s-%s.txt' % (domain_name, cls.get_file_suffix())
        f = open(filename, 'w')
        for i in range(len(state_class.states_sorted_by_ply_visit_count_over_avg_num_plies)):
            state_sorted_by_ply_visit_count_over_avg_num_plies = state_class.states_sorted_by_ply_visit_count_over_avg_num_plies[i]
            f.write('%d: %f\n' % (i, state_sorted_by_ply_visit_count_over_avg_num_plies))
        f.close()        
    
