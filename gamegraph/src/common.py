'''
Created on Dec 11, 2011

@author: reza
'''
import sys
import copy
import random
import gzip
from params import RECORD_GRAPH, PRINT_GAME_DETAIL,\
    GAMESET_PROGRESS_REPORT_USE_GZIP, ALTERNATE_SEATS, USE_SEEDS,\
    GAMESET_RECENT_WINNERS_LIST_SIZE, PRINT_GAME_RESULTS,\
    GAMESET_PROGRESS_REPORT_EVERY_N_GAMES, NUM_STATS_GAMES, SAVE_STATS, COLLECT_STATS

PLAYER_WHITE = 0
PLAYER_BLACK = 1

PLAYER_NAME = {}
PLAYER_NAME[PLAYER_WHITE] = 'White'
PLAYER_NAME[PLAYER_BLACK] = 'Black'

def other_player(player):
    return 1 - player

REWARD_WIN = 1.0
REWARD_LOSE = 0.0

DEFAULT_P = 1.0
DEFAULT_OFFSET = 0
DEFAULT_GRAPH_NAME = None
DEFAULT_TRIAL = 0

EXP_BASE = 'base'
EXP_P = 'p'
EXP_OFFSET = 'offset'
EXP_GRAPH = 'graph'

POS_ATTR = 'pos'
DIST_ATTR = 'd'
BFS_COLOR_ATTR = 'bfscolor'
VAL_ATTR = 'value'

FOLDER_DATA = '../data'
FOLDER_TRIALS = '../data/trials'
FOLDER_AVG = '../data/avg'
FOLDER_DOMAINSTATS = '../data/domainstats'
FOLDER_GRAPH = '../graph'
FOLDER_RLTABLE_VS_SELF = '../rl-table/vsself'
FOLDER_RLTABLE_VS_RANDOM = '../rl-table/vsrandom'

FILE_PREFIX_TD = 'td'
FILE_PREFIX_HC = 'hc'
FILE_PREFIX_HC_CHALLENGE = 'hc-challenge'
FILE_PREFIX_RL = 'rl'

class Game(object):
        
    def __init__(self, domain, exp_params, game_number, agent_white, agent_black,
                 player_to_start_game):
        self.domain = domain
        self.game_number = game_number
        self.agents = [None, None]
        self.agents[PLAYER_WHITE] = agent_white
        self.agents[PLAYER_BLACK] = agent_black
        self.exp_params = exp_params
        self.state = domain.StateClass(exp_params, player_to_start_game)

        # initial die roll
        self.state.roll = domain.DieClass.roll()
        if RECORD_GRAPH and not self.state.is_graph_based:
            record_graph = self.state.RECORD_GAME_GRAPH
            s = record_graph.add_node(self.state.board_config(), self.state.player_to_move)
            if not record_graph.has_attr(s, POS_ATTR):
                record_graph.set_attr(s, POS_ATTR, copy.deepcopy(self.state.pos))
                record_graph.set_as_source(s, player_to_start_game)
        
        agent_white.set_state(self.state)
        agent_black.set_state(self.state)
        self.count_plies = 0
        
    def play(self):
        while not self.state.is_final():
#            if self.player_to_play == PLAYER_WHITE:
#                self.state.compute_per_ply_stats(self.count_plies)
            self.state.compute_per_ply_stats(self.count_plies)
            if PRINT_GAME_DETAIL:
                self.state.print_state()
            action = self.agents[self.state.player_to_move].select_action()
            if PRINT_GAME_DETAIL:
                print '#  %s rolls %d, playing %s checker...' % \
                        (PLAYER_NAME[self.state.player_to_move], 
                         self.state.roll, self.StateClass.CHECKER_NAME[action])
            self.state.move(action)
            if PRINT_GAME_DETAIL:
                print '# '
            self.count_plies += 1
        
        if PRINT_GAME_DETAIL:
            self.state.print_state()

        self.state.compute_per_game_stats(self.game_number)
        
        winner = None
        loser = None
        if self.state.has_player_won(PLAYER_WHITE):
            winner = PLAYER_WHITE
            loser = PLAYER_BLACK
        elif self.state.has_player_won(PLAYER_BLACK):
            winner = PLAYER_BLACK
            loser = PLAYER_WHITE
        else:
            print 'Error: Game ended without winning player!'
        
        self.agents[winner].end_episode(REWARD_WIN)
        self.agents[loser].end_episode(REWARD_LOSE)
        
        if RECORD_GRAPH and not self.state.is_graph_based:
            sink_name = self.state.board_config()
            sink_id = self.state.RECORD_GAME_GRAPH.get_node_id(sink_name)
            self.state.RECORD_GAME_GRAPH.set_as_sink(sink_id, winner)
        
        return winner
        
    def get_count_plies(self):
        return self.count_plies
    
    @classmethod
    def get_max_episode_reward(cls):
        return REWARD_WIN
        
