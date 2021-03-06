'''
Created on Sep 17, 2012

@author: reza
'''
import random
from Queue import Queue

from common import (PLAYER_BLACK, PLAYER_NAME, PLAYER_NAME_SHORT, PLAYER_WHITE,
                    POS_ATTR, Action, Die, other_player)
from params import COLLECT_STATS, GENERATE_GRAPH_REPORT_EVERY_N_STATES
from state_graph import StateGraph


class State(object):

    GAME_GRAPH = None
    # RECORD_GAME_GRAPH = StateGraph(self.die_object.get_all_sides(), 1,
    #                                self.action_object.get_all_actions())

    # To be overridden by subclasses.
    DOMAIN_NAME = None
    BOARD_SIZE = None
    NUM_CHECKERS = None
    NUM_DIE_SIDES = None

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

    def __init__(self, exp_params, board_size, num_die_sides, num_checkers,
                 player_to_move):
        self.exp_params = exp_params
        self.board_size = board_size
        self.num_die_sides = num_die_sides
        self.num_checkers = num_checkers
        self.player_to_move = player_to_move

        self.board_mid = board_size / 2  # 4

        self.board_bar = 0               # 0
        self.board_start = 1             # 1
        self.board_end = board_size      # 8
        self.board_off = board_size + 1  # 9

        self.board_reentry_pos1 = self.board_bar + self.exp_params.offset  # 0
        self.board_reentry_pos2 = self.board_mid                           # 4

        self.die_object = Die(num_die_sides)
        self.action_object = Action(num_checkers)

        self.current_g_id = None
        self.roll = None
        self.stochastic_p = None

        self.pos = self.init_pos()

        self.is_graph_based = (self.exp_params.graph_name is not None)

        if self.is_graph_based:
            self.load_own_graph()
            self.current_g_id = self.GAME_GRAPH.get_random_source(self.player_to_move)

        self.shadow = None

    def load_own_graph(self):
        if self.GAME_GRAPH is None:
            self.__class__.GAME_GRAPH = StateGraph.load(self.exp_params)

    @classmethod
    def get_domain_signature(cls):
        return '%s-%d%d%d' % (cls.DOMAIN_NAME, cls.BOARD_SIZE,
                              cls.NUM_CHECKERS, cls.NUM_DIE_SIDES)

    def init_pos(self):
        raise NotImplementedError

    def copy_pos(self, target_pos, source_pos):
        raise NotImplementedError

    def board_config(self):
        raise NotImplementedError

    def board_config_and_roll(self):
        raise NotImplementedError

    def flip_pos(self, pos):
        return self.board_off - pos

    def fix_checker_orders(self):
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            self.pos[player].sort()

    def get_move_outcome(self, checker):
        # always create state with WHITE to move to prevent problems with
        # searching the graph for BLACK sources
        # if self.shadow is None:
        #     self.shadow = self.__class__(self.exp_params, self.player_to_move)
        # else:
        #     self.shadow.player_to_move = self.player_to_move

        # Reuse existing shadow for better performance.
        if self.shadow is None:
            # Even though this class's constructor takes many more parameters,
            # the constructors of all state subclasses need only a player color.
            self.shadow = self.__class__(self.exp_params, PLAYER_WHITE)  # pylint: disable=no-value-for-parameter
        self.shadow.player_to_move = self.player_to_move

        self.shadow.roll = self.roll
        # self.shadow.pos[0][0] = self.pos[0][0]
        # self.shadow.pos[0][1] = self.pos[0][1]
        # self.shadow.pos[1][0] = self.pos[1][0]
        # self.shadow.pos[1][1] = self.pos[1][1]
        self.copy_pos(self.shadow.pos, self.pos)
        self.shadow.current_g_id = self.current_g_id
        # move shadow
        # print 'Self before move: %s' % self.pos
        # print 'Shadow before move: %s' % self.shadow.pos
        success = self.shadow.move(checker)
        # print 'Self after move: %s' % self.pos
        # print 'Shadow after move: %s' % self.shadow.pos
        # print '-'
        if success:
            return self.shadow
        else:
            return None

    @classmethod
    def can_forfeit_move(cls):
        return True

    def switch_turn(self):
        self.player_to_move = other_player(self.player_to_move)
        self.roll = self.die_object.roll()
        self.stochastic_p = random.random()

    def reroll_dice(self):
        self.roll = self.die_object.roll()

    def is_final(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.is_sink(self.current_g_id)
        else:
            return self.has_player_won(PLAYER_WHITE) or \
                   self.has_player_won(PLAYER_BLACK)

    def has_player_won(self, player):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_sink_color(self.current_g_id) == player
        else:
            sum_checker_pos = sum(self.pos[player])
            return sum_checker_pos == self.action_object.get_num_checkers() * self.board_off

    @classmethod
    def generate_graph(cls, exp_params):
        print 'Generating graph...'
        if exp_params.is_graph_based():
            print 'Cannot generate graph in a graph-based experiment!'
            return None

        s = exp_params.state_class(exp_params, PLAYER_WHITE)
        g = StateGraph(s.die_object.get_all_sides(), 1,
                       s.action_object.get_all_actions())
        s_key = s.board_config()
        # s_pos = [[s.pos[0][0], s.pos[0][1]],
        #          [s.pos[1][0], s.pos[1][1]]]

        # Weird semantics!
        # What the init_pos() method does has nothing to do with s.
        s_pos = s.init_pos()
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
            if len(is_state_processed) % GENERATE_GRAPH_REPORT_EVERY_N_STATES == 0:
                print ('Fully processed %d nodes, %d in queue, processing %s...' %
                       (len(is_state_processed), Q.qsize(), s_key))
            s.pos = s_pos
            s.player_to_move = s_color
            s_id = g.get_node_id(s_key)
            for roll in s.die_object.get_all_sides():
                s.roll = roll
                must_consider_forfeit = True
                for action in s.action_object.get_all_actions():
                    if (action != s.action_object.action_forfeit_move or
                            must_consider_forfeit):
                        sp = s.get_move_outcome(action)
                        if sp is not None:
                            must_consider_forfeit = False
                            sp_key = sp.board_config()
                            if sp_key in is_state_processed:
                                sp_id = g.get_node_id(sp_key)
                                g.add_edge(s_id, roll, action, sp_id)
                            else:
                                # sp_pos = [[sp.pos[0][0], sp.pos[0][1]],
                                #           [sp.pos[1][0], sp.pos[1][1]]]
                                sp_pos = sp.init_pos()
                                sp.copy_pos(sp_pos, sp.pos)
                                sp_color = sp.player_to_move
                                sp_id = g.add_node(sp_key, sp_color)
                                g.set_attr(sp_id, POS_ATTR, sp_pos)
                                g.add_edge(s_id, roll, action, sp_id)
                                if sp.is_final():
                                    g.set_as_sink(sp_id, other_player(sp.player_to_move))
                                if sp_key not in is_state_queued:
                                    Q.put((sp_key, sp_pos, sp_color))
                                    is_state_queued[sp_key] = True
        return g

    # @classmethod
    # def copy_state_values_to_graph(cls, exp_params, agent_sarsa):
    #     cls.GAME_GRAPH.transfer_state_values(agent_sarsa)
    #     new_graph_filename = exp_params.get_graph_filename() + '-' + VAL_ATTR
    #     cls.GAME_GRAPH.save_to_file(new_graph_filename)

    def compute_per_ply_stats(self, current_ply_number):
        if COLLECT_STATS:
            state = self.board_config()
            if state in self.states_visit_count:
                self.states_visit_count[state] += 1
            else:
                self.states_visit_count[state] = 1

            if state in self.states_visit_history:
                self.states_visit_history[state].append(current_ply_number)
            else:
                self.states_visit_history[state] = [current_ply_number]

    def compute_per_game_stats(self, game_number):  # pylint: disable=unused-argument
        if COLLECT_STATS:
            self.games_discovered_states_count.append(len(self.states_visit_count))

    @classmethod
    def compute_overall_stats(cls, avg_num_plies_per_game):
        if COLLECT_STATS:
            # compute number of states discovered per game normalized by average game lengths
            for game_number in range(len(cls.games_discovered_states_count)):
                game_discovered_states_count = cls.games_discovered_states_count[game_number]
                game_discovered_states_count_over_avg_num_plies = (
                    float(game_discovered_states_count) / avg_num_plies_per_game)
                cls.games_discovered_states_count_over_avg_num_plies.append(
                    game_discovered_states_count_over_avg_num_plies)

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
            for state, _ in sorted(cls.states_visit_first_ply_num.iteritems(),
                                   key=lambda (k, v): (v, k)):
                state_visit_count = cls.states_visit_count[state]
                cls.states_sorted_by_ply_visit_count.append(state_visit_count)
                state_visit_count_over_avg_num_plies = (
                    float(state_visit_count) / avg_num_plies_per_game)
                cls.states_sorted_by_ply_visit_count_over_avg_num_plies.append(
                    state_visit_count_over_avg_num_plies)

    @classmethod
    def interesting_states(cls):
        """Return states to track values for."""
        return None

    def print_state(self):
        # print '#   0      1   2   3   4   5   6   7   8      9  '
        # print '# +---+  +---+---+---+---+---+---+---+---+  +---+'
        # print '# %s' % self.human_readable_board_config()
        # print '# +---+  +---+---+---+---+---+---+---+---+  +---+'
        # print '#                                                '

        line1_middle = ' '.join([str(i).center(3) for i in range(1, self.board_off)])
        line1 = '#   0     ' + line1_middle + '    ' + str(self.board_off).center(3) + ' '
        line2 = '# +---+  +' + '---+' * self.board_size + '  +---+'

        print line1
        print line2
        print '# %s  (%s)' % (self.human_readable_board_config(), self.board_config())
        print line2
        print '# '

    def human_readable_board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)[2:]
        cell_content = [''] * (self.board_off + 1)
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in self.action_object.get_all_checkers():
                pos = self.pos[player][checker]
                if player == PLAYER_BLACK:
                    pos = self.flip_pos(pos)
                letter = PLAYER_NAME[player].lower()[0]
                cell_content[pos] += letter

        for pos in range(self.board_off + 1):
            if cell_content[pos] == 'ww':
                cell_content[pos] = cell_content[pos].ljust(3)
            elif cell_content[pos] == 'bb':
                cell_content[pos] = cell_content[pos].rjust(3)
            else:
                cell_content[pos] = cell_content[pos].center(3)

        middle = '|'.join([cell_content[i] for i in range(1, self.board_off)])
        encoding = '|%s|  |%s|  |%s|' % (cell_content[0], middle, cell_content[self.board_off])
        return encoding

    def __repr__(self):
        return self.human_readable_board_config()

    def __str__(self):
        return self.board_config_and_roll()


