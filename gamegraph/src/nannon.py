'''
Created on Dec 11, 2011

@author: reza
'''
import random
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
#from pybrain.datasets.supervised import SupervisedDataSet
#from pybrain.supervised.trainers.backprop import BackpropTrainer
from common import NUM_STATS_GAMES, PRINT_GAME_DETAIL, PRINT_GAME_RESULTS, \
    RECENT_WINNERS_LIST_SIZE, COLLECT_STATS, ALTERNATE_SEATS, Experiment,\
    USE_SEEDS, GENERATE_GRAPH
from state_graph import StateGraph

HIDDEN_UNITS = 10

class NannonDie(object):
    SIDES = [1, 2, 3, 4, 5, 6]
    
    @classmethod
    def roll(cls):
        return random.choice(cls.SIDES)

class NannonAction(object):
    ACTION_CHECKER1 = 0
    ACTION_CHECKER2 = 1
    ACTION_CHECKER3 = 2
    ACTION_FORFEIT_MOVE = 3
    ALL_CHECKERS = [ACTION_CHECKER1, ACTION_CHECKER2, ACTION_CHECKER3]
    ALL_ACTIONS = ALL_CHECKERS + [ACTION_FORFEIT_MOVE]
    NUM_CHECKERS = 3

    @classmethod
    def random_action(cls, state):
        action = cls.ACTION_FORFEIT_MOVE
        checker = random.choice(cls.ALL_CHECKERS)
        tries_left = cls.NUM_CHECKERS
        while tries_left > 0:
            move_outcome = state.get_move_outcome(checker)
            if move_outcome is not None:
                return checker
            else:
                checker = cls.next_checker(checker)
            tries_left -= 1

        return action

    @classmethod
    def next_checker(cls, checker):
        return (checker + 1) % (cls.NUM_CHECKERS)
    