class GameSet(object):
    
    def __init__(self, domain, exp_params, num_games, agent1, agent2,
                 print_learning_progress = False, 
                 progress_filename = None):
        self.domain = domain
        self.num_games = num_games
        self.agent1 = agent1
        self.agent2 = agent2
        self.exp_params = exp_params
        self.print_learning_progress = print_learning_progress
        self.progress_filename = progress_filename

        self.sum_count_plies = 0 
    
    def run(self):
        if self.progress_filename is not None:
            if GAMESET_PROGRESS_REPORT_USE_GZIP:
                f = gzip.open(self.progress_filename + '.gz', 'w')
            else:
                f = open(self.progress_filename, 'w')

        game_series_size = 1
        if ALTERNATE_SEATS:
            game_series_size *= 2
        
        if USE_SEEDS:
            random_seeds = []
            for i in range(self.num_games / game_series_size): #@UnusedVariable
                random_seeds.append(random.random())
            
        # agent1, agent2
        players = [self.agent1, self.agent2]
        seats_reversed = False
        count_wins = [0, 0]
        recent_winners = [] # 0 for agent1, 1 for agent2
        
        player_to_start_game = PLAYER_WHITE
        for game_number in range(self.num_games):
            if ALTERNATE_SEATS:
#                if game_number % game_series_size == 0:
                    players[:] = [players[1], players[0]]
                    seats_reversed = not seats_reversed
            # load random seed
            if USE_SEEDS:
                random.seed(random_seeds[game_number / game_series_size])
            # setup game
            players[0].begin_episode()
            players[1].begin_episode()
            game = Game(self.domain, self.exp_params, game_number, 
                        players[0], players[1], player_to_start_game)
            winner = game.play()
            if seats_reversed:
                winner = other_player(winner)
            count_wins[winner] += 1
            if self.print_learning_progress:
                if len(recent_winners) > GAMESET_RECENT_WINNERS_LIST_SIZE - 1:
                    recent_winners.pop(0)
                recent_winners.append(winner)
            if PRINT_GAME_RESULTS:
                print 'Game %2d won by %s in %2d plies' % (game_number, 
                                        PLAYER_NAME[winner], game.count_plies)
            if self.print_learning_progress:
                if game_number % GAMESET_PROGRESS_REPORT_EVERY_N_GAMES == 0:
                    win_ratio = float(recent_winners.count(0)) / len(recent_winners)
                    print 'Played game %2d, recent win ratio: %.2f' % (
                                                    game_number, win_ratio) 
                    if self.progress_filename is not None:
                        f.write('%d %f\n' % (game_number, win_ratio))
            self.sum_count_plies += game.get_count_plies()
#            player_to_start_game = other_player(player_to_start_game)
            
        if self.progress_filename is not None:
            f.close()
            
        return count_wins
    
    def get_sum_count_plies(self):
        return self.sum_count_plies

