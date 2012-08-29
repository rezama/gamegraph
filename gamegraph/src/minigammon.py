'''
Created on Dec 5, 2011

@author: reza
'''
import random
import copy
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from common import Experiment, COLLECT_STATS, RECORD_GRAPH, POS_ATTR,\
    PLAYER_BLACK, PLAYER_WHITE, PLAYER_NAME, other_player
from state_graph import StateGraph
from Queue import Queue

HIDDEN_UNITS = 10

class MiniGammonDie(object):
    SIDES = [1, 2]
    
    @classmethod
    def roll(cls):
        return random.choice(cls.SIDES)

class MiniGammonAction(object):
    ACTION_CHECKER1 = 0
    ACTION_CHECKER2 = 1
    ACTION_FORFEIT_MOVE = 2
    ALL_CHECKERS = [ACTION_CHECKER1, ACTION_CHECKER2]
    ALL_ACTIONS = ALL_CHECKERS + [ACTION_FORFEIT_MOVE]
    NUM_CHECKERS = 2
    
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

class MiniGammonState(object):
    
    # Old version:
    #
    # -->           <--   
    #   1   2   3   4   
    # +---+---+---+---+
    # | w |   |   | b |
    # +---+---+---+---+
    #   
    #   5   6   7   8   
    # +---+---+---+---+
    # | w |   |   | b |
    # +---+---+---+---+
    #   
    #       0       9     
    #     +---+   +---+
    # Bar |   |   |   | Off
    #     +---+   +---+
    #      
    
    # New version:
    #        -->                           <--   
    #   0      1   2   3   4   5   6   7   8      9
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    # |   |  |ww |   |   |   |   |   |   | bb|  |   |
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    #  Bar                                       Off
    #      
    
    CHECKER1 = 0
    CHECKER2 = 1
    FORFEIT_MOVE = 2
    NUM_CHECKERS = 2
        
    CHECKER_NAME = {}
    CHECKER_NAME[CHECKER1] = 'back'
    CHECKER_NAME[CHECKER2] = 'front'
    CHECKER_NAME[FORFEIT_MOVE] = 'no'

    BOARD_SIZE   = 8
    BOARD_MID    = BOARD_SIZE / 2 # 4
    
    BOARD_BAR    = 0              # 0
    BOARD_START  = 1              # 1
    BOARD_END    = BOARD_SIZE     # 8
    BOARD_OFF    = BOARD_SIZE + 1 # 9
        
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
    RECORD_GAME_GRAPH = StateGraph(MiniGammonDie.SIDES, 1, MiniGammonAction.ALL_ACTIONS)
    GAME_GRAPH = None
    
    def __init__(self, exp_params, player_to_move):
        self.pos = [[self.BOARD_START, self.BOARD_START],
                    [self.BOARD_START, self.BOARD_START]]
        self.exp_params = exp_params
        self.player_to_move = player_to_move

        self.current_g_id = None
        self.roll = None
        
        self.BOARD_REENTRY_POS1 = self.BOARD_BAR + self.exp_params.offset # 0
        self.BOARD_REENTRY_POS2 = self.BOARD_MID                          # 4
        
        self.is_graph_based = (self.exp_params.graph_name is not None)
        
        if self.is_graph_based:
            if MiniGammonState.GAME_GRAPH is None:
                filename = '../graph/%s-%s' % (Domain.name, exp_params.get_file_suffix_no_trial())
                MiniGammonState.GAME_GRAPH = StateGraph.load_from_file(filename)
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
            if (checker == MiniGammonAction.ACTION_FORFEIT_MOVE) and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id, 
                                            other_player(self.player_to_move))
                print "Encountered unexplored graph node: %s" % self.GAME_GRAPH.get_node_name(self.current_g_id)
                print "Marking as final."
        else:
            if checker == MiniGammonAction.ACTION_FORFEIT_MOVE:
                success = True
            else:
                player = self.player_to_move
                checker_pos = self.pos[player][checker]
                other_checker = MiniGammonAction.next_checker(checker)
                other_checker_pos = self.pos[player][other_checker]
                opponent = other_player(player)
                opponent_actual_checker1_pos = self.flip_pos(self.pos[opponent][self.CHECKER1])
                opponent_actual_checker2_pos = self.flip_pos(self.pos[opponent][self.CHECKER2])
                
                checker_target = checker_pos + self.roll
        
                # if playing checker from bar, select entry position based on p 
                if checker_pos == self.BOARD_BAR:
                    offset = self.BOARD_REENTRY_POS1
                    r = random.random()
                    if r >= self.exp_params.p:
                        offset = self.BOARD_REENTRY_POS2
                    checker_target += offset
                
                # if playing a 2 from the last point
                if checker_target > self.BOARD_OFF:
                    checker_target = self.BOARD_OFF
                    
                # if both checkers from opponent sit together
                opponent_has_block = (opponent_actual_checker1_pos == opponent_actual_checker2_pos) and\
                                     (opponent_actual_checker1_pos != self.BOARD_OFF)
                
                hitting_opponent = (opponent_actual_checker1_pos == checker_target) or \
                                   (opponent_actual_checker2_pos == checker_target)
                
                # illegal move conditions
                moving_checker_while_other_is_on_bar = (checker_pos != self.BOARD_BAR) and \
                        (other_checker_pos == self.BOARD_BAR)
                moving_bourne_off_checker = (checker_pos == self.BOARD_OFF)
                premature_bear_off = (checker_target > self.BOARD_END) and \
                        (other_checker_pos <= self.BOARD_MID)
                hitting_opponent_in_block = hitting_opponent and opponent_has_block
                
                is_illegal_move = (moving_checker_while_other_is_on_bar or
                                   moving_bourne_off_checker or
                                   premature_bear_off or
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
                    self.__fix_checker_orders()
                        
        #        elif must_try_other_checker:
        #            if PRINT_GAME_DETAIL:
        #                print '#  illegal move, playing %s checker...' % MiniGammonState.CHECKER_NAME[other_checker]
        #            success = self.move(player, other_checker, must_try_other_checker = False)
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
            self.shadow = MiniGammonState(self.exp_params, self.player_to_move) 
        else:
            self.shadow.player_to_move = self.player_to_move
        self.shadow.roll = self.roll
        self.shadow.pos[0][0] = self.pos[0][0]
        self.shadow.pos[0][1] = self.pos[0][1]
        self.shadow.pos[1][0] = self.pos[1][0]
        self.shadow.pos[1][1] = self.pos[1][1]
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
        self.roll = MiniGammonDie.roll()
    
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
            return (checker1_pos == self.BOARD_OFF) and \
                   (checker2_pos == self.BOARD_OFF)
    
    @classmethod
    def flip_pos(cls, pos):
        return cls.BOARD_OFF - pos

    @classmethod
    def generate_graph(cls, exp_params):
        g = StateGraph(MiniGammonDie.SIDES, 1, MiniGammonAction.ALL_ACTIONS)
        s = MiniGammonState(exp_params, PLAYER_WHITE)
        s_key = s.board_config()
        s_pos = [[s.pos[0][0], s.pos[0][1]],
                 [s.pos[1][0], s.pos[1][1]]]
        s_color = s.player_to_move
        s_id = g.add_node(s_key, s_color)
        g.set_attr(s_id, POS_ATTR, s_pos)
        g.set_as_source(s_id, s_color)
        is_state_processed = {}
        is_state_queued = {}
        Q = Queue()
        Q.put((s_key, s_pos, s_color))
        is_state_queued[s_key] = True
        while not Q.empty():
            (s_key, s_pos, s_color) = Q.get()
            is_state_processed[s_key] = True
            print 'Fully processed %d, %d in queue, processing %s...\r' % \
                    (len(is_state_processed), Q.qsize(), s_key), 
            s.pos = s_pos
            s.player_to_move = s_color
            s_id = g.get_node_id(s_key)
            for roll in MiniGammonDie.SIDES:
                s.roll = roll
                must_consider_forfeit = True
                for action in MiniGammonAction.ALL_ACTIONS:
                    if (action != MiniGammonAction.ACTION_FORFEIT_MOVE) or must_consider_forfeit:
                        sp = s.get_move_outcome(action)
                        if sp is not None:
                            must_consider_forfeit = False
                            sp_key = sp.board_config()
                            if is_state_processed.has_key(sp_key):
                                sp_id = g.get_node_id(sp_key)
                                g.add_edge(s_id, roll, action, sp_id)
                            else:
                                sp_pos = [[sp.pos[0][0], sp.pos[0][1]],
                                          [sp.pos[1][0], sp.pos[1][1]]]
                                sp_color = sp.player_to_move
                                sp_id = g.add_node(sp_key, sp_color)
                                g.set_attr(sp_id, POS_ATTR, sp_pos)
                                g.add_edge(s_id, roll, action, sp_id)
                                if sp.is_final():
                                    g.set_as_sink(sp_id, other_player(sp.player_to_move))
                                if not is_state_queued.has_key(sp_key):
                                    Q.put((sp_key, sp_pos, sp_color))
                                    is_state_queued[sp_key] = True
            print ''
        return g

    def __fix_checker_orders(self):
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            if self.pos[player][self.CHECKER1] > self.pos[player][self.CHECKER2]:
                (self.pos[player][self.CHECKER1], self.pos[player][self.CHECKER2]) = \
                (self.pos[player][self.CHECKER2], self.pos[player][self.CHECKER1])
        
    def print_state(self):
        
        encoding = self.encode()
        
        print '#   0      1   2   3   4   5   6   7   8      9  '
        print '# +---+  +---+---+---+---+---+---+---+---+  +---+'
        print '# %s' % encoding
        print '# +---+  +---+---+---+---+---+---+---+---+  +---+'
        print '#                                                '

    def encode(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)[2:]
        cell_content = [''] * (self.BOARD_OFF + 1)
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in [self.CHECKER1, self.CHECKER2]:
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

        encoding = '|%s|  |%s|%s|%s|%s|%s|%s|%s|%s|  |%s|' % (cell_content[0], cell_content[1], cell_content[2], cell_content[3], cell_content[4], cell_content[5], cell_content[6], cell_content[7], cell_content[8], cell_content[9])
        return encoding

    def __repr__(self):        
        return self.encode()
    
    def __str__(self):
        return self.board_config_and_roll()

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%d-%d%d%d%d' % (self.player_to_move,
                                self.pos[0][0], self.pos[0][1], 
                                self.pos[1][0], self.pos[1][1])

    def board_config_and_roll(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id) + \
                ('-%d' % self.roll)
        else:
            return '%d-%d%d%d%d-%d' % (self.player_to_move,
                                self.pos[0][0], self.pos[0][1], 
                                self.pos[1][0], self.pos[1][1],
                                self.roll)

    def compute_per_ply_stats(self, current_ply_number):
        if COLLECT_STATS:
            state = self.encode()
            # FIXME: change this to self.board_config()
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
        