class MiniGammonState(State):

    # New version:
    #        -->                           <--
    #   0      1   2   3   4   5   6   7   8      9
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    # |   |  |ww |   |   |   |   |   |   | bb|  |   |
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    #  Bar                                       Off
    #

    DOMAIN_NAME = 'minigammon'

    BOARD_SIZE = 6
    NUM_CHECKERS = 2
    NUM_DIE_SIDES = 2
    NUM_HIDDEN_UNITS = 20

    def __init__(self, exp_params, player_to_move):
        super(MiniGammonState, self).__init__(exp_params, self.BOARD_SIZE,
                                              self.NUM_DIE_SIDES,
                                              self.NUM_CHECKERS,
                                              player_to_move)

    def init_pos(self):
        return [[self.board_start, self.board_start],
                [self.board_start, self.board_start]]

    def copy_pos(self, target_pos, source_pos):
        target_pos[0][0] = source_pos[0][0]
        target_pos[0][1] = source_pos[0][1]
        target_pos[1][0] = source_pos[1][0]
        target_pos[1][1] = source_pos[1][1]

    def move(self, checker):
        success = False
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if checker == self.action_object.action_forfeit_move and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id,
                                            other_player(self.player_to_move))
                print ('Encountered unexplored graph node: %s' %
                       self.GAME_GRAPH.get_node_name(self.current_g_id))
                print 'Marking as final.'
        else:
            if checker == self.action_object.action_forfeit_move:
                success = self.can_forfeit_move()
            else:
                player = self.player_to_move
                checker_pos = self.pos[player][checker]
                other_checker = self.action_object.next_checker(checker)
                other_checker_pos = self.pos[player][other_checker]
                opponent = other_player(player)
                opponent_actual_checker_pos = [self.board_off - x
                                               for x in self.pos[opponent]]

                checker_target = checker_pos + self.roll

                # if playing checker from bar, select entry position based on p
                if checker_pos == self.board_bar:
                    offset = self.board_reentry_pos1
                    r = random.random()
                    if r >= self.exp_params.p:
                        offset = self.board_reentry_pos2
                    checker_target += offset

                # if playing a 2 from the last point
                if checker_target > self.board_off:
                    checker_target = self.board_off

                # if both checkers from opponent sit together
                # opponent_has_block = (
                #    (opponent_actual_checker1_pos == opponent_actual_checker2_pos) and
                #    (opponent_actual_checker1_pos != self.board_off))

                hitting_opponent = (checker_target != self.board_off and
                                    opponent_actual_checker_pos.count(checker_target) == 1)

                # illegal move conditions
                moving_checker_while_other_is_on_bar = (
                    checker_pos != self.board_bar and other_checker_pos == self.board_bar)
                moving_bourne_off_checker = (checker_pos == self.board_off)
                premature_bear_off = (checker_target > self.board_end and
                                      other_checker_pos <= self.board_mid)
                hitting_opponent_in_block = (
                    checker_target != self.board_off and
                    opponent_actual_checker_pos.count(checker_target) > 1)

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
                        hit_checker = opponent_actual_checker_pos.index(checker_target)
                        self.pos[opponent][hit_checker] = self.board_bar
                    self.fix_checker_orders()

        if success:
            self.switch_turn()
        return success

    @classmethod
    def interesting_states(cls):
        """Return states to track values for."""
        # Comments show true opt val for white (ignoring roll, chooseroll=0.0)
        # return ['b-7989-1-0',  # 0.00
        #         'b-1119-1-0',  # 0.22
        #         'w-1111-1-0',  # 0.50
        #         'b-4918-1-0',  # 0.87
        #         'w-8979-1-0',  # 1.00
        #        ]
        return ['b-4656-1-0',
                'b-1116-1-0',
                'w-1111-1-0',
                'b-1615-1-0',
                'w-5646-1-0',
               ]

    @classmethod
    def get_network_inputdim(cls):
        # pylint: disable=line-too-long
        return (cls.BOARD_SIZE + 2) * (cls.NUM_CHECKERS * 2) + cls.NUM_DIE_SIDES + cls.NUM_CHECKERS + 1 + 2
        # pylint: disable=line-too-long
        #     |bar| |.|...|.| |off| x |1w|2w|1b|2b|            roll                actions (+forfeit)     whose turn
        # pylint: enable=line-too-long

    @classmethod
    def get_network_hiddendim(cls):
        return cls.NUM_HIDDEN_UNITS

    def encode_network_input(self, action):
        # import pdb; pdb.set_trace()
        inputdim = self.get_network_inputdim()
        network_in = [0] * inputdim
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in self.action_object.get_all_checkers():
                pos = self.pos[player][checker]
                offset = pos * 4 + player * 2
                # Seeing a second checker on the same point?
                if network_in[offset] == 1:
                    # network_in[offset] = 0
                    network_in[offset + 1] = 1
                else:
                    network_in[offset] = 1
        roll_offset = (self.BOARD_SIZE + 2) * (self.NUM_CHECKERS * 2)
        network_in[roll_offset + self.roll - 1] = 1  # roll starts at 1
        action_offset = roll_offset + self.NUM_DIE_SIDES
        network_in[action_offset + action] = 1
        turn_offset = action_offset + self.NUM_CHECKERS + 1
        assert turn_offset == inputdim - 2
        network_in[turn_offset + self.player_to_move] = 1
        return network_in

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%s-%d%d%d%d' % (PLAYER_NAME_SHORT[self.player_to_move],
                                    self.pos[0][0], self.pos[0][1],
                                    self.pos[1][0], self.pos[1][1])

    def board_config_and_roll(self):
        return '%s-%d' % (self.board_config(), self.roll)