class NannonState(object):
    
    # -->                                 <--   
    #   0      1   2   3   4   5   6      7
    # +---+  +---+---+---+---+---+---+  +---+
    # | w |  | w | w |   |   | b | b |  | b |
    # +---+  +---+---+---+---+---+---+  +---+
    #  Bar                               Off
    #      
    
    PLAYER_WHITE = 0
    PLAYER_BLACK = 1
    
    PLAYER_NAME = {}
    PLAYER_NAME[PLAYER_WHITE] = 'White'
    PLAYER_NAME[PLAYER_BLACK] = 'Black'
    
    CHECKER1 = 0
    CHECKER2 = 1
    CHECKER3 = 2
    FORFEIT_MOVE = 3
    NUM_CHECKERS = 3
    
    CHECKER_NAME = {}
    CHECKER_NAME[CHECKER1] = 'back'
    CHECKER_NAME[CHECKER2] = 'middle'
    CHECKER_NAME[CHECKER3] = 'front'
    CHECKER_NAME[FORFEIT_MOVE] = 'no'

    BOARD_SIZE   = 6
    BOARD_MID    = BOARD_SIZE / 2 # 3
    
    BOARD_BAR    = 0              # 0
    BOARD_START  = 1              # 1
    BOARD_END    = BOARD_SIZE     # 6
    BOARD_OFF    = BOARD_SIZE + 1 # 7
        
    # stats updated per move
    states_visit_count = {}
    states_visit_history = {}
    
    # stats updated per game
    games_discovered_states_count = []
    games_discovered_states_count_over_avg_num_plies = []

    # stats updated at the end
    states_visit_count_rel = {}
    states_visit_avg_ply_num = {}
    states_visit_first_ply_num = {}
    states_sorted_by_ply_visit_count = []
    states_sorted_by_ply_visit_count_over_avg_num_plies = []

    # graph
    G = StateGraph()
        
    def __init__(self, player_to_move, p, reentry_offset, graph_name):
        self.pos = [[0, 1, 2],
                    [0, 1, 2]]
        self.player_to_move = player_to_move
        self.roll = None
        
        
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.BOARD_REENTRY_POS1 = self.BOARD_BAR + self.reentry_offset # 0
        self.BOARD_REENTRY_POS2 = self.BOARD_MID                       # 4
        
        self.shadow = None
    
    def move(self, checker):
        if GENERATE_GRAPH:
            graph_node_from = str(self)
            
        player = self.player_to_move
        if checker == NannonAction.ACTION_FORFEIT_MOVE:
            self.switch_turn()
            return True
        
        checker_pos = self.pos[player][checker]
        other_checker1 = NannonAction.next_checker(checker)
        other_checker1_pos = self.pos[player][other_checker1]
        other_checker2 = NannonAction.next_checker(other_checker1)
        other_checker2_pos = self.pos[player][other_checker2]
        opponent = self.other_player(player)
        opponent_actual_checker1_pos = self.flip_pos(self.pos[opponent][self.CHECKER1])
        opponent_actual_checker2_pos = self.flip_pos(self.pos[opponent][self.CHECKER2])
        opponent_actual_checker3_pos = self.flip_pos(self.pos[opponent][self.CHECKER3])
        
        checker_target = checker_pos + self.roll

        # if playing checker from bar, select entry position based on p 
        if checker_pos == self.BOARD_BAR:
            offset = self.BOARD_REENTRY_POS1
            r = random.random()
            if r >= self.p:
                offset = self.BOARD_REENTRY_POS2
            checker_target += offset
        
        # truncate bear off moves
        if checker_target > self.BOARD_OFF:
            checker_target = self.BOARD_OFF
        
        hitting_opponent = (checker_target < self.BOARD_OFF) and \
                           ((checker_target == opponent_actual_checker1_pos) or
                            (checker_target == opponent_actual_checker2_pos) or
                            (checker_target == opponent_actual_checker3_pos))

        # illegal move conditions
        moving_bourne_off_checker = (checker_pos == self.BOARD_OFF)
        has_self_checker_in_target = (checker_target < self.BOARD_OFF) and \
                ((checker_target == other_checker1_pos) or 
                 (checker_target == other_checker2_pos))
        hitting_opponent_in_block = False
        if hitting_opponent:
            hitting_opponent_in_block = \
                ((self.BOARD_BAR < opponent_actual_checker1_pos < self.BOARD_OFF) and
                 (abs(checker_target - opponent_actual_checker1_pos) == 1)) or \
                ((self.BOARD_BAR < opponent_actual_checker2_pos < self.BOARD_OFF) and
                 (abs(checker_target - opponent_actual_checker2_pos) == 1)) or \
                ((self.BOARD_BAR < opponent_actual_checker3_pos < self.BOARD_OFF) and
                 (abs(checker_target - opponent_actual_checker3_pos) == 1))
        
        is_illegal_move = (moving_bourne_off_checker or
                           has_self_checker_in_target or
                           hitting_opponent_in_block)
        
        success = False
        if not is_illegal_move:
            success = True
            # move checker
            self.pos[player][checker] = checker_target
            # hit if checker from opponent is there
            if hitting_opponent:
                if checker_target == opponent_actual_checker1_pos:
                    self.pos[opponent][self.CHECKER1] = self.BOARD_BAR
                elif checker_target == opponent_actual_checker2_pos:
                    self.pos[opponent][self.CHECKER2] = self.BOARD_BAR
                elif checker_target == opponent_actual_checker3_pos:
                    self.pos[opponent][self.CHECKER3] = self.BOARD_BAR
            self.switch_turn()
            self.__fix_checker_orders()

#        elif try_more_checkers > 0:
#            if PRINT_GAME_DETAIL:
#                print '#  illegal move, playing %s checker...' % NannonState.CHECKER_NAME[other_checker1]
#            success = self.move(player, other_checker1, try_more_checkers - 1)
#        else:
#            if PRINT_GAME_DETAIL:
#                print '#  can\'t move either of checkers.'
            
        if GENERATE_GRAPH:
            if success:
                graph_node_to = str(self)
                self.G.add_edge(graph_node_from, graph_node_to, checker)
            
        return success
    
    def get_move_outcome(self, checker):
        if self.shadow is None:
            self.shadow = NannonState(self.player_to_move,
                                      self.p, self.reentry_offset,
                                      self.graph_name)
        else:
            self.shadow.player_to_move = self.player_to_move
        self.shadow.roll = self.roll
        self.shadow.pos[0][0] = self.pos[0][0]
        self.shadow.pos[0][1] = self.pos[0][1]
        self.shadow.pos[0][2] = self.pos[0][2]
        self.shadow.pos[1][0] = self.pos[1][0]
        self.shadow.pos[1][1] = self.pos[1][1]
        self.shadow.pos[1][2] = self.pos[1][2]
        # move shadow