class ExpParams:
    
    def __init__(self, exp, p, offset, graph_name, trial):
        self.exp = exp
        self.p = p
        self.offset = offset
        self.graph_name = graph_name
        self.trial = trial

    def get_filename_suffix_with_trial(self):
        return self.get_filename_suffix_no_trial() + ('-%d' % self.trial)

    def get_filename_suffix_no_trial(self):
        if self.exp == EXP_BASE:
            return EXP_BASE
        elif self.exp == EXP_P:
            return '%s-%1.2f' % (self.exp, self.p)
        elif self.exp == EXP_OFFSET:
            return '%s-%d' % (self.exp, self.offset)
        elif self.exp == EXP_GRAPH:
            return '%s-%s' % (self.exp, self.graph_name)
        else:
            return 'invalidexp'
        
    def get_custom_filename_no_trial(self, folder, file_prefix, domain_name):
        filename = '%s/%s-%s-%s.txt' % (folder, file_prefix, domain_name,
                                        self.get_filename_suffix_no_trial()())
        return filename
        
    def get_custom_filename_with_trial(self, folder, file_prefix, domain_name):
        filename = '%s/%s-%s-%s.txt' % (folder, file_prefix, domain_name,
                                        self.get_filename_suffix_with_trial()())
        return filename
        
    def get_trial_filename(self, file_prefix, domain_name):
        filename = '%s/%s-%s-%s.txt' % (FOLDER_TRIALS, file_prefix, domain_name,
                                        self.get_filename_suffix_with_trial())
        return filename
        
    def get_graph_filename(self, domain_name):
        filename = '%s/%s-%s' % (FOLDER_GRAPH, domain_name,
                                 self.get_filename_suffix_no_trial())
        return filename
        
    def is_graph_based(self):
        return (self.graph_name is not None)
    
    def is_first_trial(self):
        return self.trial == 0

        
class Experiment:
    
    @classmethod
    def get_command_line_args(cls):
        if len(sys.argv) < 3:
            print 'You can specify an experiment mode with:'
            print 'python %s graph <name> [<trial>]' % sys.argv[0]
            print 'python %s p <p> [<trial>]' % sys.argv[0]
            print 'python %s offset <offset> [<trial>]' % sys.argv[0]
            exp = EXP_BASE
            p = DEFAULT_P
            offset = DEFAULT_OFFSET
            graph_name = DEFAULT_GRAPH_NAME
            trial = DEFAULT_TRIAL
        else:
            p = DEFAULT_P
            offset = DEFAULT_OFFSET
            graph_name = DEFAULT_GRAPH_NAME
            trial = DEFAULT_TRIAL
        
            if len(sys.argv) == 4:
                trial = int(sys.argv[3])

            exp = sys.argv[1]
            if exp == EXP_P:
                p = float(sys.argv[2])
            elif exp == EXP_OFFSET:
                offset = int(sys.argv[2])
            elif exp == EXP_GRAPH:
                graph_name = sys.argv[2]

        if exp == EXP_P:
            print 'Using: p = %.2f, trial = %d' % (p, trial)
        elif exp == EXP_OFFSET:
            print 'Using: offset = %d, trial = %d' % (offset, trial)
        elif exp == EXP_GRAPH:
            print 'Using: graph = %s, trial = %d' % (graph_name, trial)
        else:
            print 'Using: base, trial = %d' % trial
        print 
        return ExpParams(exp, p, offset, graph_name, trial)

    @classmethod
    def run_random_games(cls, domain):
        exp_params = cls.get_command_line_args()
        
        num_games = NUM_STATS_GAMES
        agent_white = domain.AgentRandomClass()
        agent_black = domain.AgentRandomClass()
        game_set = GameSet(domain, exp_params, num_games, agent_white, agent_black)
    
        count_wins = game_set.run()
        total_plies = game_set.get_sum_count_plies()
        
        if RECORD_GRAPH and (exp_params.graph_name is None):
            record_graph = domain.StateClass.RECORD_GAME_GRAPH
            record_graph.print_stats()
            record_graph.adjust_probs()
            filename = exp_params.get_graph_filename()
            filename = '../graph/%s-%s' % (domain.name, Experiment.get_filename_suffix_no_trial())
            record_graph.save_to_file(filename)
        
        # printing overall stats
        print '----'
        print 'P was: %.2f' % exp_params.p
        print 'Re-entry offset was: %d' % exp_params.offset
        print 'Graph name was: %s' % exp_params.graph_name
            
        if SAVE_STATS:
            # general info
