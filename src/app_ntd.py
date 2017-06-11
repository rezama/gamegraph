'''
Created on Dec 9, 2011

@author: reza
'''
import random
import numpy as np
from pybrain.datasets.supervised import SupervisedDataSet  # pylint: disable=import-error
from pybrain.supervised.trainers.backprop import BackpropTrainer  # pylint: disable=import-error

from app_random_games import AgentRandom
from common import (FILE_PREFIX_NTD, PLAYER_WHITE, REWARD_LOSE, REWARD_WIN,
                    AgentNeural, Experiment, ExpParams, GameSet, PrettyFloat,
                    make_data_folders)
from params import (ALGO, ALGO_Q_LEARNING, ALGO_SARSA, NTD_ALPHA, NTD_EPSILON,
                    NTD_EPSILON_ANNEAL_TIME, NTD_EPSILON_END,
                    NTD_EPSILON_START, NTD_GAMMA, NTD_LAMBDA,
                    NTD_LEARNING_RATE, NTD_NETWORK_INIT_WEIGHTS,
                    NTD_NUM_EVAL_GAMES, NTD_NUM_ITERATIONS, NTD_NUM_OUTPUTS,
                    NTD_NUM_TRAINING_GAMES, NTD_SEARCH_PLIES, NTD_TRAIN_EPOCHS,
                    NTD_USE_ALPHA_ANNEALING, NTD_USE_EPSILON_ANNEALING,
                    PRINT_GAME_RESULTS, TRAIN_BUDDY, TRAIN_BUDDY_COPY,
                    TRAIN_BUDDY_RANDOM, TRAIN_BUDDY_SELF)
from state_graph import VAL_ATTR


