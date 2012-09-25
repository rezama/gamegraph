'''
Created on Dec 11, 2011

@author: reza
'''
import sys
import getopt

from params import SAVE_STATS, EVAL_OPPONENT, EVAL_OPPONENT_SARSA,\
    EVAL_OPPONENT_RANDOM, EVAL_OPPONENT_OPTIMAL

PLAYER_WHITE = 0
PLAYER_BLACK = 1

PLAYER_NAME = {}
PLAYER_NAME[PLAYER_WHITE] = 'White'
PLAYER_NAME[PLAYER_BLACK] = 'Black'

def other_player(player):
    return 1 - player

REWARD_WIN = 1.0
REWARD_LOSE = 0.0

#EXP_BASE = 'base'
EXP_P = 'p'
EXP_OFFSET = 'offset'
EXP_GRAPH = 'graph'

DEFAULT_DOMAIN_NAME = None
DEFAULT_EXP = None
DEFAULT_P = 1.0
DEFAULT_OFFSET = 0
DEFAULT_GRAPH_NAME = None
DEFAULT_CHOOSE_ROLL = 0.0
DEFAULT_TRIAL = 0

POS_ATTR = 'pos'
DIST_ATTR = 'd'
BFS_COLOR_ATTR = 'bfscolor'
VAL_ATTR = 'value'

FOLDER_DATA = '../data'
FOLDER_TRIALS = '../data/trials'
FOLDER_AVG = '../data/avg'
FOLDER_DOMAINSTATS = '../data/domainstats'
FOLDER_GRAPH = '../graph'
SUFFIX_GRAPH_OK = '-ok'
FOLDER_QTABLE_VS_SELF = '../q-table/vsself'
FOLDER_QTABLE_VS_RANDOM = '../q-table/vsrandom'
FOLDER_CONDOR = '../condor'
FILE_CONDOR_PLAN = FOLDER_CONDOR + '/plan.txt'
FOLDER_PLOT = '../plot'
FILE_PLOT_PLAN = FOLDER_PLOT + '/plan.gp'

FILE_PREFIX_SARSA = 'sarsa'
FILE_PREFIX_NTD = 'ntd'
FILE_PREFIX_HC = 'hc'
FILE_PREFIX_HC_CHALLENGE = 'hc-challenge'

class ExpParams(object):
    
    def __init__(self, domain_name, exp, graph_name, p, offset, choose_roll,
                 trial, exp_signature):
        self.domain_name = domain_name
        from domain_proxy import DomainProxy
        self.state_class = DomainProxy.load_domain_state_class_by_name(domain_name)
        self.exp = exp
        self.graph_name = graph_name
        self.p = p
        self.offset = offset
        self.choose_roll = choose_roll
        self.trial = trial
        self.exp_signature = exp_signature
        
        self.domain_signature = self.state_class.get_domain_signature()
        self.signature = self.domain_signature
        if self.exp_signature != '':
            self.signature = self.domain_signature + '-' + self.exp_signature 

    def get_filename_suffix_with_trial(self):
        return self.get_filename_suffix_no_trial() + ('-%d' % self.trial)

    def get_filename_suffix_no_trial(self):
        return self.signature
#        if self.exp == EXP_BASE:
#            return EXP_BASE
#        if self.exp == EXP_P:
#            return '%s-%1.2f' % (self.exp, self.p)
#        elif self.exp == EXP_OFFSET:
#            return '%s-%d' % (self.exp, self.offset)
#        elif self.exp == EXP_GRAPH:
#            return '%s-%s' % (self.exp, self.graph_name)
#        else:
#            return 'invalidexp'
        
    def get_custom_filename_no_trial(self, folder, file_prefix):
        filename = '%s/%s-%s.txt' % (folder, file_prefix,
                                        self.get_filename_suffix_no_trial())
        return filename
        
    def get_custom_filename_with_trial(self, folder, file_prefix):
        filename = '%s/%s-%s.txt' % (folder, file_prefix,
                                        self.get_filename_suffix_with_trial())
        return filename
        
    def get_trial_filename(self, file_prefix):
        filename = '%s/%s-%s.txt' % (FOLDER_TRIALS, file_prefix,
                                        self.get_filename_suffix_with_trial())
        return filename
        
    def get_graph_filename(self):
        if self.graph_name is not None:
            filename = '%s/%s' % (FOLDER_GRAPH, self.graph_name)
        else:
            filename = '%s/%s' % (FOLDER_GRAPH, self.get_filename_suffix_no_trial())
        return filename
        
    def is_graph_based(self):
        return (self.graph_name is not None)
    
    def is_first_trial(self):
        return self.trial == 0

class Experiment(object):
    
    exp_param_cached = None
    
    @classmethod
    def get_command_line_args(cls):
        if cls.exp_param_cached is not None:
            return cls.exp_param_cached
        
        domain_name = DEFAULT_DOMAIN_NAME
        exp = DEFAULT_EXP
        graph_name = DEFAULT_GRAPH_NAME
        p = DEFAULT_P
        offset = DEFAULT_OFFSET
        choose_roll = DEFAULT_CHOOSE_ROLL
        trial = DEFAULT_TRIAL

        options, remainder = getopt.getopt(sys.argv[1:], #@UnusedVariable
                    'd:g:o:p:c:t:',
                    ['domain=', 'graph=', 'offset=', 'p=', 'chooseroll=',
                     'trial='])        
        
        exp_signature = ''
        
        for opt, arg in options:
            if opt in ('-d', '--domain'):
                print 'Setting domain to: %s' % arg
                domain_name = arg
