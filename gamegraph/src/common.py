'''
Created on Dec 11, 2011

@author: reza
'''
import sys
import copy
import random

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
DEFAULT_REENTRY_OFFSET = 0
DEFAULT_GRAPH_NAME = None
DEFAULT_TRIAL = 0

NUM_TRIALS = 10

EXP_VARY_P = 'p'
EXP_VARY_REENTRY = 'offset'
EXP_VARY_GRAPH = 'graph'

POS_ATTR = 'pos'

ALTERNATE_SEATS = True
USE_SEEDS = True
ALTERNATE_SEATS = False
USE_SEEDS = False

RECENT_WINNERS_LIST_SIZE = 3000

COLLECT_STATS = False
SAVE_STATS = False

RECORD_GRAPH = False

NUM_STATS_GAMES = 10000

PRINT_GAME_DETAIL = False
PRINT_GAME_RESULTS = False
#PRINT_GAME_DETAIL = True
#PRINT_GAME_RESULTS = True

class Game(object):
        
    def __init__(self, domain, game_number, agent_white, agent_black,
                 player_to_start_game, p, reentry_offset, graph_name):
        self.domain = domain
        self.game_number = game_number
        self.agents = [None, None]
        self.agents[PLAYER_WHITE] = agent_white
        self.agents[PLAYER_BLACK] = agent_black
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.state = domain.StateClass(player_to_start_game, self.p,
                                       self.reentry_offset, self.graph_name)

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
    
    def __init__(self, domain, num_games, agent1, agent2,
                 p, reentry_offset, graph_name,
                 print_learning_progress = False, 
                 progress_filename = None):
        self.domain = domain
        self.num_games = num_games
        self.agent1 = agent1
        self.agent2 = agent2
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.print_learning_progress = print_learning_progress
        self.progress_filename = progress_filename

        self.sum_count_plies = 0 
    
    def run(self):
        if self.progress_filename is not None:
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
                if game_number % game_series_size == 0:
                    players[:] = [players[1], players[0]]
                    seats_reversed = not seats_reversed
            # load random seed
            if USE_SEEDS:
                random.seed(random_seeds[game_number / game_series_size])
            # setup game
            players[0].begin_episode()
            players[1].begin_episode()
            game = Game(self.domain, game_number, players[0], players[1], 
                        player_to_start_game,
                        self.p, self.reentry_offset, self.graph_name)
            winner = game.play()
            if seats_reversed:
                winner = other_player(winner)
            count_wins[winner] += 1
            if self.print_learning_progress:
                if len(recent_winners) > RECENT_WINNERS_LIST_SIZE - 1:
                    recent_winners.pop(0)
                recent_winners.append(winner)
            if PRINT_GAME_RESULTS:
                print 'Game %2d won by %s in %2d plies' % (game_number, PLAYER_NAME[winner], game.count_plies)
            if self.print_learning_progress:
                win_ratio = float(recent_winners.count(0)) / len(recent_winners)
                print 'Played game %2d, recent win ratio: %.2f' % (game_number, win_ratio) 
                if self.progress_filename is not None:
                    f.write('%d %f\n' % (game_number, win_ratio))
            self.sum_count_plies += game.get_count_plies()
#            player_to_start_game = other_player(player_to_start_game)
            
        if self.progress_filename is not None:
            f.close()
            
        return count_wins
    
    def get_sum_count_plies(self):
        return self.sum_count_plies