class AgentNTD(AgentNeural):

    def __init__(self, state_class, load_knowledge=False):
        super(AgentNTD, self).__init__(state_class, NTD_NUM_OUTPUTS,
                                       init_weights=NTD_NETWORK_INIT_WEIGHTS)

        # Predicting separate state-action values for white and black only makes
        # sense when training against self.
        if NTD_NUM_OUTPUTS == 2:
            assert TRAIN_BUDDY == TRAIN_BUDDY_SELF

        self.trainer = BackpropTrainer(self.network,
                                       learningrate=NTD_LEARNING_RATE,
                                       momentum=0.0, verbose=False)

        self.epsilon = NTD_EPSILON
        self.lamda = NTD_LAMBDA
        self.alpha = NTD_ALPHA
        self.gamma = NTD_GAMMA

        # self.state_str = None
        # self.state_in = None
        self.last_state_str = None
        # self.last_state_in = None
        self.last_action = None
        # Since we apply updates with one step delay, need to remember Whether
        # the action in previous time step was exploratory.
        self.was_last_action_random = False

        self.processed_final_reward = False
        self.episode_traj = ''

        self.is_learning = True
        self.e = {}
        self.updates = {}
        # astar_value[s'] = argmax_b Q(s', b) for undetermined roll.
        self.astar_value = {}
        # Used for alpha annealing.  Note that the roll value that is recorded
        # reflects the roll chosen by the agent, not the original random roll.
        # So, including the roll makes sense for calculating the updates, which
        # are based on the action chosen by the agent.  But it doesn't make
        # sense for epsilon annealing, which is calculated before the agent
        # is asked to take an action.
        self.visit_count = {}  # Example key: (w-5-1, action)
        # Used for epsilon annealing.
        self.visit_count_no_roll = {}  # Example key: w-5
        self.visited_in_episode = {}
        self.network_inputs = {}
        self.network_outputs = {}

        # Recording value of intersting states over time.
        self.num_training_games = 0
        self.value_tracker_file = None
        # network_predictions are gathered at the end of each iteration to
        # produce reports.
        self.network_predictions = {}

        # TODO: Merge this functionality with COLLECT_STATS logic.
        self.traj_count = {}

        if load_knowledge:
            raise ValueError('AgentNTD does not support load_knowledge.')
            # self.is_learning = False

    def begin_episode(self):
        self.e = {}
        self.astar_value = {}
        self.updates = {}
        if self.is_learning:
            self.network_outputs = {}
        self.visited_in_episode = {}
        # self.state_str = None
        # self.state_in = None
        self.last_state_str = None
        # self.last_state_in = None
        self.last_action = None
        self.processed_final_reward = False
        self.episode_traj = ''

    def end_episode(self, reward):
        if self.is_learning and not self.processed_final_reward:
            if TRAIN_BUDDY == TRAIN_BUDDY_SELF:
                # Ignore the reward parameter and construct own reward signal
                # corresponding to the probability of white winning.
                rewards = self.compute_values_for_final_state(self.state)
                # winner = other_player(self.state.player_to_move)
                # if winner == PLAYER_WHITE:
                #     rewards = np.array([REWARD_WIN, REWARD_LOSE])
                # else:
                #     rewards = np.array([REWARD_LOSE, REWARD_WIN])
                #
                # if self.outputdim == 1:
                #     rewards = rewards[:1]
            else:
                rewards = np.array([reward])

            self.ntd_step(action=None, is_action_random=False, rewards=rewards)

            if PRINT_GAME_RESULTS:
                print 'Episode traj: %s' % self.episode_traj
            self.traj_count[self.episode_traj] = self.traj_count.get(self.episode_traj, 0) + 1

            self.apply_updates()
            self.processed_final_reward = True

    def update_values(self, delta):
        # Number of elements in delta depends on NTD_NUM_OUTPUTS.
        if all(v == 0 for v in delta):  # If aLL elements in delta are zero.
            return
        alpha = self.alpha
        for (si, ai) in self.e.iterkeys():
            if NTD_USE_ALPHA_ANNEALING:
                alpha = 1.0 / self.visit_count.get((si, ai), 1)
                alpha = max(alpha, NTD_ALPHA)
            if self.e[(si, ai)] != 0.0:
                change = [alpha * x * self.e[(si, ai)] for x in delta]
                # network_in = self.network_inputs[si]
                current_update = self.updates.get((si, ai), [0.0] * self.outputdim)
                self.updates[(si, ai)] = [a + b for a, b in zip(current_update, change)]

    def apply_updates(self):
        dataset = SupervisedDataSet(self.inputdim, self.outputdim)
        for (si, ai) in self.updates.iterkeys():
            si_ai = '%s-%s' % (si, ai)
            network_in = self.network_inputs[si_ai]
            current_value = self.get_network_value(None, None, si_ai)
            new_value = [a + b for a, b in zip(current_value, self.updates[(si, ai)])]
            dataset.addSample(network_in, new_value)
            if PRINT_GAME_RESULTS:
                print 'updating (%s, %s) from %s to %s' % (
                    si, ai, map(PrettyFloat, current_value),
                    map(PrettyFloat, new_value))
        # import pdb; pdb.set_trace()
        if dataset:  # len(dataset) > 0:
            self.trainer.setData(dataset)
            self.trainer.trainEpochs(NTD_TRAIN_EPOCHS)
        # print '----'

    def compute_values_for_final_state(self, state):
        if state.has_player_won(PLAYER_WHITE):
            values = np.array([REWARD_WIN, REWARD_LOSE])
        else:
            values = np.array([REWARD_LOSE, REWARD_WIN])

        if self.outputdim == 1:
            values = values[:1]

        return values

    def get_Q_value(self, state, action):
        """Returns state-action value.

        Args:
            state: State for which value is requested.
            action: Action for which value is requested.


        Returns:
            List containing NTD_NUM_OUTPUTS elements.
            When NTD_NUM_OUTPUTS == 1, one-dimensional return value can be
            intepretted as [p_w] showing the probability for white winning.
            When NTD_NUM_OUTPUTS == 2, the two-dimensional return value can be
            intepretted as [p_w, p_b] showing probabilities for white or black
            winning.
        """
        if state.is_final():
            # The algorithm never trains the network on final states, so it
            # cannot know their values.  Need to retrieve the value of final
            # states directly.
            values = self.compute_values_for_final_state(state)
        else:
            network_out = self.get_network_value(state, action)
            values = network_out
        # # If player to move is white, it means black is considering a move
        # # outcome, so black is evaluating the position.
        # if state.player_to_move == PLAYER_WHITE:
        #     multiplier = -1.0
        # else:
        #     multiplier = 1.0
        # return multiplier * state_value
        return values
        # if state.player_to_move == PLAYER_WHITE:
        #    return network_out[1]
        # else:
        #    return network_out[0]

    # def cache_network_values(self, state):
    #     state_str = str(state)[:-2]
    #     if state_str not in self.network_inputs:
    #         self.network_inputs[state_str] = state.encode_network_input()
    #     network_in = self.network_inputs[state_str]
    #     if state_str not in self.network_outputs:
    #         self.network_outputs[state_str] = self.network.activate(network_in)

    # This function needs to receive the actual state object, because it needs
    # to calculate the corresponding network inputs for it.
    def get_network_value(self, state, action, state_action_str=None):
        if state_action_str:
            assert state is None
            assert action is None
            assert state_action_str in self.network_outputs
            return self.network_outputs[state_action_str]
        else:
            state_action_str = '%s-%s' % (state, action)
            if state_action_str in self.network_outputs:
                return self.network_outputs[state_action_str]
            if state_action_str not in self.network_inputs:
                self.network_inputs[state_action_str] = state.encode_network_input(action)
            network_in = self.network_inputs[state_action_str]
            self.network_outputs[state_action_str] = self.network.activate(network_in)
            return self.network_outputs[state_action_str]

    def ntd_step(self, action, is_action_random, rewards=None):
        """Updates the underlying model after every transition.

        This method is called in self.select_action() and self.end_episode().

        Args:
            action: Action taken by the agent.
            is_action_random: Whether action was an exploratory action.
            rewards: List of reward components received from the environment.

        Returns:
            None
        """
        if rewards is None:
            rewards = [0.0] * self.outputdim
        assert len(rewards) == self.outputdim

        s = self.last_state_str
        a = self.last_action
        sp = self.state
        ap = action

        # state_str_no_roll = str(self.state)[:-2]
        if action is None:
            self.episode_traj += ' -> %s.' % str(self.state)
        else:
            self.episode_traj += ' -> %s, %s' % (str(self.state), action)

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
            for other_action in self.state.action_object.get_all_actions():
                if other_action != a:
                    if (s, other_action) in self.e:
                        self.e[(s, other_action)] = 0

            s_a = '%s-%s' % (s, a)
            if self.state.is_final():
                # delta = reward - self.Q.get((s, a), self.default_q)
                # print 'Shouldn\'t happen'
                # if self.is_learning:
                #     import pdb; pdb.set_trace()
                delta = rewards - self.get_network_value(None, None, s_a)
            else:
                # delta = (reward + self.gamma * self.Q.get((sp, ap), self.default_q) -
                #                   self.Q.get((s, a), self.default_q))
                # delta = (reward + self.gamma * self.get_network_value(sp_in) -
                #                   self.get_network_value(s_in))
                # In our domains, only the very last state transition receives
                # a reward.
                assert all(v == 0 for v in rewards)
                if ALGO == ALGO_SARSA:
                    # Just consider the action we took in sp.
                    next_state_v = self.get_network_value(sp, ap)
                elif ALGO == ALGO_Q_LEARNING:
                    # Consider the best we could do from sp.
                    next_state_v = self.astar_value[str(sp)[:-2]]  # state_str_no_roll

                delta = (rewards + self.gamma * next_state_v -
                         self.get_network_value(None, None, s_a))

            self.update_values(delta)
        else:
            # Just cache the value of current state-action, so we can access
            # it on the next call to this method, when it's requested as s_a.
            self.get_network_value(sp, ap)

        # save visited state and chosen action
        self.last_state_str = str(self.state)
        # self.last_state_in = self.state_in
        self.last_action = action
        self.was_last_action_random = is_action_random
        if action is not None:  # end_episode calls this with action=None.
            key = (self.last_state_str, self.last_action)
            if key not in self.visited_in_episode:
                self.visit_count[key] = self.visit_count.get(key, 0) + 1
            self.visited_in_episode[key] = True

    def select_action(self):
        # self.last_played_as = self.state.player_to_move
        # self.cache_network_values(self.state)
        # self.state_str = str(self.state)[:-2]

        # if self.state_str not in self.network_inputs:
        #     self.network_inputs[self.state_str] = self.encode_network_input(self.state)
        # self.state_in = self.network_inputs[self.state_str]

        if self.is_learning:
            if NTD_USE_EPSILON_ANNEALING:
                # Since under some conditions the current roll can be entirely
                # ignored (--chooseroll=1.0), it makes sense to exclude the
                # current roll from visit counts.
                state_str_no_roll = str(self.state)[:-2]
                self.visit_count_no_roll[state_str_no_roll] = (
                    self.visit_count_no_roll.get(state_str_no_roll, 0) + 1)
                # Following logic with example: anneal_time = 100, visit_count = 5.
                time_to_end = max(0, NTD_EPSILON_ANNEAL_TIME -
                                  self.visit_count_no_roll.get(state_str_no_roll, 0))
                ratio = float(time_to_end) / NTD_EPSILON_ANNEAL_TIME # 0.95
                epsilon = NTD_EPSILON_END + (NTD_EPSILON_START - NTD_EPSILON_END) * ratio
                # print "State: %s, visits: %d, time_to_end: %d, ratio: %.2f, epsilon: %.2f" % (
                #     state_str, self.visit_count.get(state_str, 0), time_to_end, ratio, epsilon)
            else:
                epsilon = self.epsilon
        else:
            epsilon = 0

        choose_random_action = True if random.random() < epsilon else False

        # Select the best action.
        action, _ = self.select_action_with_search(
            state=self.state, choose_random_action=choose_random_action,
            plies=NTD_SEARCH_PLIES)

        # Update values.
        if self.is_learning:
            self.ntd_step(action, is_action_random=choose_random_action)

        return action

    # def save_knowledge(self):
    #
    #     filename = './td-network.txt' % Domain.name
    #     f = open(filename, 'w')
    #     pickle.dump(self.network, f)
    #     f.close()
    #
    # def load_knowledge(self):
    #     filename = './td-network-%s.txt' % Domain.name
    #     f = open(filename, 'r')
    #     self.network = pickle.load(f)
    #     f.close()

    def pause_learning(self):
        self.is_learning = False

    def resume_learning(self):
        self.is_learning = True

    def print_e(self):
        e_keys = self.e.keys()
        e_keys.sort()
        print "e:"
        for key in e_keys:
            print "e%s -> %.10f" % (key, self.e[key])

    def print_visit_count(self):
        print "Visit Counts:"
        # keys = self.visit_count.keys()
        # keys.sort()
        # for key in Q_keys:
        #     print "Q%s -> %.2f" % (key, self.Q[key])
        for key, value in sorted(self.visit_count.iteritems(), key=lambda (k, v): (v, k)):
            print "%s: %s" % (key, value)

    def probe_network(self):
        exp_params = ExpParams.get_exp_params_from_command_line_args()
        graph = exp_params.state_class.GAME_GRAPH

        print "Network predictions:"
        self.network_predictions = {} # Network predictions.
        true_values = {} # True values obtained from the graph using value iteration.
        for state_roll_action_str in sorted(self.network_inputs.iterkeys()):
            # state_value = self.network_outputs[state_str]
            state_roll_action_value = self.network.activate(
                self.network_inputs[state_roll_action_str])
            self.network_predictions[state_roll_action_str] = state_roll_action_value
            node_id = graph.get_node_id(state_roll_action_str[:-4])  # Removes roll and action.
            true_value = graph.get_attr(node_id, VAL_ATTR)
            true_values[state_roll_action_str] = true_value
            # print "%s -> %s (%.2f)" % (state_str, state_value, abs_value)
        for (si, ai), _ in sorted(self.visit_count.iteritems(),
                                  key=lambda (k, v): (v, k)):
            state_roll_action_str = '%s-%s' % (si, ai)
            true_value = true_values[state_roll_action_str]
            # Reward for white win is [1, 0],
            # Reward for black win is [0, 1],
            # state_value[0] - state_value[1] ranges from -1 to +1, although
            # it can exceed those bounds when the network outputs are
            # outside the range [0, 1].
            # The following formula is meant to scale the difference to range [0, 1].
            print "(%s, %s): opt. val. for white: %+.2f prediction: %s visited: %d" % (
                si, ai, true_value,
                map(PrettyFloat, self.network_predictions[state_roll_action_str]),
                self.visit_count.get((si, ai), 0))
        print ('Note: optimal values for white are based on the board '
               'positions only and ignore the current roll.')

    def track_interesting_states(self):
        interesting_states = self.state.interesting_states()
        if interesting_states:
            if not self.value_tracker_file:
                value_tracker_filename = (
                    self.state.exp_params.get_value_tracker_filename(FILE_PREFIX_NTD))
                self.value_tracker_file = open(value_tracker_filename, 'w')
            self.num_training_games += NTD_NUM_TRAINING_GAMES
            self.value_tracker_file.write('%d' % self.num_training_games)
            for s in interesting_states:
                s_val = self.network_predictions[s][0] if s in self.network_predictions else 0.5
                self.value_tracker_file.write(' %f' % s_val)
            self.value_tracker_file.write('\n')
            self.value_tracker_file.flush()

    def print_traj_counts(self):
        print "Trajectories in training:"
        import operator
        sorted_traj_count = sorted(self.traj_count.items(),
                                   key=operator.itemgetter(1),
                                   reverse=True)
        for traj, cnt in sorted_traj_count:
            print "%s: %d" % (traj, cnt)
        # Reset after each query.
        self.traj_count = {}

    def print_learner_state(self):
        self.print_visit_count()
        self.print_e()
        self.probe_network()
        self.print_traj_counts()


