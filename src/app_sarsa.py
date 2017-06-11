'''
Created on Dec 10, 2011

@author: reza
'''

import pickle
import random

from app_random_games import AgentRandom
from common import (FILE_PREFIX_SARSA, FOLDER_QTABLE, PLAYER_NAME_SHORT,
                    PLAYER_WHITE, REWARD_LOSE, REWARD_WIN, Agent, Experiment,
                    ExpParams, Game, GameSet, make_data_folders, other_player)
from params import (ALGO, ALGO_Q_LEARNING, ALGO_SARSA, SARSA_ALPHA,
                    SARSA_EPSILON, SARSA_GAMMA, SARSA_LAMBDA,
                    SARSA_NUM_EPISODES_PER_ITERATION, SARSA_NUM_EVAL_EPISODES,
                    SARSA_NUM_TRAINING_ITERATIONS, SARSA_OPTIMISTIC_INIT,
                    SARSA_SAVE_TABLES, SARSA_USE_ALPHA_ANNEALING, TRAIN_BUDDY,
                    TRAIN_BUDDY_COPY, TRAIN_BUDDY_RANDOM, TRAIN_BUDDY_SELF)


class AgentSarsa(Agent):

    def __init__(self, state_class, load_knowledge=False):
        super(AgentSarsa, self).__init__(state_class)
        self.algorithm = SarsaLambdaAlg(state_class)

        if load_knowledge:
            self.algorithm.load_knowledge()
            self.algorithm.is_learning = False

    def begin_episode(self):
        self.algorithm.begin_episode(self.state)

    def end_episode(self, reward):
        self.algorithm.end_episode(self.state, reward)

    def select_action(self):
        return self.algorithm.select_action(self.state)

    # Unused method.
    def get_board_value(self, board_str, all_rolls, all_actions):
        return self.algorithm.get_board_value(board_str, all_rolls, all_actions)

    def pause_learning(self):
        self.algorithm.pause_learning()

    def resume_learning(self):
        self.algorithm.resume_learning()

    # def save_learning_state(self):
    #     if self.algorithm is not None:
    #         self.algorithm.save_learning_state()
    #
    # def restore_learning_state(self):
    #     if self.algorithm is not None:
    #         self.algorithm.restore_learning_state()
    #
    # def reset_learning(self):
    #     if self.algorithm is not None:
    #         self.algorithm.reset_learning()