#            filename = '../data/%s-%s-overall-stats.txt' % (domain.name, 
#                                            cls.get_filename_suffix_with_trial())
            filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS,
                                            'overall-stats', domain.name)
            f = open(filename, 'w')
            
        avg_num_plies_per_game = float(total_plies) / num_games
        print 'Games won by agent: %d, opponent: %d' % (count_wins[PLAYER_WHITE], 
                                                        count_wins[PLAYER_BLACK])
        print 'Average plies per game: %.2f' % avg_num_plies_per_game 
        if SAVE_STATS:
            f.write('Games won by agent: %d, opponent: %d' % (count_wins[PLAYER_WHITE],
                                                              count_wins[PLAYER_BLACK]))
            f.write('Average plies per game: %.2f' % avg_num_plies_per_game) 
            
        if COLLECT_STATS:
            total_states_visited = len(domain.StateClass.states_visit_count)
            print 'Total number of states encountered: %d' % total_states_visited
            print 'per 1000 plies: %.2f' % (float(total_states_visited) / 
                                            avg_num_plies_per_game)
            if SAVE_STATS:
                f.write('Total number of states encountered: %d' % total_states_visited)
                f.write('per 1000 plies: %.2f' % (float(total_states_visited) / 
                                                  avg_num_plies_per_game))
            
            avg_visit_count_to_states = sum(domain.StateClass.states_visit_count.itervalues()) / float(total_states_visited)
            print 'Average number of visits to states: %.2f' % avg_visit_count_to_states
            print 'per 1000 plies: %.2f' % (float(avg_visit_count_to_states) / 
                                            avg_num_plies_per_game)
            if SAVE_STATS:
                f.write('Average number of visits to states: %.2f' % avg_visit_count_to_states)
                f.write('per 1000 plies: %.2f' % (float(avg_visit_count_to_states) / 
                                                  avg_num_plies_per_game))
            
            sum_squared_diffs = sum([(e - avg_visit_count_to_states) ** 2 
                                     for e in domain.StateClass.states_visit_count.itervalues()])
            var_visit_count_to_states =  sum_squared_diffs / float(total_states_visited) 
            print 'Variance of number of visits to states: %.2f' % var_visit_count_to_states
            if SAVE_STATS:
                f.write('Variance of number of visits to states: %.2f' % var_visit_count_to_states)
            
            domain.StateClass.compute_overall_stats(avg_num_plies_per_game)
            Experiment.save_stats(domain.StateClass, domain, exp_params)        
    
        if SAVE_STATS:
            f.close()

    @classmethod
    def save_stats(cls, state_class, domain, exp_params):
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
                    'games-discovered-states-count', domain.name)
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count)):
            f.write('%d %d\n' % (game_number, 
                                 state_class.games_discovered_states_count[game_number])) 
        f.close()
    
        # number of states discovered by game over average number of plies per game      
#        filename = '../data/%s-%s-games-discovered-states-count-over-avg-num-plies.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'games-discovered-states-count-over-avg-num-plies', domain.name)
        f = open(filename, 'w')
        for game_number in range(len(state_class.games_discovered_states_count_over_avg_num_plies)):
            f.write('%d %f\n' % (game_number, 
                                 state_class.games_discovered_states_count_over_avg_num_plies[game_number])) 
        f.close()
    
#        filename = '../data/%s-%s-games-new-discovered-states-count.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'games-new-discovered-states-count', domain.name)
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
                    'states-sorted-by-ply-visit-count', domain.name)
        f = open(filename, 'w')
        for i in range(len(state_class.states_sorted_by_ply_visit_count)):
            state_sorted_by_ply_visit_count = state_class.states_sorted_by_ply_visit_count[i]
            f.write('%d: %d\n' % (i, state_sorted_by_ply_visit_count))
        f.close()        
    
        # same as above, over average num of plies per game   
#        filename = '../data/%s-%s-states-sorted-by-ply-visit-count-over-avg-num-plies.txt' % (domain.name, cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS, 
                    'states-sorted-by-ply-visit-count-over-avg-num-plies', domain.name)
        f = open(filename, 'w')
        for i in range(len(state_class.states_sorted_by_ply_visit_count_over_avg_num_plies)):
            state_sorted_by_ply_visit_count_over_avg_num_plies = state_class.states_sorted_by_ply_visit_count_over_avg_num_plies[i]
            f.write('%d: %f\n' % (i, state_sorted_by_ply_visit_count_over_avg_num_plies))
        f.close()
    