class NannonState(State):

    # -->                                 <--
    #   0      1   2   3   4   5   6      7
    # +---+  +---+---+---+---+---+---+  +---+
    # | w |  | w | w |   |   | b | b |  | b |
    # +---+  +---+---+---+---+---+---+  +---+
    #  Bar                               Off
    #

    DOMAIN_NAME = 'nannon'

    BOARD_SIZE = 6
    NUM_CHECKERS = 3
    NUM_DIE_SIDES = 6
    NUM_HIDDEN_UNITS = 10

    def __init__(self, exp_params, player_to_move):
        super(NannonState, self).__init__(exp_params, self.BOARD_SIZE,
                                          self.NUM_DIE_SIDES, self.NUM_CHECKERS,
                                          player_to_move)

    def init_pos(self):
        return [[0, 1, 2],
                [0, 1, 2]]

    def copy_pos(self, target_pos, source_pos):
        target_pos[0][0] = source_pos[0][0]
        target_pos[0][1] = source_pos[0][1]
        target_pos[0][2] = source_pos[0][2]
        target_pos[1][0] = source_pos[1][0]
        target_pos[1][1] = source_pos[1][1]
        target_pos[1][2] = source_pos[1][2]

    def move(self, checker):
        success = False
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if checker == self.action_object.action_forfeit_move and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id,
                                            other_player(self.player_to_move))
                print ('Encountered unexplored graph node: %s' %
                       self.GAME_GRAPH.get_node_name(self.current_g_id))
                print 'Marking as final.'
        else:
            if checker == self.action_object.action_forfeit_move:
                success = self.can_forfeit_move()
            else:
                player = self.player_to_move
                (checker1, checker2, checker3) = self.action_object.get_all_checkers()
                checker_pos = self.pos[player][checker]
                other_checker1 = self.action_object.next_checker(checker)
                other_checker1_pos = self.pos[player][other_checker1]
                other_checker2 = self.action_object.next_checker(other_checker1)
                other_checker2_pos = self.pos[player][other_checker2]
                opponent = other_player(player)
                opponent_actual_checker1_pos = self.flip_pos(self.pos[opponent][checker1])
                opponent_actual_checker2_pos = self.flip_pos(self.pos[opponent][checker2])
                opponent_actual_checker3_pos = self.flip_pos(self.pos[opponent][checker3])

                checker_target = checker_pos + self.roll

                # if playing checker from bar, select entry position based on p
                if checker_pos == self.board_bar:
                    offset = self.board_reentry_pos1
                    r = random.random()
                    if r >= self.exp_params.p:
                        offset = self.board_reentry_pos2
                    checker_target += offset

                # truncate bear off moves
                if checker_target > self.board_off:
                    checker_target = self.board_off

                hitting_opponent = (checker_target < self.board_off) and \
                                   ((checker_target == opponent_actual_checker1_pos) or
                                    (checker_target == opponent_actual_checker2_pos) or
                                    (checker_target == opponent_actual_checker3_pos))

                # illegal move conditions
                moving_bourne_off_checker = (checker_pos == self.board_off)
                has_self_checker_in_target = (checker_target < self.board_off) and \
                                             ((checker_target == other_checker1_pos) or
                                              (checker_target == other_checker2_pos))
                hitting_opponent_in_block = False
                if hitting_opponent:
                    hitting_opponent_in_block = \
                        ((self.board_bar < opponent_actual_checker1_pos < self.board_off) and
                         (abs(checker_target - opponent_actual_checker1_pos) == 1)) or \
                        ((self.board_bar < opponent_actual_checker2_pos < self.board_off) and
                         (abs(checker_target - opponent_actual_checker2_pos) == 1)) or \
                        ((self.board_bar < opponent_actual_checker3_pos < self.board_off) and
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
                            self.pos[opponent][checker1] = self.board_bar
                        elif checker_target == opponent_actual_checker2_pos:
                            self.pos[opponent][checker2] = self.board_bar
                        elif checker_target == opponent_actual_checker3_pos:
                            self.pos[opponent][checker3] = self.board_bar
                    self.fix_checker_orders()

        if success:
            self.switch_turn()
        return success

    @classmethod
    def get_network_inputdim(cls):
        # pylint: disable=line-too-long
        return cls.BOARD_SIZE * 2 + 2 * 6                   + cls.NUM_DIE_SIDES + cls.NUM_CHECKERS + 1 + 2
        # pylint: disable=line-too-long
        # |.|.|.|.|.|.| x |1w|1b|  |bar|,|off|:0-3 checkers   roll                actions (+forfeit)     whose turn
        # pylint: enable=line-too-long

    @classmethod
    def get_network_hiddendim(cls):
        return cls.NUM_HIDDEN_UNITS

    def encode_network_input(self, action):
        inputdim = self.get_network_inputdim()
        network_in = [0] * inputdim
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in self.action_object.get_all_checkers():
                pos = self.pos[player][checker]
                if pos == self.board_bar:
                    offset = player * 3
                elif self.board_bar < pos < self.board_off:
                    offset = 6 + (pos - 1) * 2 + player
                elif pos == self.board_off:
                    offset = 6 + self.board_size * 2 + player * 3
                else:
                    print 'Invalid checker position when encoding network input!'

                # Seeing a second checker on the same point?
                while network_in[offset] == 1:
                    offset += 1
                network_in[offset] = 1
        roll_offset = self.BOARD_SIZE * 2 + 2 * 6
        network_in[roll_offset + self.roll - 1] = 1  # roll starts at 1
        action_offset = roll_offset + self.NUM_DIE_SIDES
        network_in[action_offset + action] = 1
        turn_offset = action_offset + self.NUM_CHECKERS + 1
        assert turn_offset == inputdim - 2
        network_in[turn_offset + self.player_to_move] = 1
        return network_in

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%s-%d%d%d-%d%d%d' % (
                PLAYER_NAME_SHORT[self.player_to_move],
                self.pos[0][0], self.pos[0][1], self.pos[0][2],
                self.pos[1][0], self.pos[1][1], self.pos[1][2])

    def board_config_and_roll(self):
        return '%s-%d' % (self.board_config(), self.roll)