#                exp_signature += arg + '-'
            elif opt in ('-g', '--graph'):
                print 'Setting graph name to: %s' % arg
                graph_name = arg
                exp_signature += 'graph-%s-' % arg
            elif opt in ('-p', '--p'):
                print 'Setting p to: %s' % arg
                p = float(arg)
                exp_signature += 'p-%s-' % arg
            elif opt in ('-o', '--offset'):
                print 'Setting offset to: %s' % arg
                offset = int(arg)
                exp_signature += 'offset-%s-' % arg
            elif opt in ('-c', '--chooseroll'):
                print 'Setting choose_roll to: %s' % arg
                choose_roll = float(arg)
                exp_signature += 'chooseroll-%s-' % arg
            elif opt in ('-t', '--trial'):
                print 'Setting trial to: %s' % arg
                trial = int(arg)
#                exp_signature += 'trial-%s' % arg

        if exp_signature.rfind('-') >= 0:
            exp_signature = exp_signature[:exp_signature.rfind('-')] # remove last hyphen        

        if domain_name is None:
            print 'Please specify an experiment using:'
            print ''
            print 'python %s --domain=<name> --graph=<name> [--choose-roll=<frac>] [--trial=<trial>]' % sys.argv[0]
            print 'python %s --domain=<name> --p=<frac> [--choose-roll=<frac>] [--trial=<trial>]' % sys.argv[0]
            print 'python %s --domain=<name> --offset=<int> [--choose-roll=<frac>] [--trial=<trial>]' % sys.argv[0]
            sys.exit(-1)
        else:
            print 'Experiment signature is: %s' % exp_signature
            cls.exp_param_cached = ExpParams(domain_name, exp, graph_name, 
                                             p, offset, choose_roll, trial,
                                             exp_signature)
            return cls.exp_param_cached

    @classmethod
    def create_eval_opponent_agent(cls, exp_params):
        agent_eval = None
        from app_sarsa import AgentSarsa
        from domain import AgentRandom
        from app_optimal import AgentOptimal
        if EVAL_OPPONENT == EVAL_OPPONENT_RANDOM:
            agent_eval = AgentRandom(exp_params.state_class)
        elif EVAL_OPPONENT == EVAL_OPPONENT_SARSA:
            agent_eval = AgentSarsa(exp_params.state_class, load_knowledge = True)
        elif EVAL_OPPONENT == EVAL_OPPONENT_OPTIMAL:
            agent_eval = AgentOptimal(exp_params.state_class)
        return agent_eval

    @classmethod
    def save_stats(cls, state_class, exp_params):
        if not SAVE_STATS:
            return
    #    # visit counts to individual states
    #    filename = '../data/states-visit-count-%1.2f.txt' % state_class.p
    #    f = open(filename, 'w')
    #    for state, count_visits in sorted(state_class.states_visit_count.iteritems(), 
    #                                      key=lambda (k,v): (v,k)):
    #        f.write('%s %d\n' % (state, count_visits))
    ##        print '%s: %d' % (state, count_visits)
    #    f.close()
    
        # number of states discovered by game
#        filename = '../data/%s-%s-games-discovered-states-count.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'games-discovered-states-count')
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count)):
            f.write('%d %d\n' % (game_number, 
                                 state_class.games_discovered_states_count[game_number])) 
        f.close()
    
        # number of states discovered by game over average number of plies per game      
#        filename = '../data/%s-%s-games-discovered-states-count-over-avg-num-plies.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'games-discovered-states-count-over-avg-num-plies')
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count_over_avg_num_plies)):
            f.write('%d %f\n' % (game_number, 
                                 state_class.games_discovered_states_count_over_avg_num_plies[game_number])) 
        f.close()
    
#        filename = '../data/%s-%s-games-new-discovered-states-count.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'games-new-discovered-states-count')
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count)):
            newly_discovered_count = state_class.games_discovered_states_count[game_number]
            if game_number != 0:
                newly_discovered_count -= state_class.games_discovered_states_count[game_number - 1]
            f.write('%d %d\n' % (game_number, newly_discovered_count)) 
        f.close()
    
        # number of visits to game states sorted by first ply of visit    
#        filename = '../data/%s-%s-states-sorted-by-ply-visit-count.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'states-sorted-by-ply-visit-count')
        f = open(filename, 'w')
        for i in range(len(state_class.states_sorted_by_ply_visit_count)):
            state_sorted_by_ply_visit_count = state_class.states_sorted_by_ply_visit_count[i]
            f.write('%d: %d\n' % (i, state_sorted_by_ply_visit_count))
        f.close()        
    
        # same as above, over average num of plies per game   
#        filename = '../data/%s-%s-states-sorted-by-ply-visit-count-over-avg-num-plies.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'states-sorted-by-ply-visit-count-over-avg-num-plies')
        f = open(filename, 'w')
        for i in range(len(state_class.states_sorted_by_ply_visit_count_over_avg_num_plies)):
            state_sorted_by_ply_visit_count_over_avg_num_plies = state_class.states_sorted_by_ply_visit_count_over_avg_num_plies[i]
            f.write('%d: %f\n' % (i, state_sorted_by_ply_visit_count_over_avg_num_plies))
        f.close()
    