class MiniGammonAgent(object):
    
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

class MiniGammonAgentRandom(MiniGammonAgent):
    
    def __init__(self):
        super(MiniGammonAgentRandom, self).__init__()
    
    def select_action(self):
        return MiniGammonAction.random_action(self.state)
    
class MiniGammonAgentNeural(MiniGammonAgent):
    
    def __init__(self, outputdim, init_weights = None):
        super(MiniGammonAgentNeural, self).__init__()
        self.inputdim = (MiniGammonState.BOARD_SIZE + 2) * 4   + 2
        #               10 points: |1w |2w |1b |2b             |white's turn |black's turn
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
            action = MiniGammonAction.ACTION_FORFEIT_MOVE
            
        return action
        
    def encode_network_input(self, state):
        network_in = [0] * self.inputdim
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in MiniGammonAction.ALL_CHECKERS:
                pos = state.pos[player][checker]
                offset = pos * 4 + player * 2
                # Seeing a second checker on the same point?
                if network_in[offset] == 1:
#                    network_in[offset] = 0
                    network_in[offset + 1] = 1
                else:
                    network_in[offset] = 1
        turn_offset = self.inputdim - 2
        network_in[turn_offset + state.player_to_move] = 1
        return network_in
    
    def __repr__(self):
        return str(self.network.params)
    
class Domain(object):
    name = 'minigammon'
    DieClass = MiniGammonDie
    StateClass = MiniGammonState
    ActionClass = MiniGammonAction
    AgentClass = MiniGammonAgent
    AgentRandomClass = MiniGammonAgentRandom
    AgentNeuralClass = MiniGammonAgentNeural

    print 'Loading Domain: %s' % name
    print 

if __name__ == '__main__':
    Experiment.run_random_games(Domain)