class SarsaLambdaAlg(object):

    def __init__(self, state_class):
        self.state_class = state_class

        self.epsilon = SARSA_EPSILON
        self.lamda = SARSA_LAMBDA
        self.alpha = SARSA_ALPHA
        self.gamma = SARSA_GAMMA

        self.state_str = None
        self.last_state_str = None
        self.last_action = None
        # Since we apply updates with one step delay, need to remember Whether
        # the action in previous time step was exploratory.
        self.was_last_action_random = False

        self.is_learning = True
        self.Q = {}
        # astar_value[s'] = argmax_b Q(s', b) for undetermined roll.
        self.astar_value = {}
        # self.Q_save = {}
        self.e = {}
        self.visit_count = {}
        self.processed_final_reward = False  # Useful with TRAIN_BUDDY_SELF.

        if SARSA_OPTIMISTIC_INIT:
            self.default_q = Game.get_max_episode_reward()  # * 1.1
        else:
            self.default_q = Game.get_min_episode_reward()

    def get_default_q(self, state_str):
        # If not training against self, initialize all state values similarly.
        if TRAIN_BUDDY != TRAIN_BUDDY_SELF:
            # Winning player will receive a 1.0 be it white or black.
            return self.default_q

        # If training against self, initialize white states to 1.0 and black
        # states to 0.0.  This amounts to an optimistic initialization for both
        # players.
        if state_str.startswith(PLAYER_NAME_SHORT[PLAYER_WHITE]):
            # If it's white's turn to move, optimistically assume the highest reward.
            return self.default_q
        else:
            # If it's black's turn to move, optimistically assume the lowest reward for white.
            return Game.get_min_episode_reward()

    def begin_episode(self, state):  # pylint: disable=unused-argument
        self.e = {}
        self.astar_value = {}
        self.state_str = None
        self.last_state_str = None
        self.last_action = None
        self.was_last_action_random = False
        self.processed_final_reward = False

    def end_episode(self, state, reward):
        if self.is_learning and not self.processed_final_reward:
            if TRAIN_BUDDY == TRAIN_BUDDY_SELF:
                # Ignore the reward parameter and construct own reward signal
                # corresponding to the probability of white winning.
                winner = other_player(state.player_to_move)
                if winner == PLAYER_WHITE:
                    reward_for_white = REWARD_WIN
                else:
                    reward_for_white = REWARD_LOSE
                # Overwriting reward.
                reward = reward_for_white

            self.sarsa_step(state, action=None, is_action_random=False,
                            reward=reward)
            self.processed_final_reward = True

    def sarsa_step(self, state, action, is_action_random, reward=0):
        """Updates the underlying model after every transition.

        self.last_state_str    ->    state    ->    next state (current state)
                        self.last_action     action

        This method is called in self.select_action() and self.end_episode().

        Args:
            state: State where the action was taken.
            action: Action taken by the agent.
            is_action_random: Whether action was an exploratory action.
            reward: Rewards received from the environment.

        Returns:
            None
        """
        s = self.last_state_str
        a = self.last_action
        sp = self.state_str
        ap = action

        if s is not None:
            # update e
            if ALGO == ALGO_Q_LEARNING and self.was_last_action_random:
                # Q(lambda): Set all traces to zero.
                self.e = {}
            else:
                for key in self.e.iterkeys():
                    self.e[key] *= (self.gamma * self.lamda)

            # replacing traces
            self.e[(s, a)] = 1.0
            # set the trace for the other actions to 0
            for other_action in state.action_object.get_all_actions():
                if other_action != a:
                    if (s, other_action) in self.e:
                        self.e[(s, other_action)] = 0

            # See: https://en.wikipedia.org/wiki/State-Action-Reward-State-Action
            if state.is_final():
                delta = reward - self.Q.get((s, a), self.get_default_q(s))
            else:
                if ALGO == ALGO_SARSA:
                    # Just consider the action we took in sp.
                    next_state_v = self.Q.get((sp, ap), self.get_default_q(sp))
                elif ALGO == ALGO_Q_LEARNING:
                    # Consider the best we could do from sp.
                    next_state_v = self.astar_value[sp[:-2]]  # state_str_no_roll
                delta = (reward +
                         self.gamma * next_state_v -
                         self.Q.get((s, a), self.get_default_q(s)))

            self.update_values(delta)

        # save visited state and chosen action
        self.last_state_str = self.state_str
        self.last_action = action
        self.was_last_action_random = is_action_random
        if action is not None:  # end_episode calls this with action=None.
            key = (self.last_state_str, self.last_action)
            self.visit_count[key] = self.visit_count.get(key, 0) + 1

    def select_action(self, state):
        self.state_str = str(state)

        can_choose_roll = (True if state.stochastic_p < state.exp_params.choose_roll
                           else False)

        epsilon = self.epsilon if self.is_learning else 0
        choose_random_action = True if random.random() < epsilon else False

        if TRAIN_BUDDY == TRAIN_BUDDY_SELF:
            reverse = state.player_to_move == PLAYER_WHITE
        else:
            # When TRAIN_BUDDY != TRAIN_BUDDY_SELF, the agent maintains (in
            # Q table) state values for white and black players from their
            # own perspectives.  So, regardless of player's color, we need
            # to pick actions leading to states with higher values.
            reverse = True

        all_rolls = state.die_object.get_all_sides()
        avail_rolls = all_rolls if can_choose_roll else [state.roll]

        action_values = []  # For all avail_rolls: (roll, action) -> value.
        roll_values = [None] * len(all_rolls)  # For all rolls: roll -> value.
        for replace_roll in all_rolls:
            roll_index = replace_roll - 1
            state.roll = replace_roll
            self.state_str = str(state)
            for checker in state.action_object.get_all_checkers():
                move_outcome = state.get_move_outcome(checker)
                if move_outcome is not None:
                    move_value = self.Q.get((self.state_str, checker),
                                            self.get_default_q(self.state_str))
                    if roll_values[roll_index] is None:
                        roll_values[roll_index] = move_value
                    else:
                        if reverse:  # We want the action with highest value.
                            if move_value > roll_values[roll_index]:
                                roll_values[roll_index] = move_value
                        else:
                            if move_value < roll_values[roll_index]:
                                roll_values[roll_index] = move_value
                    # Consider this roll-action for choosing the best action
                    # only if the associated roll is available to the agent.
                    if replace_roll in avail_rolls:
                        # insert a random number to break the ties
                        action_values.append(((move_value, random.random()),
                                              (replace_roll, checker)))

        # Compute max_b Q(s, b), for undetermined roll, under current
        # choose_roll probability.
        # First have to remove Nones for rolls that are not legal.
        legal_roll_values = [v for v in roll_values if v is not None]
        num_legal_rolls = len(legal_roll_values)
        avg_value = float(sum(legal_roll_values)) / num_legal_rolls
        if reverse:
            value_with_choose_roll = exp_params.choose_roll * max(legal_roll_values)
        else:
            value_with_choose_roll = exp_params.choose_roll * min(legal_roll_values)
        value_with_random_roll = (1 - exp_params.choose_roll) * avg_value
        astar_value = value_with_random_roll + value_with_choose_roll
        state_str_no_roll = str(state)[:-2]
        self.astar_value[state_str_no_roll] = astar_value

        # Select best action.
        if action_values:  # len(action_values) > 0:
            action_values_sorted = sorted(action_values, reverse=reverse)
            if choose_random_action:
                index = random.randint(0, len(action_values) - 1)
            else:
                index = 0
            best_roll = action_values_sorted[index][1][0]
            # set the best roll there
            state.roll = best_roll
            self.state_str = str(state)
            action = action_values_sorted[index][1][1]
        else:
            action = state.action_object.action_forfeit_move

            # if (action != state.action_object.action_forfeit_move or
            #         state.can_forfeit_move()):
            #     done = True
            # else:
            #     state.reroll_dice()

        # Update values.
        if self.is_learning:
            self.sarsa_step(state, action, is_action_random=choose_random_action)

        return action

    # Unused method.
    def get_board_value(self, board_str, all_rolls, all_actions):
        INVALID_ACTION_VALUE = -2
        sum_values = 0.0
        count = 0
        for roll in all_rolls:
            state_str = board_str + ('-%d' % roll)
            action_values = []
            for action in all_actions:
                action_value = self.Q.get((state_str, action), INVALID_ACTION_VALUE)
                # insert a random number to break the ties
                action_values.append(((action_value, random.random()), action))
            # TODO: Always sorting with reverse=True is wrong.
            action_values_sorted = sorted(action_values, reverse=True)
            best_action_value = action_values_sorted[0][0][0]

            if best_action_value != INVALID_ACTION_VALUE:
                sum_values += best_action_value
                count += 1

        if count == 0:
            return INVALID_ACTION_VALUE
        else:
            return sum_values / count

    def update_values(self, delta):
        alpha = self.alpha
        for (si, ai) in self.e.iterkeys():
            if SARSA_USE_ALPHA_ANNEALING:
                alpha = 1.0 / self.visit_count.get((si, ai), 1)
                alpha = max(alpha, SARSA_ALPHA)
            if self.e[(si, ai)] != 0.0:
                change = alpha * delta * self.e[(si, ai)]
                self.Q[(si, ai)] = self.Q.get((si, ai), self.get_default_q(si)) + change

    @classmethod
    def get_knowledge_filename(cls):
        exp_params = ExpParams.get_exp_params_from_command_line_args()
        filename = exp_params.get_custom_filename_no_trial(FOLDER_QTABLE,
                                                           FILE_PREFIX_SARSA)
        return filename

    def save_knowledge(self):
        filename = self.get_knowledge_filename()
        f = open(filename, 'w')
        pickle.dump(self.Q, f)
        f.close()

    def load_knowledge(self):
        filename = self.get_knowledge_filename()
        f = open(filename, 'r')
        self.Q = pickle.load(f)
        f.close()

    def pause_learning(self):
        self.is_learning = False

    def resume_learning(self):
        self.is_learning = True

    # def save_learning_state(self):
    #     self.Q_save = copy.deepcopy(self.Q)
    #
    # def restore_learning_state(self):
    #     self.Q = copy.deepcopy(self.Q_save)

    def print_Q(self):
        print "Q:"
        # Q_keys = self.Q.keys()
        # Q_keys.sort()
        # for key in Q_keys:
        #     print "Q%s -> %.2f" % (key, self.Q[key])
        # for key, value in sorted(self.Q.iteritems(), key=lambda (k, v): (v, k)):
        #     print "%s: %s" % (key, value)
        for (si, ai), visit_count in sorted(self.visit_count.iteritems(),
                                            key=lambda (k, v): (v, k)):
            value = self.Q.get((si, ai), self.get_default_q(str(si)))
            print "%s: %+.2f, visited: %d" % ((si, ai), value, visit_count)

    def print_e(self):
        e_keys = self.e.keys()
        e_keys.sort()
        print "e:"
        for key in e_keys:
            print "e%s -> %.10f" % (key, self.e[key])

    def print_visit_count(self):
        keys = self.visit_count.keys()
        keys.sort()
        print "Visit Counts:"
        # for key in Q_keys:
        #     print "Q%s -> %.2f" % (key, self.Q[key])
        for key, value in sorted(self.visit_count.iteritems(), key=lambda (k, v): (v, k)):
            print "%s: %s" % (key, value)

    def print_learner_state(self):
        self.print_visit_count()
        self.print_e()
        self.print_Q()