class Experiment:
    exp = None
    p = None
    offset = None
    trial = None
    
    @classmethod
    def get_file_suffix(cls):
        return cls.get_file_suffix_no_trial() + ('-%d' % cls.trial)

    @classmethod
    def get_file_suffix_no_trial(cls):
        if cls.exp == EXP_VARY_P:
            return '%s-%1.2f' % (cls.exp, cls.p)
        elif cls.exp == EXP_VARY_REENTRY:
            return '%s-%d' % (cls.exp, cls.offset)
        else:
            return '%s-%s' % (cls.exp, cls.graph_name)
        
    @classmethod
    def get_command_line_args(cls):
        if len(sys.argv) < 4:
            print 'You can specify an experiment mode with:'
            print 'python %s p <p> <trial>' % sys.argv[0]
            print 'python %s offset <offset> <trial>' % sys.argv[0]
            print 'python %s graph <name> <trial>' % sys.argv[0]
            exp = EXP_VARY_REENTRY
            p = DEFAULT_P
            offset = DEFAULT_REENTRY_OFFSET
            trial = DEFAULT_TRIAL
            graph_name = DEFAULT_GRAPH_NAME
        else:
            p = DEFAULT_P
            offset = DEFAULT_REENTRY_OFFSET
            graph_name = DEFAULT_GRAPH_NAME
        
            exp = sys.argv[1]
            if exp == EXP_VARY_P:
                p = float(sys.argv[2])
            elif exp == EXP_VARY_REENTRY:
                offset = int(sys.argv[2])
            else:
                graph_name = sys.argv[2]
            
            trial = int(sys.argv[3])
    
        cls.exp = exp
        cls.p = p
        cls.offset = offset
        cls.graph_name = graph_name
        cls.trial = trial
        print 'Using: p = %.2f, offset = %d, graph = %s, trial = %d' % (
                                            p, offset, graph_name, trial)
        print 
        return (p, offset, graph_name) 

    @classmethod
    def run_random_games(cls, domain):
        (p, reentry_offset, graph_name) = Experiment.get_command_line_args()
        
        num_games = NUM_STATS_GAMES
        agent_white = domain.AgentRandomClass()
        agent_black = domain.AgentRandomClass()
        game_set = GameSet(domain, num_games, agent_white, agent_black,
                           p, reentry_offset, graph_name)
    
        count_wins = game_set.run()
        total_plies = game_set.get_sum_count_plies()
        
        if RECORD_GRAPH and (graph_name is None):
            record_graph = domain.StateClass.RECORD_GAME_GRAPH
            record_graph.print_stats()
            record_graph.adjust_probs()
            filename = '../graph/%s-%s' % (domain.name, Experiment.get_file_suffix_no_trial())
            record_graph.save_to_file(filename)
        
        # printing overall stats
        print '----'
        print 'P was: %.2f' % p
        print 'Re-entry offset was: %d' % reentry_offset
        print 'Graph name was: %s' % graph_name
            
        avg_num_plies_per_game = float(total_plies) / num_games
        print 'Games won by White: %d, Black: %d' % (count_wins[PLAYER_WHITE], count_wins[PLAYER_BLACK])
        print 'Average plies per game: %.2f' % avg_num_plies_per_game 
        
        if COLLECT_STATS:
            total_states_visited = len(domain.StateClass.states_visit_count)
            print 'Total number of states encountered: %d' % total_states_visited
            print 'per 1000 plies: %.2f' % (float(total_states_visited) / avg_num_plies_per_game)
            
            avg_visit_count_to_states = sum(domain.StateClass.states_visit_count.itervalues()) / float(total_states_visited)
            print 'Average number of visits to states: %.2f' % avg_visit_count_to_states
            print 'per 1000 plies: %.2f' % (float(avg_visit_count_to_states) / avg_num_plies_per_game)
            
            var_visit_count_to_states = sum([(e - avg_visit_count_to_states) ** 2 for e in domain.StateClass.states_visit_count.itervalues()]) / float(total_states_visited) 
            print 'Variance of number of visits to states: %.2f' % var_visit_count_to_states
            
            domain.StateClass.compute_overall_stats(avg_num_plies_per_game)
            Experiment.save_stats(domain.StateClass, domain.name)        
    
    @classmethod
    def save_stats(cls, state_class, domain_name):
        if not SAVE_STATS:
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
    
