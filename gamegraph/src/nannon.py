'''
Created on Dec 11, 2011

@author: reza
'''
import random
import copy
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
#from pybrain.datasets.supervised import SupervisedDataSet
#from pybrain.supervised.trainers.backprop import BackpropTrainer
from common import Experiment, COLLECT_STATS, RECORD_GRAPH, POS_ATTR,\
    PLAYER_BLACK, PLAYER_WHITE, PLAYER_NAME, other_player
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
    RECORD_GAME_GRAPH = StateGraph(NannonAction.ALL_ACTIONS, NannonDie.SIDES)
    GAME_GRAPH = None
        
    def __init__(self, player_to_move, p, reentry_offset, graph_name):
        self.pos = [[0, 1, 2],
                    [0, 1, 2]]
        self.current_g_id = None
        self.player_to_move = player_to_move
        self.roll = None
        
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.BOARD_REENTRY_POS1 = self.BOARD_BAR + self.reentry_offset # 0
        self.BOARD_REENTRY_POS2 = self.BOARD_MID                       # 4
        
        self.is_graph_based = (self.graph_name is not None)
        
        if self.is_graph_based:
            if NannonState.GAME_GRAPH is None:
                filename = '../graph/%s-%s' % (Domain.name, Experiment.get_file_suffix_no_trial())
                NannonState.GAME_GRAPH = StateGraph.load_from_file(filename)
            self.current_g_id = self.GAME_GRAPH.get_random_source(self.player_to_move)

        self.shadow = None
    
    def move(self, checker):
        success = False
        if RECORD_GRAPH and not self.is_graph_based:
            node_from_name = self.board_config()
            current_roll = self.roll
            
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if (checker == NannonAction.ACTION_FORFEIT_MOVE) and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id, 
                                            other_player(self.player_to_move))
                print "Encountered unexplored graph node: %s" % self.GAME_GRAPH.get_node_name(self.current_g_id)
                print "Marking as final."
        else:        
            if checker == NannonAction.ACTION_FORFEIT_MOVE:
                success = True
            else:
                player = self.player_to_move
                checker_pos = self.pos[player][checker]
                other_checker1 = NannonAction.next_checker(checker)
                other_checker1_pos = self.pos[player][other_checker1]
                other_checker2 = NannonAction.next_checker(other_checker1)
                other_checker2_pos = self.pos[player][other_checker2]
                opponent = other_player(player)
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
                    self.__fix_checker_orders()
        
        #        elif try_more_checkers > 0:
        #            if PRINT_GAME_DETAIL:
        #                print '#  illegal move, playing %s checker...' % NannonState.CHECKER_NAME[other_checker1]
        #            success = self.move(player, other_checker1, try_more_checkers - 1)
        #        else:
        #            if PRINT_GAME_DETAIL:
        #                print '#  can\'t move either of checkers.'
                
        if success:
            self.switch_turn()
            if RECORD_GRAPH and not self.is_graph_based:
                node_from_id = self.RECORD_GAME_GRAPH.get_node_id(node_from_name)
                node_to_name = self.board_config()
                node_to_id = self.RECORD_GAME_GRAPH.add_node(node_to_name, self.player_to_move)
                if not self.RECORD_GAME_GRAPH.has_attr(node_to_id, POS_ATTR):
                    self.RECORD_GAME_GRAPH.set_attr(node_to_id, POS_ATTR, copy.deepcopy(self.pos))
                self.RECORD_GAME_GRAPH.add_edge(node_from_id, current_roll,
                                                checker, node_to_id)
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
        self.shadow.current_g_id = self.current_g_id
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
        self.player_to_move = other_player(self.player_to_move)
        self.roll = NannonDie.roll()
            
    def is_final(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.is_sink(self.current_g_id)
        else:
            return self.has_player_won(PLAYER_WHITE) or \
                   self.has_player_won(PLAYER_BLACK)
    
    def has_player_won(self, player):
        if self.is_graph_based:
            return (self.GAME_GRAPH.get_sink_color(self.current_g_id) == player)
        else:
            checker1_pos = self.pos[player][self.CHECKER1]
            checker2_pos = self.pos[player][self.CHECKER2]
            checker3_pos = self.pos[player][self.CHECKER3]
            return (checker1_pos == self.BOARD_OFF) and \
                   (checker2_pos == self.BOARD_OFF) and \
                   (checker3_pos == self.BOARD_OFF)
    
    @classmethod
    def flip_pos(cls, pos):
        return cls.BOARD_OFF - pos

    def __fix_checker_orders(self):
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
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
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)[2:]
        else:
            cell_content = [''] * (self.BOARD_OFF + 1)
            for player in [PLAYER_WHITE, PLAYER_BLACK]:
                for checker in range(self.NUM_CHECKERS):
                    pos = self.pos[player][checker]
                    if (player == PLAYER_BLACK):
                        pos = self.flip_pos(pos)
                    letter = PLAYER_NAME[player].lower()[0]
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
        return self.board_config_and_roll()

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%d-%d%d%d-%d%d%d' % (self.player_to_move,
                                self.pos[0][0], self.pos[0][1], self.pos[0][2], 
                                self.pos[1][0], self.pos[1][1], self.pos[1][2])

    def board_config_and_roll(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id) + \
                ('-%d' % self.roll)
        else:
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
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
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
    
class Domain(object):
    name = 'nannon'
    DieClass = NannonDie
    StateClass = NannonState
    ActionClass = NannonAction
    AgentClass = NannonAgent
    AgentRandomClass = NannonAgentRandom
    AgentNeuralClass = NannonAgentNeural

    print 'Loading Domain: %s' % name
    print 

if __name__ == '__main__':
    Experiment.run_random_games(Domain)
    