#        print 'Self before move: %s' % self.pos
#        print 'Shadow before move: %s' % self.shadow.pos
        success = self.shadow.move(checker)
#        print 'Self after move: %s' % self.pos
#        print 'Shadow after move: %s' % self.shadow.pos
#        print '-'
        if success:
            return self.shadow
        else:
            return None

    def switch_turn(self):
        self.player_to_move = self.other_player(self.player_to_move)
        self.roll = NannonDie.roll()
            
    def is_final(self):
        return self.has_player_won(self.PLAYER_WHITE) or \
               self.has_player_won(self.PLAYER_BLACK)
    
    def has_player_won(self, player):
        checker1_pos = self.pos[player][self.CHECKER1]
        checker2_pos = self.pos[player][self.CHECKER2]
        checker3_pos = self.pos[player][self.CHECKER3]
        return (checker1_pos == self.BOARD_OFF) and (checker2_pos == self.BOARD_OFF) and (checker3_pos == self.BOARD_OFF)
    
    @classmethod
    def other_player(cls, player):
        return 1 - player
        
    @classmethod
    def flip_pos(cls, pos):
        return cls.BOARD_OFF - pos

    def __fix_checker_orders(self):
        for player in [self.PLAYER_WHITE, self.PLAYER_BLACK]:
            for checker1 in [self.CHECKER1, self.CHECKER2]:
                for checker2 in range(checker1 + 1, self.NUM_CHECKERS):
                    if self.pos[player][checker1] > self.pos[player][checker2]:
                        (self.pos[player][checker1], self.pos[player][checker2]) = \
                        (self.pos[player][checker2], self.pos[player][checker1])
        
    def print_state(self):
        
        encoding = self.encode()
        
        print '#   0      1   2   3   4   5   6      7  '
        print '# +---+  +---+---+---+---+---+---+  +---+'
        print '# %s' % encoding
        print '# +---+  +---+---+---+---+---+---+  +---+'
        print '#                                                '

    def encode(self):
        cell_content = [''] * (self.BOARD_OFF + 1)
        for player in [self.PLAYER_WHITE, self.PLAYER_BLACK]:
            for checker in range(self.NUM_CHECKERS):
                pos = self.pos[player][checker]
                if (player == self.PLAYER_BLACK):
                    pos = self.flip_pos(pos)
                letter = self.PLAYER_NAME[player].lower()[0]
                cell_content[pos] += letter
                
        for pos in range(self.BOARD_OFF + 1):
            if cell_content[pos] == 'ww':
                cell_content[pos] = cell_content[pos].ljust(3)
            elif cell_content[pos] == 'bb':
                cell_content[pos] = cell_content[pos].rjust(3)
            else:
                cell_content[pos] = cell_content[pos].center(3)

        encoding = '|%s|  |%s|%s|%s|%s|%s|%s|  |%s|' % (cell_content[0], cell_content[1], cell_content[2], cell_content[3], cell_content[4], cell_content[5], cell_content[6], cell_content[7])
        return encoding

    def __repr__(self):        
        return self.encode()
    
    def __str__(self):
        return '%d-%d%d%d-%d%d%d-%d' % (self.player_to_move,
                                self.pos[0][0], self.pos[0][1], self.pos[0][2], 
                                self.pos[1][0], self.pos[1][1], self.pos[1][2],
                                self.roll)

