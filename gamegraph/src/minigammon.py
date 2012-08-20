'''
Created on Dec 5, 2011

@author: reza
'''
import random
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from common import NUM_STATS_GAMES, PRINT_GAME_DETAIL, PRINT_GAME_RESULTS, \
    RECENT_WINNERS_LIST_SIZE, COLLECT_STATS, ALTERNATE_SEATS, Experiment,\
    USE_SEEDS, GENERATE_GRAPH
from state_graph import StateGraph

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
    
    PLAYER_WHITE = 0
    PLAYER_BLACK = 1
    
    PLAYER_NAME = {}
    PLAYER_NAME[PLAYER_WHITE] = 'White'
    PLAYER_NAME[PLAYER_BLACK] = 'Black'
    
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
    RECORD_GAME_GRAPH = StateGraph(MiniGammonDie.SIDES)
    GAME_GRAPH = None
    
    def __init__(self, player_to_move, p, reentry_offset, graph_name):
        self.pos = [[self.BOARD_START, self.BOARD_START],
                    [self.BOARD_START, self.BOARD_START]]
        self.graph_node = None
        self.player_to_move = player_to_move
        self.roll = None
        
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.BOARD_REENTRY_POS1 = self.BOARD_BAR + self.reentry_offset # 0
        self.BOARD_REENTRY_POS2 = self.BOARD_MID                       # 4
        
        self.is_graph_based = (self.graph_name is not None)
        
        if self.is_graph_based:
            if self.GAME_GRAPH is None:
                filename = '../graph/%s-%s' % (Domain.name, Experiment.get_file_suffix_no_trial())
                self.GAME_GRAPH = StateGraph.load_from_file(filename)
            self.graph_node = self.GAME_GRAPH.get_random_source(self.player_to_move)

        self.shadow = None
    
    def move(self, checker):
        success = False
        if GENERATE_GRAPH and not self.is_graph_based:
            graph_node_from = self.board_config()
            current_roll = self.roll
                
        if self.is_graph_based:
            next_node = self.GAME_GRAPH.move(self.graph_node, self.roll,
                                             checker)
            if next_node is not None:
                self.graph_node = next_node
                success = True
        else:
            if checker == MiniGammonAction.ACTION_FORFEIT_MOVE:
                success = True
            else:
                player = self.player_to_move
                checker_pos = self.pos[player][checker]
                other_checker = MiniGammonAction.next_checker(checker)
                other_checker_pos = self.pos[player][other_checker]
                opponent = self.other_player(player)
                opponent_actual_checker1_pos = self.flip_pos(self.pos[opponent][self.CHECKER1])
                opponent_actual_checker2_pos = self.flip_pos(self.pos[opponent][self.CHECKER2])
                
                checker_target = checker_pos + self.roll
        
                # if playing checker from bar, select entry position based on p 
                if checker_pos == self.BOARD_BAR:
                    offset = self.BOARD_REENTRY_POS1
                    r = random.random()
                    if r >= self.p:
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
            if GENERATE_GRAPH and not self.is_graph_based:
                graph_node_to = self.board_config()
                self.RECORD_GAME_GRAPH.add_edge(graph_node_from, current_roll,
                                                checker, graph_node_to)
        return success
    
    def get_move_outcome(self, checker):
        if self.shadow is None:
            self.shadow = MiniGammonState(self.player_to_move, 
                                          self.p, self.reentry_offset,
                                          self.graph_name)
        else:
            self.shadow.player_to_move = self.player_to_move
        self.shadow.roll = self.roll
        self.shadow.pos[0][0] = self.pos[0][0]
        self.shadow.pos[0][1] = self.pos[0][1]
        self.shadow.pos[1][0] = self.pos[1][0]
        self.shadow.pos[1][1] = self.pos[1][1]
        self.shadow.graph_node = self.graph_node
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
        self.roll = MiniGammonDie.roll()
    
    def is_final(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.is_sink(self.graph_node)
        else:
            return self.has_player_won(self.PLAYER_WHITE) or \
                   self.has_player_won(self.PLAYER_BLACK)
    
    def has_player_won(self, player):
        if self.is_graph_based:
            return (self.GAME_GRAPH.get_sink_color(self.graph_node) == player)
        else:
            checker1_pos = self.pos[player][self.CHECKER1]
            checker2_pos = self.pos[player][self.CHECKER2]
            return (checker1_pos == self.BOARD_OFF) and \
                   (checker2_pos == self.BOARD_OFF)
    
    @classmethod
    def other_player(cls, player):
        return 1 - player
        
    @classmethod
    def flip_pos(cls, pos):
        return cls.BOARD_OFF - pos

    def __fix_checker_orders(self):
        for player in [self.PLAYER_WHITE, self.PLAYER_BLACK]:
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
            return self.graph_node[2:]
        cell_content = [''] * (self.BOARD_OFF + 1)
        for player in [self.PLAYER_WHITE, self.PLAYER_BLACK]:
            for checker in [self.CHECKER1, self.CHECKER2]:
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

        encoding = '|%s|  |%s|%s|%s|%s|%s|%s|%s|%s|  |%s|' % (cell_content[0], cell_content[1], cell_content[2], cell_content[3], cell_content[4], cell_content[5], cell_content[6], cell_content[7], cell_content[8], cell_content[9])
        return encoding

    def __repr__(self):        
        return self.encode()
    
    def __str__(self):
        if self.is_graph_based:
            return self.graph_node + ('-%d' % self.roll)
        else:
            return '%d-%d%d%d%d-%d' % (self.player_to_move,
                                self.pos[0][0], self.pos[0][1], 
                                self.pos[1][0], self.pos[1][1],
                                self.roll)
    def board_config(self):
        if self.is_graph_based:
            return self.graph_node
        else:
            return '%d-%d%d%d%d' % (self.player_to_move,
                                self.pos[0][0], self.pos[0][1], 
                                self.pos[1][0], self.pos[1][1])

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
        for player in [MiniGammonState.PLAYER_WHITE, MiniGammonState.PLAYER_BLACK]:
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
    
class MiniGammonGame(object):
    
    REWARD_WIN = 1.0
    REWARD_LOSE = 0.0
    
    def __init__(self, game_number, agent_white, agent_black,
                 player_to_start_game, p, reentry_offset, graph_name):
        self.game_number = game_number
        self.agents = [None, None]
        self.agents[MiniGammonState.PLAYER_WHITE] = agent_white
        self.agents[MiniGammonState.PLAYER_BLACK] = agent_black
        self.p = p
        self.reentry_offset = reentry_offset
        self.graph_name = graph_name
        self.state = MiniGammonState(player_to_start_game, self.p,
                                     self.reentry_offset, self.graph_name)

        # initial die roll
        self.state.roll = MiniGammonDie.roll()
        if GENERATE_GRAPH:
            MiniGammonState.RECORD_GAME_GRAPH.add_source(self.state.board_config(),
                                                         player_to_start_game)
        
        agent_white.set_state(self.state)
        agent_black.set_state(self.state)
        self.count_plies = 0
        
    def play(self):
        while not self.state.is_final():
#            if self.player_to_play == MiniGammonState.PLAYER_WHITE:
#                self.state.compute_per_ply_stats(self.count_plies)
            self.state.compute_per_ply_stats(self.count_plies)
            if PRINT_GAME_DETAIL:
                self.state.print_state()
            action = self.agents[self.state.player_to_move].select_action()
            if PRINT_GAME_DETAIL:
                print '#  %s rolls %d, playing %s checker...' % \
                        (MiniGammonState.PLAYER_NAME[self.state.player_to_move], 
                         self.state.roll, MiniGammonState.CHECKER_NAME[action])
            self.state.move(action)
            if PRINT_GAME_DETAIL:
                print '# '
            self.count_plies += 1
        
        if PRINT_GAME_DETAIL:
            self.state.print_state()

        self.state.compute_per_game_stats(self.game_number)
        
        winner = None
        loser = None
        if self.state.has_player_won(MiniGammonState.PLAYER_WHITE):
            winner = MiniGammonState.PLAYER_WHITE
            loser = MiniGammonState.PLAYER_BLACK
        elif self.state.has_player_won(MiniGammonState.PLAYER_BLACK):
            winner = MiniGammonState.PLAYER_BLACK
            loser = MiniGammonState.PLAYER_WHITE
        else:
            print 'Error: Game ended without winning player!'
        
        self.agents[winner].end_episode(self.REWARD_WIN)
        self.agents[loser].end_episode(self.REWARD_LOSE)
        
        if GENERATE_GRAPH:
            MiniGammonState.RECORD_GAME_GRAPH.add_sink(self.state.board_config(),
                                                       winner)
        
        return winner
        
    def get_count_plies(self):
        return self.count_plies
    
    @classmethod
    def get_max_episode_reward(cls):
        return cls.REWARD_WIN
        
class MiniGammonGameSet(object):
    
    def __init__(self, num_games, agent1, agent2, p, reentry_offset,
                 graph_name, print_learning_progress = False, 
                 progress_filename = None):
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
        
        player_to_start_game = MiniGammonState.PLAYER_WHITE
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
            game = MiniGammonGame(game_number, players[0], players[1],
                                  player_to_start_game, self.p,
                                  self.reentry_offset, self.graph_name)
            winner = game.play()
            if seats_reversed:
                winner = MiniGammonState.other_player(winner)
            count_wins[winner] += 1
            if self.print_learning_progress:
                if len(recent_winners) > RECENT_WINNERS_LIST_SIZE - 1:
                    recent_winners.pop(0)
                recent_winners.append(winner)
            if PRINT_GAME_RESULTS:
                print 'Game %2d won by %s in %2d plies' % (game_number, MiniGammonState.PLAYER_NAME[winner], game.count_plies)
            if self.print_learning_progress:
                win_ratio = float(recent_winners.count(0)) / len(recent_winners)
                print 'First agent\'s recent win ratio: %.2f' % win_ratio 
                if self.progress_filename is not None:
                    f.write('%d %f\n' % (game_number, win_ratio))
            self.sum_count_plies += game.get_count_plies()
            player_to_start_game = MiniGammonState.other_player(player_to_start_game)
            
        if self.progress_filename is not None:
            f.close()
            
        return count_wins
    
    def get_sum_count_plies(self):
        return self.sum_count_plies

class Domain(object):
    name = 'minigammon'
    DieClass = MiniGammonDie
    StateClass = MiniGammonState
    ActionClass = MiniGammonAction
    GameClass = MiniGammonGame
    GameSetClass = MiniGammonGameSet
    AgentClass = MiniGammonAgent
    AgentRandomClass = MiniGammonAgentRandom
    AgentNeuralClass = MiniGammonAgentNeural

    print 'Loading Domain: %s' % name
    print 

if __name__ == '__main__':
    (p, reentry_offset, graph_name) = Experiment.get_command_line_args()
    
    num_games = NUM_STATS_GAMES
    agent_white = MiniGammonAgentRandom()
    agent_black = MiniGammonAgentRandom()
    game_set = MiniGammonGameSet(num_games, agent_white, agent_black,
                                 p, reentry_offset, graph_name)

    count_wins = game_set.run()
    total_plies = game_set.get_sum_count_plies()
    
    if GENERATE_GRAPH:
        MiniGammonState.RECORD_GAME_GRAPH.print_stats()
        MiniGammonState.RECORD_GAME_GRAPH.convert_freq_to_prob()
        filename = '../graph/%s-%s' % (Domain.name, Experiment.get_file_suffix_no_trial())
        MiniGammonState.RECORD_GAME_GRAPH.save_to_file(filename)
    
    # printing overall stats
    print '----'
    print 'P was: %.2f' % p
    print 'Re-entry offset was: %d' % reentry_offset
    print 'Graph name was: %s' % graph_name
        
    avg_num_plies_per_game = float(total_plies) / num_games
    print 'Games won by White: %d, Black: %d' % (count_wins[MiniGammonState.PLAYER_WHITE], count_wins[MiniGammonState.PLAYER_BLACK])
    print 'Average plies per game: %.2f' % avg_num_plies_per_game 
    
    if COLLECT_STATS:
        total_states_visited = len(MiniGammonState.states_visit_count)
        print 'Total number of states encountered: %d' % total_states_visited
        print 'per 1000 plies: %.2f' % (float(total_states_visited) / avg_num_plies_per_game)
        
        avg_visit_count_to_states = sum(MiniGammonState.states_visit_count.itervalues()) / float(total_states_visited)
        print 'Average number of visits to states: %.2f' % avg_visit_count_to_states
        print 'per 1000 plies: %.2f' % (float(avg_visit_count_to_states) / avg_num_plies_per_game)
        
        var_visit_count_to_states = sum([(e - avg_visit_count_to_states) ** 2 for e in MiniGammonState.states_visit_count.itervalues()]) / float(total_states_visited) 
        print 'Variance of number of visits to states: %.2f' % var_visit_count_to_states
        
        MiniGammonState.compute_overall_stats(avg_num_plies_per_game)
        Experiment.write_stats(MiniGammonState, Domain.name)