if __name__ == '__main__':
    make_data_folders()
    exp_params = ExpParams.get_exp_params_from_command_line_args()

    filename = exp_params.get_trial_filename(FILE_PREFIX_SARSA)
    f = open(filename, 'w')

    agent_sarsa = AgentSarsa(exp_params.state_class)
    if TRAIN_BUDDY == TRAIN_BUDDY_SELF:
        agent_train_buddy = agent_sarsa
    elif TRAIN_BUDDY == TRAIN_BUDDY_COPY:
        # agent_train_buddy = AgentSarsa(exp_params.state_class)
        agent_train_buddy = AgentSarsa(exp_params.state_class)
        # # Use this for evaluating against pre-trained version of self:
        # agent_train_buddy = AgentSarsa(exp_params.state_class, load_knowledge=True)
    elif TRAIN_BUDDY == TRAIN_BUDDY_RANDOM:
        agent_train_buddy = AgentRandom(exp_params.state_class)
    agent_eval = Experiment.create_eval_opponent_agent(exp_params)
    print 'Training buddy is: %s' % agent_train_buddy
    print 'Evaluation opponent is: %s' % agent_eval

    for i in range(SARSA_NUM_TRAINING_ITERATIONS):
        print 'Iteration %d' % i
        print 'Evaluating (%d games)...' % SARSA_NUM_EVAL_EPISODES

        agent_sarsa.pause_learning()
        game_set = GameSet(exp_params, SARSA_NUM_EVAL_EPISODES, agent_sarsa,
                           agent_eval)
        count_wins = game_set.run()
        agent_sarsa.resume_learning()
        win_rate = float(count_wins[0]) / SARSA_NUM_EVAL_EPISODES
        print 'Win rate against evaluation opponent: %.2f' % win_rate
        f.write('%d %f\n' % (i * SARSA_NUM_EPISODES_PER_ITERATION, win_rate))
        f.flush()

        agent_sarsa.resume_learning()

        print 'Training (%d games)...' % SARSA_NUM_EPISODES_PER_ITERATION
        # # when training for benchmark, have the RL agent play as black
        # game_set = Domain.GameSetClass(NUM_ITERATIONS, agent_eval, agent_sarsa,
        #                                p, reentry_offset,
        #                                print_learning_progress = True)
        game_set = GameSet(exp_params, SARSA_NUM_EPISODES_PER_ITERATION,
                           agent_sarsa, agent_train_buddy)
        count_wins = game_set.run()
        agent_sarsa.algorithm.print_learner_state()
        print 'Win rate in training: %.2f' % (float(count_wins[0]) /
                                              SARSA_NUM_EPISODES_PER_ITERATION)

    if SARSA_SAVE_TABLES and exp_params.is_first_trial():
        print 'Saving RL table...'
        agent_sarsa.algorithm.save_knowledge()
        agent_sarsa.algorithm.print_learner_state()

    # if SARSA_SAVE_STATE_VALUES_IN_GRAPH and exp_params.is_graph_based() and \
    #         exp_params.is_first_trial():
    #     print 'Saving state values in graph...'
    #     exp_params.domain.StateClass.copy_state_values_to_graph(exp_params,
    #                                                             agent_sarsa)
