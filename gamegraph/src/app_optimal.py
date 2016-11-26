'''
Created on Sep 20, 2012

@author: reza
'''
import random

from domain import Agent, AgentRandom, GameSet
from common import VAL_ATTR, PLAYER_BLACK, Experiment, FOLDER_DOMAINSTATS,\
    PLAYER_WHITE, ExpParams
from params import NUM_STATS_GAMES, SAVE_STATS, COLLECT_STATS

class AgentOptimal(Agent):

    def __init__(self, state_class):
        super(AgentOptimal, self).__init__(state_class)
        self.graph = None
        self.attempt_graph_init = True

    def select_action(self):
        node_label = self.state.board_config()
        node_color = self.state.player_to_move
        if self.attempt_graph_init:
            print 'AgentOptimal trying to load the game graph...'
            self.state.load_own_graph()
            self.graph = self.state.GAME_GRAPH
            node_id = self.graph.get_node_id(node_label)
            print 'Checking for value attributes...'
            if self.graph.has_attr(node_id, VAL_ATTR):
                print 'Present.'
            else:
                print 'Not present.'
                self.graph.value_iteration(self.state.exp_params)
                print 'AgentOptimal trying to save state values in graph...'
                self.graph.save(self.state.exp_params)
            self.attempt_graph_init = False

        node_id = self.graph.get_node_id(node_label)
#        multiplier = 1
#        if node_color == PLAYER_BLACK:
#            multiplier = -1

        do_choose_roll = False
#        if self.state.exp_params.choose_roll > 0.0:
#            r = random.random()
#            if r < self.state.exp_params.choose_roll:
#                do_choose_roll = True
        if self.state.stochastic_p < self.state.exp_params.choose_roll:
            do_choose_roll = True

        roll_range = [self.state.roll]
        if do_choose_roll:
            roll_range = self.state.die_object.get_all_sides()

        action_values = []

        for replace_roll in roll_range:
            self.state.roll = replace_roll
            for action in self.state.action_object.get_all_checkers():
                succ_id = self.graph.get_successor(node_id, replace_roll, action)
                if succ_id is not None:
                    succ_value = self.graph.get_attr(succ_id, VAL_ATTR)
                    action_values.append(((succ_value, random.random()), (replace_roll, action)))

        if len(action_values) > 0:
            # The game graph stores the probability of white winning for each state.
            # If AgentOptimal is to choose a move for black, it needs to pick the
            # action leading to a state with minimal value.
            # For white: Sort with reverse=True.
            # For black: Sort with reverse=False.
            reverse = node_color == PLAYER_WHITE  # Pick highest win rate for white.
            action_values_sorted = sorted(action_values, reverse=reverse)
            best_roll = action_values_sorted[0][1][0]
            # set the best roll there
            self.state.roll = best_roll
            action = action_values_sorted[0][1][1]
        else:
            action = self.state.action_object.action_forfeit_move

#            if (action != self.state.action_object.action_forfeit_move) or self.state.can_forfeit_move():
#                return action
#            else:
#                self.state.reroll_dice()

        return action


if __name__ == '__main__':
    exp_params = ExpParams.get_exp_params_from_command_line_args()

    num_games = NUM_STATS_GAMES
    agent_white = AgentOptimal(exp_params.state_class)
    agent_black = AgentRandom(exp_params.state_class)
    game_set = GameSet(exp_params, num_games, agent_white, agent_black)

    count_wins = game_set.run()
    total_plies = game_set.get_sum_count_plies()

    # printing overall stats
    print '----'
    print 'Run signature is: %s' % exp_params.signature
#    print 'P was: %.2f' % exp_params.p
#    print 'Re-entry offset was: %d' % exp_params.offset
#    print 'Graph name was: %s' % exp_params.graph_name

    if SAVE_STATS:
        # general info
#            filename = '../data/%s-%s-overall-stats.txt' % (domain.name,
#                                            cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS,
                                        'overall-stats')
        f = open(filename, 'w')

    avg_num_plies_per_game = float(total_plies) / num_games
    print 'Games won by agent: %d, opponent: %d' % (count_wins[PLAYER_WHITE],
                                                    count_wins[PLAYER_BLACK])
    print 'Average plies per game: %.2f' % avg_num_plies_per_game
    if SAVE_STATS:
        f.write('Games won by agent: %d, opponent: %d\n' % (count_wins[PLAYER_WHITE],
                                                          count_wins[PLAYER_BLACK]))
        f.write('Average plies per game: %.2f\n' % avg_num_plies_per_game)

    if COLLECT_STATS:
        total_states_visited = len(exp_params.state_class.states_visit_count)
        print 'Total number of states encountered: %d' % total_states_visited
        print 'per 1000 plies: %.2f' % (float(total_states_visited) /
                                        avg_num_plies_per_game)
        if SAVE_STATS:
            f.write('Total number of states encountered: %d\n' % total_states_visited)
            f.write('per 1000 plies: %.2f\n' % (float(total_states_visited) /
                                              avg_num_plies_per_game))

        avg_visit_count_to_states = sum(exp_params.state_class.states_visit_count.itervalues()) / float(total_states_visited)
        print 'Average number of visits to states: %.2f' % avg_visit_count_to_states
        print 'per 1000 plies: %.2f' % (float(avg_visit_count_to_states) /
                                        avg_num_plies_per_game)
        if SAVE_STATS:
            f.write('Average number of visits to states: %.2f\n' % avg_visit_count_to_states)
            f.write('per 1000 plies: %.2f\n' % (float(avg_visit_count_to_states) /
                                              avg_num_plies_per_game))

        sum_squared_diffs = sum([(e - avg_visit_count_to_states) ** 2
                                 for e in exp_params.state_class.states_visit_count.itervalues()])
        var_visit_count_to_states =  sum_squared_diffs / float(total_states_visited)
        print 'Variance of number of visits to states: %.2f' % var_visit_count_to_states
        if SAVE_STATS:
            f.write('Variance of number of visits to states: %.2f\n' % var_visit_count_to_states)

        exp_params.state_class.compute_overall_stats(avg_num_plies_per_game)
        Experiment.save_stats(exp_params.state_class, exp_params)

    if SAVE_STATS:
        f.close()