class MidGammonState(State):

    #        -->                           <--
    #   0      1   2   3   4   5   6   7   8      9
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    # |   |  |ww |ww |   |   |   |   | bb| bb|  |   |
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    #  Bar                                       Off
    #

    DOMAIN_NAME = 'midgammon'

    BOARD_SIZE = 6
    NUM_CHECKERS = 4
    NUM_DIE_SIDES = 3
    NUM_HIDDEN_UNITS = 20

    def __init__(self, exp_params, player_to_move):
        super(MidGammonState, self).__init__(exp_params, self.BOARD_SIZE,
                                             self.NUM_DIE_SIDES,
                                             self.NUM_CHECKERS,
                                             player_to_move)

    def init_pos(self):
        start2 = self.board_start + 1
        return [[self.board_start, self.board_start, start2, start2],
                [self.board_start, self.board_start, start2, start2]]

    def copy_pos(self, target_pos, source_pos):
        target_pos[0][0] = source_pos[0][0]
        target_pos[0][1] = source_pos[0][1]
        target_pos[0][2] = source_pos[0][2]
        target_pos[0][3] = source_pos[0][3]
        target_pos[1][0] = source_pos[1][0]
        target_pos[1][1] = source_pos[1][1]
        target_pos[1][2] = source_pos[1][2]
        target_pos[1][3] = source_pos[1][3]

    def move(self, checker):
        success = False
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if checker == self.action_object.action_forfeit_move and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id,
                                            other_player(self.player_to_move))
                print ('Encountered unexplored graph node: %s' %
                       self.GAME_GRAPH.get_node_name(self.current_g_id))
                print 'Marking as final.'
        else:
            if checker == self.action_object.action_forfeit_move:
                success = self.can_forfeit_move()
            else:
                player = self.player_to_move
                checker_pos = self.pos[player][checker]