#    def __str__(self):
#        return '%d-%d%d%d-%d%d%d-%d  %s' % (self.player_to_move,
#                                self.pos[0][0], self.pos[0][1], self.pos[0][2], 
#                                self.pos[1][0], self.pos[1][1], self.pos[1][2],
#                                self.roll, self.encode())

    def compute_per_ply_stats(self, current_ply_number):
        if COLLECT_STATS:
            state = self.encode()
            if state in self.states_visit_count:
                self.states_visit_count[state] += 1
            else:
                self.states_visit_count[state] = 1
    
            if state in self.states_visit_history:
                self.states_visit_history[state].append(current_ply_number)
            else:
                self.states_visit_history[state] = [current_ply_number]

    def compute_per_game_stats(self, game_number):
        if COLLECT_STATS:
            self.games_discovered_states_count.append(len(self.states_visit_count))

    @classmethod
    def compute_overall_stats(cls, avg_num_plies_per_game):
        if COLLECT_STATS:
            # compute number of states discovered per game normalized by average game lengths
            for game_number in range(len(cls.games_discovered_states_count)):
                game_discovered_states_count = cls.games_discovered_states_count[game_number]
                game_discovered_states_count_over_avg_num_plies = float(game_discovered_states_count) / avg_num_plies_per_game
                cls.games_discovered_states_count_over_avg_num_plies.append(game_discovered_states_count_over_avg_num_plies)
        
            # compute the average and first ply number where each state is visited
            for state, visit_history in cls.states_visit_history.iteritems():
                state_visit_avg_ply_num = float(sum(visit_history)) / len(visit_history)
                state_visit_first_ply_num = min(visit_history)
                cls.states_visit_avg_ply_num[state] = state_visit_avg_ply_num
                cls.states_visit_first_ply_num[state] = state_visit_first_ply_num
                
            # compute the relative visit counts to states 
            sum_states_visit_count = sum(cls.states_visit_count.itervalues())
            for state, state_visit_count in cls.states_visit_count.iteritems():
                state_visit_count_rel = float(state_visit_count) / sum_states_visit_count
                cls.states_visit_count_rel[state] = state_visit_count_rel
    
            # compute visit counts to game positions
    #        latest_position = max(cls.states_visit_avg_ply_num.itervalues())
            for state, state_first_ply_number_visit in sorted(cls.states_visit_first_ply_num.iteritems(), key=lambda (k,v): (v,k)): #@UnusedVariable
                state_visit_count = cls.states_visit_count[state]
                cls.states_sorted_by_ply_visit_count.append(state_visit_count)
                state_visit_count_over_avg_num_plies = float(state_visit_count) / avg_num_plies_per_game 
                cls.states_sorted_by_ply_visit_count_over_avg_num_plies.append(state_visit_count_over_avg_num_plies)
        
class NannonAgent(object):
    
    def __init__(self):
        self.state = None
    
    def set_state(self, state):
        self.state = state
    
    def begin_episode(self):
        pass
    
    def end_episode(self, reward):
        pass

    def select_action(self):
        raise NotImplementedError

class NannonAgentRandom(NannonAgent):
    
    def __init__(self):
        super(NannonAgentRandom, self).__init__()
    
    def select_action(self):
        return NannonAction.random_action(self.state)
    
class NannonAgentNeural(NannonAgent):
    
    def __init__(self, outputdim, init_weights = None):
        super(NannonAgentNeural, self).__init__()
        self.inputdim = (NannonState.BOARD_SIZE) * 2 + (6 * 2)       + 2
        #               6 points: |1w |1b / 0-3 checkers on bar and off / |white's turn |black's turn
        self.outputdim = outputdim
        self.hiddendim = HIDDEN_UNITS
        self.network = buildNetwork(self.inputdim, self.hiddendim, self.outputdim,
                                    hiddenclass = SigmoidLayer, bias = True)
        if init_weights is not None:
            self.network.params[:] = [init_weights] * len(self.network.params)
    
    def select_action(self):
        action_values = []
        for action in Domain.ActionClass.ALL_CHECKERS:
            move_outcome = self.state.get_move_outcome(action)
            if move_outcome is not None:
                move_value = self.get_state_value(move_outcome)
                # insert a random number to break the ties
                action_values.append(((move_value, random.random()), action))
            
        if len(action_values) > 0:
            action_values_sorted = sorted(action_values, reverse=True)
            action = action_values_sorted[0][1]
        else:
            action = NannonAction.ACTION_FORFEIT_MOVE
            
        return action
        
    def encode_network_input(self, state):
        network_in = [0] * self.inputdim
        for player in [NannonState.PLAYER_WHITE, NannonState.PLAYER_BLACK]:
            for checker in NannonAction.ALL_CHECKERS:
                pos = state.pos[player][checker]
                if pos == NannonState.BOARD_BAR:
                    offset = player * 3
                elif NannonState.BOARD_BAR < pos < NannonState.BOARD_OFF:
                    offset = 6 + (pos - 1) * 2 + player
                elif pos == NannonState.BOARD_OFF:
                    offset = 6 + NannonState.BOARD_SIZE * 2 + player * 3
                else:
                    print 'Invalid checker position when encoding network input!'
                
                # Seeing a second checker on the same point?
                while network_in[offset] == 1:
                    offset += 1
                network_in[offset] = 1
                
        turn_offset = self.inputdim - 2
        network_in[turn_offset + state.player_to_move] = 1
        return network_in
    
    def __repr__(self):
        return str(self.network.params)
    