if __name__ == '__main__':
    make_data_folders()
    exp_params = ExpParams.get_exp_params_from_command_line_args()

    filename = exp_params.get_trial_filename(FILE_PREFIX_NTD)
    f = open(filename, 'w')

    agent_ntd = AgentNTD(exp_params.state_class)
    if TRAIN_BUDDY == TRAIN_BUDDY_SELF:
        agent_train_buddy = agent_ntd
    elif TRAIN_BUDDY == TRAIN_BUDDY_COPY:
        agent_train_buddy = AgentNTD(exp_params.state_class)
    elif TRAIN_BUDDY == TRAIN_BUDDY_RANDOM:
        agent_train_buddy = AgentRandom(exp_params.state_class)
    agent_eval = Experiment.create_eval_opponent_agent(exp_params)
    print 'Training buddy is: %s' % agent_train_buddy
    print 'Evaluation opponent is: %s' % agent_eval

    for i in range(NTD_NUM_ITERATIONS):
        # import pdb; pdb.set_trace()
        print 'Iteration %d' % i
        print 'Evaluating against opponent (%d games)...' % NTD_NUM_EVAL_GAMES

        agent_ntd.pause_learning()
        game_set = GameSet(exp_params, NTD_NUM_EVAL_GAMES, agent_ntd,
                           agent_eval)
        count_wins = game_set.run()
        win_rate = float(count_wins[0]) / NTD_NUM_EVAL_GAMES
        print 'Win rate against evaluation opponent: %.2f' % win_rate
        f.write('%d %f\n' % (i, win_rate))
        f.flush()

        print
        print 'Trajectories in evaluation:'
        agent_ntd.print_traj_counts()
        agent_ntd.resume_learning()

        print 'Training (%d games)...' % NTD_NUM_TRAINING_GAMES
        game_set = GameSet(exp_params, NTD_NUM_TRAINING_GAMES,
                           agent_ntd, agent_train_buddy)
        count_wins = game_set.run()
        agent_ntd.print_learner_state()
        print 'Win rate in training: %.2f' % (float(count_wins[0]) /
                                              NTD_NUM_TRAINING_GAMES)
        print 'White wins in training: %.2f' % (float(count_wins[2]) /
                                                NTD_NUM_TRAINING_GAMES)

    f.close()