#                other_checker = MidGammonAction.next_checker(checker)
#                other_checker_pos = self.pos[player][other_checker]
                opponent = other_player(player)
#                opponent_actual_checker1_pos = self.flip_pos(self.pos[opponent][self.CHECKER1])
#                opponent_actual_checker2_pos = self.flip_pos(self.pos[opponent][self.CHECKER2])
                opponent_actual_checker_pos = [self.board_off - x
                                               for x in self.pos[opponent]]

                checker_target = checker_pos + self.roll

                # if playing checker from bar, select entry position based on p
                if checker_pos == self.board_bar:
                    offset = self.board_reentry_pos1
                    r = random.random()
                    if r >= self.exp_params.p:
                        offset = self.board_reentry_pos2
                    checker_target += offset

                # if playing a 2 from the last point
                if checker_target > self.board_off:
                    checker_target = self.board_off

                # if both checkers from opponent sit together
                # opponent_has_block = (
                #     opponent_actual_checker1_pos == opponent_actual_checker2_pos and
                #     opponent_actual_checker1_pos != self.board_off)
                #
                # hitting_opponent = (opponent_actual_checker1_pos == checker_target) or \
                #                    (opponent_actual_checker2_pos == checker_target)
                hitting_opponent = (checker_target != self.board_off and
                                    opponent_actual_checker_pos.count(checker_target) == 1)

                # illegal move conditions
                moving_checker_while_other_is_on_bar = (
                    checker_pos != self.board_bar and
                    self.pos[player].count(self.board_bar) > 0)
                moving_bourne_off_checker = (checker_pos == self.board_off)
                premature_bear_off = (checker_target > self.board_end and
                                      min(self.pos[player]) <= self.board_mid)
                hitting_opponent_in_block = (
                    checker_target != self.board_off and
                    opponent_actual_checker_pos.count(checker_target) > 1)

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
                        hit_checker = opponent_actual_checker_pos.index(checker_target)
                        self.pos[opponent][hit_checker] = self.board_bar
                    self.fix_checker_orders()

        if success:
            self.switch_turn()
        return success

    @classmethod
    def get_network_inputdim(cls):
        # pylint: disable=line-too-long
        return (cls.BOARD_SIZE + 2) * (cls.NUM_CHECKERS * 2) + cls.NUM_DIE_SIDES + cls.NUM_CHECKERS + 1 + 2
        # pylint: disable=line-too-long
        #     |bar| |.|...|.| |off| x |1w|2w|1b|2b|            roll                actions (+forfeit)     whose turn
        # pylint: enable=line-too-long

    @classmethod
    def get_network_hiddendim(cls):
        return cls.NUM_HIDDEN_UNITS

    def encode_network_input(self, action):
        inputdim = self.get_network_inputdim()
        network_in = [0] * inputdim
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in self.action_object.get_all_checkers():
                pos = self.pos[player][checker]
                offset = pos * 8 + player * 4
                # Seeing a second checker on the same point?
                while network_in[offset] == 1:
                    offset += 1
                network_in[offset] = 1
        roll_offset = (self.BOARD_SIZE + 2) * (self.NUM_CHECKERS * 2)
        network_in[roll_offset + self.roll - 1] = 1  # roll starts at 1
        action_offset = roll_offset + self.NUM_DIE_SIDES
        network_in[action_offset + action] = 1
        turn_offset = action_offset + self.NUM_CHECKERS + 1
        assert turn_offset == inputdim - 2
        network_in[turn_offset + self.player_to_move] = 1
        return network_in

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%s-%d%d%d%d%d%d%d%d' % (
                PLAYER_NAME_SHORT[self.player_to_move],
                self.pos[0][0], self.pos[0][1], self.pos[0][2], self.pos[0][3],
                self.pos[1][0], self.pos[1][1], self.pos[1][2], self.pos[1][3])

    def board_config_and_roll(self):
        return '%s-%d' % (self.board_config(), self.roll)