class NannonGame(object):
    
    REWARD_WIN = 1.0
    REWARD_LOSE = 0.0
    
    def __init__(self, game_number, agent_white, agent_black,
                 player_to_start_game, p, reentry_offset, graph_name):
        self.game_number = game_number
        self.agents = [None, None]
        self.agents[NannonState.PLAYER_WHITE] = agent_white
        self.agents[NannonState.PLAYER_BLACK] = agent_black
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.state = NannonState(player_to_start_game, self.p, 
                                 self.reentry_offset, self.graph_name)
        
        # first roll
        roll = 0
        while roll == 0:
            roll = abs(NannonDie.roll() - NannonDie.roll())
        self.state.roll = roll
        NannonState.G.add_source(str(self.state), player_to_start_game)
        
        agent_white.set_state(self.state)
        agent_black.set_state(self.state)
        self.count_plies = 0
        
    def play(self):
            
        while not self.state.is_final():
#            if self.player_to_play == NannonState.PLAYER_WHITE:
#                self.state.compute_per_ply_stats(self.count_plies)
            self.state.compute_per_ply_stats(self.count_plies)
            if PRINT_GAME_DETAIL:
                self.state.print_state()
            action = self.agents[self.state.player_to_move].select_action()
            if PRINT_GAME_DETAIL:
                print '#  %s rolls %d, playing %s checker...' % \
                        (NannonState.PLAYER_NAME[self.state.player_to_move], 
                         self.state.roll, NannonState.CHECKER_NAME[action])
            self.state.move(action)
            if PRINT_GAME_DETAIL:
                print '# '
            self.count_plies += 1
        
        if PRINT_GAME_DETAIL:
            self.state.print_state()

        self.state.compute_per_game_stats(self.game_number)
        
        winner = None
        loser = None
        if self.state.has_player_won(NannonState.PLAYER_WHITE):
            winner = NannonState.PLAYER_WHITE
            loser = NannonState.PLAYER_BLACK
        elif self.state.has_player_won(NannonState.PLAYER_BLACK):
            winner = NannonState.PLAYER_BLACK
            loser = NannonState.PLAYER_WHITE
        else:
            print 'Error: Game ended without winning player!'
        
        self.agents[winner].end_episode(self.REWARD_WIN)
        self.agents[loser].end_episode(self.REWARD_LOSE)
        
        NannonState.G.add_sink(str(self.state), winner)
        
        return winner
        
    def get_count_plies(self):
        return self.count_plies
    
    @classmethod
    def get_max_episode_reward(cls):
        return cls.REWARD_WIN
        