class NohitGammonState(State):

    #        -->                           <--
    #   0      1   2   3   4   5   6   7   8      9
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    # |   |  |ww |ww |   |   |   |   | bb| bb|  |   |
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    #  Bar                                       Off
    #

    DOMAIN_NAME = 'nohitgammon'

    BOARD_SIZE = 8
    NUM_CHECKERS = 4
    NUM_DIE_SIDES = 3
    NUM_HIDDEN_UNITS = 20

    def __init__(self, exp_params, player_to_move):
        super(NohitGammonState, self).__init__(exp_params, self.BOARD_SIZE,
                                               self.NUM_DIE_SIDES,
                                               self.NUM_CHECKERS,
                                               player_to_move)

    def init_pos(self):
        start2 = self.board_start + 1
        return [[self.board_start, self.board_start, start2, start2],
                [self.board_start, self.board_start, start2, start2]]

    def copy_pos(self, target_pos, source_pos):
        target_pos[0][0] = source_pos[0][0]
        target_pos[0][1] = source_pos[0][1]
        target_pos[0][2] = source_pos[0][2]
        target_pos[0][3] = source_pos[0][3]
        target_pos[1][0] = source_pos[1][0]
        target_pos[1][1] = source_pos[1][1]
        target_pos[1][2] = source_pos[1][2]
        target_pos[1][3] = source_pos[1][3]

    def move(self, checker):
        success = False
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if checker == self.action_object.action_forfeit_move and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id,
                                            other_player(self.player_to_move))
                print ('Encountered unexplored graph node: %s' %
                       self.GAME_GRAPH.get_node_name(self.current_g_id))
                print 'Marking as final.'
        else:
            if checker == self.action_object.action_forfeit_move:
                success = self.can_forfeit_move()
            else:
                player = self.player_to_move
                checker_pos = self.pos[player][checker]
                opponent = other_player(player)
                opponent_actual_checker_pos = [self.board_off - x
                                               for x in self.pos[opponent]]

                checker_target = checker_pos + self.roll

                # if playing checker from bar, select entry position based on p
                if checker_pos == self.board_bar:
                    offset = self.board_reentry_pos1
                    r = random.random()
                    if r >= self.exp_params.p:
                        offset = self.board_reentry_pos2
                    checker_target += offset

                # if playing a 2 from the last point
                if checker_target > self.board_off:
                    checker_target = self.board_off

                # if both checkers from opponent sit together
                # opponent_has_block = (
                #     opponent_actual_checker1_pos == opponent_actual_checker2_pos and
                #     opponent_actual_checker1_pos != self.BOARD_OFF)
                #
                # hitting_opponent = (opponent_actual_checker1_pos == checker_target) or \
                #                    (opponent_actual_checker2_pos == checker_target)
                hitting_opponent = (checker_target != self.board_off and
                                    opponent_actual_checker_pos.count(checker_target) >= 1)

                # illegal move conditions
                moving_bourne_off_checker = (checker_pos == self.board_off)
                premature_bear_off = (
                    checker_target > self.board_end and
                    min(self.pos[player]) <= self.board_mid)

                is_illegal_move = (moving_bourne_off_checker or
                                   premature_bear_off or
                                   hitting_opponent)

                if not is_illegal_move:
                    success = True
                    # move checker
                    self.pos[player][checker] = checker_target
                    # hit if checker from opponent is there
                    self.fix_checker_orders()

        if success:
            self.switch_turn()
        return success

    @classmethod
    def get_network_inputdim(cls):
        # pylint: disable=line-too-long
        return (cls.BOARD_SIZE + 2) * (cls.NUM_CHECKERS * 2) + cls.NUM_DIE_SIDES + cls.NUM_CHECKERS + 1 + 2
        # pylint: disable=line-too-long
        #     |bar| |.|...|.| |off| x |1w|2w|1b|2b|            roll                actions (+forfeit)     whose turn
        # pylint: enable=line-too-long

    @classmethod
    def get_network_hiddendim(cls):
        return cls.NUM_HIDDEN_UNITS

    def encode_network_input(self, action):
        inputdim = self.get_network_inputdim()
        network_in = [0] * inputdim
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in self.action_object.get_all_checkers():
                pos = self.pos[player][checker]
                offset = pos * 8 + player * 4
                # Seeing a second checker on the same point?
                while network_in[offset] == 1:
                    offset += 1
                network_in[offset] = 1
        roll_offset = (self.BOARD_SIZE + 2) * (self.NUM_CHECKERS * 2)
        network_in[roll_offset + self.roll - 1] = 1  # roll starts at 1
        action_offset = roll_offset + self.NUM_DIE_SIDES
        network_in[action_offset + action] = 1
        turn_offset = action_offset + self.NUM_CHECKERS + 1
        assert turn_offset == inputdim - 2
        network_in[turn_offset + self.player_to_move] = 1
        return network_in

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%s-%d%d%d%d%d%d%d%d' % (
                PLAYER_NAME_SHORT[self.player_to_move],
                self.pos[0][0], self.pos[0][1], self.pos[0][2], self.pos[0][3],
                self.pos[1][0], self.pos[1][1], self.pos[1][2], self.pos[1][3])

    def board_config_and_roll(self):
        return '%s-%d' % (self.board_config(), self.roll)