class NannonGameSet(object):
    
    def __init__(self, num_games, agent1, agent2, p, reentry_offset, graph_name,
                 print_learning_progress = False, progress_filename = None):
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
        
        if USE_SEEDS:
            random_seeds = []
            for i in range(self.num_games / 4): #@UnusedVariable
                random_seeds.append(random.random())
            
        # agent1, agent2
        players = [self.agent1, self.agent2]
        seats_reversed = False
        count_wins = [0, 0]
        recent_winners = [] # 0 for agent1, 1 for agent2
        
        player_to_start_game = NannonState.PLAYER_WHITE
        for game_number in range(self.num_games):
            if ALTERNATE_SEATS:
                if game_number % 2 == 0:
                    players[:] = [players[1], players[0]]
                    seats_reversed = not seats_reversed
            # load random seed
            if USE_SEEDS:
                random.seed(random_seeds[game_number / 4])
            # setup game
            players[0].begin_episode()
            players[1].begin_episode()
            game = NannonGame(game_number, players[0], players[1],
                              player_to_start_game, self.p, self.reentry_offset,
                              self.graph_name)
            winner = game.play()
            if seats_reversed:
                winner = NannonState.other_player(winner)
            count_wins[winner] += 1
            if self.print_learning_progress:
                if len(recent_winners) > RECENT_WINNERS_LIST_SIZE - 1:
                    recent_winners.pop(0)
                recent_winners.append(winner)
            if PRINT_GAME_RESULTS:
                print 'Game %2d won by %s in %2d plies' % (game_number, NannonState.PLAYER_NAME[winner], game.count_plies)
            if self.print_learning_progress:
                win_ratio = float(recent_winners.count(0)) / len(recent_winners)
                print 'First agent\'s recent win ratio: %.2f' % win_ratio 
                if self.progress_filename is not None:
                    f.write('%d %f\n' % (game_number, win_ratio))
            self.sum_count_plies += game.get_count_plies()
            player_to_start_game = NannonState.other_player(player_to_start_game)

        return count_wins
    
        if self.progress_filename is not None:
            f.close()

    def get_sum_count_plies(self):
        return self.sum_count_plies

class Domain(object):
    name = 'nannon'
    DieClass = NannonDie
    StateClass = NannonState
    ActionClass = NannonAction
    GameClass = NannonGame
    GameSetClass = NannonGameSet
    AgentClass = NannonAgent
    AgentRandomClass = NannonAgentRandom
    AgentNeuralClass = NannonAgentNeural

    print 'Loading Domain: %s' % name
    print 

if __name__ == '__main__':
    (p, reentry_offset, graph_name) = Experiment.get_command_line_args()
    
    num_games = NUM_STATS_GAMES
    agent_white = NannonAgentRandom()
    agent_black = NannonAgentRandom()
    game_set = NannonGameSet(num_games, agent_white, agent_black,
                             p, reentry_offset, graph_name)
    count_wins = game_set.run()
    total_plies = game_set.get_sum_count_plies()
    
    if GENERATE_GRAPH:
        NannonState.G.print_stats()
        NannonState.G.convert_freq_to_prob()
        filename = '../graph/%s-%s' % (Domain.name, Experiment.get_file_suffix_no_trial())
        NannonState.G.save_to_file(filename)
        
    # printing overall stats
    print '----'
    print 'P was: %.2f' % p
    print 'Re-entry offset was: %d' % reentry_offset
    print 'Graph name was: %s' % graph_name
    
    avg_num_plies_per_game = float(total_plies) / num_games
    print 'Games won by White: %d, Black: %d' % (count_wins[NannonState.PLAYER_WHITE], count_wins[NannonState.PLAYER_BLACK])
    print 'Average plies per game: %.2f' % avg_num_plies_per_game 
    
    if COLLECT_STATS:
        total_states_visited = len(NannonState.states_visit_count)
        print 'Total number of states encountered: %d' % total_states_visited
        print 'per 1000 plies: %.2f' % (float(total_states_visited) / avg_num_plies_per_game)
        
        avg_visit_count_to_states = sum(NannonState.states_visit_count.itervalues()) / float(total_states_visited)
        print 'Average number of visits to states: %.2f' % avg_visit_count_to_states
        print 'per 1000 plies: %.2f' % (float(avg_visit_count_to_states) / avg_num_plies_per_game)
        
        var_visit_count_to_states = sum([(e - avg_visit_count_to_states) ** 2 for e in NannonState.states_visit_count.itervalues()]) / float(total_states_visited) 
        print 'Variance of number of visits to states: %.2f' % var_visit_count_to_states
        
        NannonState.compute_overall_stats(avg_num_plies_per_game)
        Experiment.write_stats(NannonState, Domain.name)