class TwoDiceMiniState(State):

    #        -->                           <--
    #   0      1   2   3   4   5   6   7   8      9
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    # |   |  |ww |ww |   |   |   |   | bb| bb|  |   |
    # +---+  +---+---+---+---+---+---+---+---+  +---+
    #  Bar                                       Off
    #

    DOMAIN_NAME = 'twodicemini'

    REAL_NUM_CHECKERS = 4
    REAL_NUM_DICE_SIDES = 2

    BOARD_SIZE = 7
    # Picking 2 of the n checkers to move is simulated by picking 1 of n^2 virtual checkers.
    NUM_CHECKERS = REAL_NUM_CHECKERS * REAL_NUM_CHECKERS
    # Rolling 2 dice each with s sides is simulated by a virtual die with s^2 sides.
    NUM_DIE_SIDES = REAL_NUM_DICE_SIDES * REAL_NUM_DICE_SIDES
    NUM_HIDDEN_UNITS = 10

    def __init__(self, exp_params, player_to_move):
        super(TwoDiceMiniState, self).__init__(exp_params, self.BOARD_SIZE,
                                               self.NUM_DIE_SIDES,
                                               self.NUM_CHECKERS,
                                               player_to_move)

    def init_pos(self):
        start2 = self.board_start + 1
        return [[self.board_start, self.board_start, start2, start2],
                [self.board_start, self.board_start, start2, start2]]

    def copy_pos(self, target_pos, source_pos):
        target_pos[0][0] = source_pos[0][0]
        target_pos[0][1] = source_pos[0][1]
        target_pos[0][2] = source_pos[0][2]
        target_pos[0][3] = source_pos[0][3]
        target_pos[1][0] = source_pos[1][0]
        target_pos[1][1] = source_pos[1][1]
        target_pos[1][2] = source_pos[1][2]
        target_pos[1][3] = source_pos[1][3]

    def has_player_won(self, player):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_sink_color(self.current_g_id) == player
        else:
            sum_checker_pos = sum(self.pos[player])
            return (sum_checker_pos == self.action_object.get_num_checkers() /
                    self.REAL_NUM_CHECKERS * self.board_off)

    def move(self, checker):
        success = False
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if (checker == self.action_object.action_forfeit_move and
                    not success):
                self.GAME_GRAPH.set_as_sink(self.current_g_id,
                                            other_player(self.player_to_move))
                print ('Encountered unexplored graph node: %s' %
                       self.GAME_GRAPH.get_node_name(self.current_g_id))
                print 'Marking as final.'
        else:
            if checker == self.action_object.action_forfeit_move:
                success = self.can_forfeit_move()
            else:
                player = self.player_to_move
                opponent = other_player(player)
                opponent_actual_checker_pos = [self.board_off - x
                                               for x in self.pos[opponent]]

                roll1 = int((self.roll - 1) / self.REAL_NUM_DICE_SIDES) + 1
                roll2 = ((self.roll - 1) % self.REAL_NUM_DICE_SIDES) + 1
                checker1 = int(checker / self.REAL_NUM_CHECKERS)
                checker2 = checker % self.REAL_NUM_CHECKERS

                checker1_pos = self.pos[player][checker1]
                checker1_target = checker1_pos + roll1

                # if playing checker from bar, select entry position based on p
                if checker1_pos == self.board_bar:
                    offset = self.board_reentry_pos1
                    r = random.random()
                    if r >= self.exp_params.p:
                        offset = self.board_reentry_pos2
                    checker1_target += offset

                # if playing a 2 from the last point
                if checker1_target > self.board_off:
                    checker1_target = self.board_off

                hitting_opponent = (
                    checker1_target != self.board_off and
                    opponent_actual_checker_pos.count(checker1_target) == 1)

                # illegal move conditions
                moving_checker_while_other_is_on_bar = (
                    checker1_pos != self.board_bar and
                    self.pos[player].count(self.board_bar) > 0)
                moving_bourne_off_checker = (checker1_pos == self.board_off)
                premature_bear_off = (
                    checker1_target > self.board_end and
                    min(self.pos[player]) <= self.board_mid)
                hitting_opponent_in_block = (
                    checker1_target != self.board_off and
                    opponent_actual_checker_pos.count(checker1_target) > 1)

                is_illegal_move = (moving_checker_while_other_is_on_bar or
                                   moving_bourne_off_checker or
                                   premature_bear_off or
                                   hitting_opponent_in_block)

                if not is_illegal_move:
                    # move checker
                    checker1_prev_pos = self.pos[player][checker1]
                    self.pos[player][checker1] = checker1_target
                    # hit if checker from opponent is there
                    hit_checker1 = None
                    if hitting_opponent:
                        hit_checker1 = opponent_actual_checker_pos.index(checker1_target)
                        hit_checker1_prev_pos = self.pos[opponent][hit_checker1]
                        self.pos[opponent][hit_checker1] = self.board_bar

                    checker2_pos = self.pos[player][checker2]
                    checker2_target = checker2_pos + roll2

                    # if playing checker from bar, select entry position based on p
                    if checker2_pos == self.board_bar:
                        offset = self.board_reentry_pos1
                        r = random.random()
                        if r >= self.exp_params.p:
                            offset = self.board_reentry_pos2
                        checker2_target += offset

                    # if playing a 2 from the last point
                    if checker2_target > self.board_off:
                        checker2_target = self.board_off

                    hitting_opponent = (
                        checker2_target != self.board_off and
                        opponent_actual_checker_pos.count(checker2_target) == 1)

                    # illegal move conditions
                    moving_checker_while_other_is_on_bar = (
                        checker2_pos != self.board_bar and
                        self.pos[player].count(self.board_bar) > 0)
                    # if the player is winning, we allow him to spend his
                    # second move on moving a bourne off checker
                    moving_bourne_off_checker = (
                        checker2_pos == self.board_off and
                        not self.has_player_won(player))
                    premature_bear_off = (
                        checker2_target > self.board_end and
                        min(self.pos[player]) <= self.board_mid)
                    hitting_opponent_in_block = (
                        checker2_target != self.board_off and
                        opponent_actual_checker_pos.count(checker2_target) > 1)

                    is_illegal_move = (moving_checker_while_other_is_on_bar or
                                       moving_bourne_off_checker or
                                       premature_bear_off or
                                       hitting_opponent_in_block)

                    if not is_illegal_move:
                        success = True
                        # move checker
                        self.pos[player][checker2] = checker2_target
                        # hit if checker from opponent is there
                        if hitting_opponent:
                            hit_checker2 = opponent_actual_checker_pos.index(checker2_target)
                            self.pos[opponent][hit_checker2] = self.board_bar

                        self.fix_checker_orders()
                    else:
                        self.pos[player][checker1] = checker1_prev_pos
                        if hit_checker1 is not None:
                            self.pos[opponent][hit_checker1] = hit_checker1_prev_pos

        if success:
            self.switch_turn()
        return success

    @classmethod
    def get_network_inputdim(cls):
        # pylint: disable=line-too-long
        return (cls.BOARD_SIZE + 2) * (cls.REAL_NUM_CHECKERS * 2) + cls.NUM_DIE_SIDES + cls.NUM_CHECKERS + 1 + 2
        # pylint: disable=line-too-long
        #     |bar| |.|...|.| |off| x |1-4w|1-4b|                   roll                actions (+forfeit)     whose turn
        # pylint: enable=line-too-long

    @classmethod
    def get_network_hiddendim(cls):
        return cls.NUM_HIDDEN_UNITS

    def encode_network_input(self, action):
        inputdim = self.get_network_inputdim()
        network_in = [0] * inputdim
        for player in [PLAYER_WHITE, PLAYER_BLACK]:
            for checker in range(self.REAL_NUM_CHECKERS):
                pos = self.pos[player][checker]
                offset = pos * 8 + player * 4
                # Seeing a second checker on the same point?
                while network_in[offset] == 1:
                    offset += 1
                network_in[offset] = 1
        roll_offset = (self.BOARD_SIZE + 2) * (self.REAL_NUM_CHECKERS * 2)
        network_in[roll_offset + self.roll - 1] = 1  # roll starts at 1
        action_offset = roll_offset + self.NUM_DIE_SIDES
        network_in[action_offset + action] = 1
        turn_offset = action_offset + self.NUM_CHECKERS + 1
        assert turn_offset == inputdim - 2
        network_in[turn_offset + self.player_to_move] = 1
        return network_in

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%s-%d%d%d%d%d%d%d%d' % (
                PLAYER_NAME_SHORT[self.player_to_move],
                self.pos[0][0], self.pos[0][1], self.pos[0][2], self.pos[0][3],
                self.pos[1][0], self.pos[1][1], self.pos[1][2], self.pos[1][3])

    def board_config_and_roll(self):
        return '%s-%d' % (self.board_config(), self.roll)


class NimState(State):

    DOMAIN_NAME = 'nim'

#    NUM_HEAPS = 4
#    TAKE_MAX = 3
#    SIZE_HEAPS = [3, 4, 5, 4]
#    TOTAL_TOKENS = sum(SIZE_HEAPS)

    NUM_HEAPS = 1
    TAKE_MAX = 3
    SIZE_HEAPS = [23]
    TOTAL_TOKENS = sum(SIZE_HEAPS)

#    BOARD_SIZE   = 0
#    NUM_CHECKERS = TAKE_MAX
#    NUM_DIE_SIDES = NUM_HEAPS
#    NUM_HIDDEN_UNITS = 10

    BOARD_SIZE = 0
    NUM_CHECKERS = NUM_HEAPS
    NUM_DIE_SIDES = TAKE_MAX
    NUM_HIDDEN_UNITS = 10

    def __init__(self, exp_params, player_to_move):
        super(NimState, self).__init__(exp_params, self.BOARD_SIZE,
                                       self.NUM_DIE_SIDES, self.NUM_CHECKERS,
                                       player_to_move)

    @classmethod
    def get_domain_signature(cls):
        return super(NimState, cls).get_domain_signature() + (
            '-%s' % '-'.join(str(x) for x in cls.SIZE_HEAPS))

    def init_pos(self):
        return self.SIZE_HEAPS[:]

    def copy_pos(self, target_pos, source_pos):
        for i in range(self.NUM_HEAPS):
            target_pos[i] = source_pos[i]

    def has_player_won(self, player):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_sink_color(self.current_g_id) == player
        else:
            sum_checker_pos = sum(self.pos)
            return (sum_checker_pos == 0) and (self.player_to_move != player)

    def can_forfeit_move(self):
        return True

    def move(self, checker):
        success = False
        if self.is_graph_based:
            next_id = self.GAME_GRAPH.get_transition_outcome(self.current_g_id,
                                                             self.roll, checker)
            if next_id is not None:
                self.current_g_id = next_id
                self.pos = self.GAME_GRAPH.get_attr(next_id, POS_ATTR)
                success = True
            if checker == self.action_object.action_forfeit_move and not success:
                self.GAME_GRAPH.set_as_sink(self.current_g_id,
                                            other_player(self.player_to_move))
                print ('Encountered unexplored graph node: %s' %
                       self.GAME_GRAPH.get_node_name(self.current_g_id))
                print 'Marking as final.'
        else:
            if checker == self.action_object.action_forfeit_move:
                success = self.can_forfeit_move()
            else:
                # action = self.roll - 1
                # which_heap = int(action / self.TAKE_MAX)
                # how_many = (action % self.TAKE_MAX) + 1

                # which_heap = self.roll - 1
                # how_many = checker + 1

                # which_heap = checker
                # how_many = self.roll

                # action = checker
                # which_heap = int(action / self.TAKE_MAX)
                # how_many = (action % self.TAKE_MAX) + 1

                # # Dice roll determines which heap to take from.
                # which_heap = self.roll - 1
                # how_many = checker + 1

                # Dice roll determines how many to take.
                which_heap = checker
                how_many = self.roll

                if self.pos[which_heap] >= how_many:
                    success = True
                    # move checker
                    self.pos[which_heap] -= how_many

        if success:
            self.switch_turn()
        return success

    @classmethod
    def interesting_states(cls):
        """Return states to track values for."""
        return ['w-14-1-0', 'w-14-2-0', 'w-14-3-0',
                'w-11-1-0', 'w-11-2-0', 'w-11-3-0',
                'b-11-1-0', 'b-11-2-0', 'b-11-3-0',
                'w-8-1-0', 'w-8-2-0', 'w-8-3-0',
                'b-8-1-0', 'b-8-2-0', 'b-8-3-0',
                'w-5-1-0', 'w-5-2-0', 'w-5-3-0',
                'b-5-1-0', 'b-5-2-0', 'b-5-3-0',
                'w-3-3-0', 'w-3-2-0', 'w-3-1-0',
                'b-3-3-0', 'b-3-2-0', 'b-3-1-0',
                'w-2-2-0', 'w-2-1-0']

    @classmethod
    def get_network_inputdim(cls):
        return cls.TOTAL_TOKENS + cls.NUM_DIE_SIDES + cls.NUM_CHECKERS + 1 + 2
        #      how many left      roll                actions (+forfeit)     whose turn

    @classmethod
    def get_network_hiddendim(cls):
        return cls.NUM_HIDDEN_UNITS

    def encode_network_input(self, action):
        # import pdb; pdb.set_trace()
        inputdim = self.get_network_inputdim()
        network_in = [0] * inputdim
        offset = 0
        for heap in range(self.NUM_HEAPS):
            tokens_in_heap = self.pos[heap]
#            if tokens_in_heap > 0:
            network_in[offset + tokens_in_heap] = 1
            offset += self.SIZE_HEAPS[heap] + 1
        roll_offset = self.TOTAL_TOKENS
        network_in[roll_offset + self.roll - 1] = 1  # roll starts at 1
        action_offset = roll_offset + self.NUM_DIE_SIDES
        network_in[action_offset + action] = 1
        turn_offset = action_offset + self.NUM_CHECKERS + 1
        assert turn_offset == inputdim - 2
        network_in[turn_offset + self.player_to_move] = 1
        return network_in

    def print_state(self):
        print '# %s  (%s)' % (self.human_readable_board_config(), self.board_config())
        print '# '

    def human_readable_board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)[2:]
        return str(self.pos)

    def board_config(self):
        if self.is_graph_based:
            return self.GAME_GRAPH.get_node_name(self.current_g_id)
        else:
            return '%s-%s' % (PLAYER_NAME_SHORT[self.player_to_move],
                              ''.join([str(x) for x in self.pos]))

    def board_config_and_roll(self):
        return '%s-%d' % (self.board_config(), self.roll)


if __name__ == '__main__':
    pass
