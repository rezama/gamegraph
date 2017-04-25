'''
Created on Dec 9, 2011

@author: reza
'''
import random

from pybrain.datasets.supervised import SupervisedDataSet  # pylint: disable=import-error
from pybrain.supervised.trainers.backprop import BackpropTrainer  # pylint: disable=import-error

from common import (FILE_PREFIX_NTD, PLAYER_WHITE, REWARD_LOSE, REWARD_WIN,
                    Experiment, ExpParams, make_data_folders, other_player)
from domain import AgentNeural, GameSet
from params import (ALTERNATE_SEATS, NTD_ALPHA, NTD_EPSILON, NTD_GAMMA,
                    NTD_LAMBDA, NTD_LEARNING_RATE, NTD_NETWORK_INIT_WEIGHTS,
                    NTD_NUM_EVAL_GAMES, NTD_NUM_ITERATIONS,
                    NTD_NUM_TRAINING_GAMES, NTD_TRAIN_EPOCHS,
                    NTD_USE_ALPHA_ANNEALING)


class AgentNTD(AgentNeural):

    def __init__(self, state_class, load_knowledge=False):
        super(AgentNTD, self).__init__(state_class, 2,
                                       init_weights=NTD_NETWORK_INIT_WEIGHTS)

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
        self.processed_final_reward = False
        # self.last_played_as = None
        self.episode_traj = ''

        self.is_learning = True

        self.e = {}
        self.updates = {}
        self.visit_count = {}
        self.visited_in_episode = {}
        self.network_inputs = {}
        self.network_outputs = {}

        self.traj_count = {}

        if load_knowledge:
            raise ValueError('AgentNTD does not support load_knowledge.')
            # self.is_learning = False

    def begin_episode(self):
        self.e = {}
        self.updates = {}
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
        if self.is_learning and (not self.processed_final_reward):
            winner = other_player(self.state.player_to_move)
            reward_list = [REWARD_LOSE, REWARD_LOSE]
            reward_list[winner] = REWARD_WIN

            self.ntd_step(action=None, reward=reward_list)

            self.traj_count[self.episode_traj] = self.traj_count.get(self.episode_traj, 0) + 1

            self.apply_updates()
            self.processed_final_reward = True

    def update_values(self, delta):
        if delta[0] == 0.0 and delta[1] == 0.0:
            return
        alpha = self.alpha
        for si in self.e.iterkeys():
            if NTD_USE_ALPHA_ANNEALING:
                alpha = 1.0 / self.visit_count.get(si, 1)
            if self.e[si] != 0.0:
                change = [alpha * e * self.e[si] for e in delta]
                # network_in = self.network_inputs[si]
                current_update = self.updates.get(si, [0.0, 0.0])
                self.updates[si] = [a + b for a, b in zip(current_update, change)]

    def apply_updates(self):
        dataset = SupervisedDataSet(self.inputdim, 2)
        for si in self.updates.iterkeys():
            network_in = self.network_inputs[si]
            current_value = self.get_network_value(si)
            new_value = [a + b for a, b in zip(current_value, self.updates[si])]
            dataset.addSample(network_in, new_value)
            # print 'updating %s from [%.2f, %.2f] to [%.2f, %.2f]' % (si,
            #     current_value[0], current_value[1], new_value[0], new_value[1])
        if dataset:  # len(dataset) > 0:
            self.trainer.setData(dataset)
            self.trainer.trainEpochs(NTD_TRAIN_EPOCHS)
        # print '----'

    def get_state_value(self, state):
        """Returns state value.  Higher is better for requesting player.

        Args:
            state: state for which value is requested.

        Returns:
            scalar representing value for requesting player.  The underlying
            AgentNeural returns the state value as a pair (p_w, p_b) showing
            probabilities for white or black winning the game from the requested
            state.  This function returns p_w - p_b when the requesting player
            is white and p_b - p_w when the requesting player is black.
        """
        if state.is_final():
            # The algorithm never trains the network on final states, so it
            # cannot know their values.  Need to retrieve the value of final
            # states directly.
            if state.has_player_won(PLAYER_WHITE):
                white_black_values = [REWARD_WIN, REWARD_LOSE]
            else:
                white_black_values = [REWARD_LOSE, REWARD_WIN]
        else:
            self.cache_network_values(state)
            state_str = str(state)[:-2]
            network_out = self.get_network_value(state_str)
            white_black_values = network_out
        # If player to move is white, it means black is considering a move
        # outcome, so black is evaluating the position.
        if state.player_to_move == PLAYER_WHITE:
            multiplier = -1.0
        else:
            multiplier = 1.0
        return multiplier * (white_black_values[0] - white_black_values[1])
        # if state.player_to_move == PLAYER_WHITE:
        #    return network_out[1]
        # else:
        #    return network_out[0]

    def cache_network_values(self, state):
        state_str = str(state)[:-2]
        if state_str not in self.network_inputs:
            self.network_inputs[state_str] = state.encode_network_input()
        network_in = self.network_inputs[state_str]
        if state_str not in self.network_outputs:
            self.network_outputs[state_str] = self.network.activate(network_in)

    def get_network_value(self, state_str):
        return self.network_outputs[state_str]

    def ntd_step(self, action, reward=[0, 0]):
        """Updates the underlying model after every transition.

        This method is called in self.select_action() and self.end_episode().

        Args:
            action: Action taken by the agent.
            reward: Rewards received from the environment.

        Returns:
            None
        """
        s = self.last_state_str
        # s_in = self.last_state_in
        # Since the NTD agent's operates based on state values and not
        # state-action values, we don't need a, ap in this method.
        # a = self.last_action
        state_str = str(self.state)[:-2]
        sp = state_str
        # sp_in = self.state_in
        # ap = action

        self.episode_traj += ' -> ' + state_str

        if s is not None:
            # update e
            for key in self.e.iterkeys():
                self.e[key] *= (self.gamma * self.lamda)

            # replacing traces
            self.e[s] = 1.0
            # # set the trace for the other actions to 0
            # for other_action in Domain.ActionClass.ALL_ACTIONS:
            #     if other_action != a:
            #         self.e[(s, other_action)] = 0

            if self.state.is_final():
                # delta = reward - self.Q.get((s, a), self.default_q)
                # print 'Shouldn\'t happen'
                delta = reward - self.get_network_value(s)
            else:
                # delta = reward + self.gamma * (self.Q.get((sp, ap), self.default_q) -
                #                                self.Q.get((s, a), self.default_q))
                delta = [self.gamma * x - y
                         for x, y in zip(self.get_network_value(sp), self.get_network_value(s))]
                # delta = reward + self.gamma * (self.get_network_value(sp_in) -
                #                                self.get_network_value(s_in))

            self.update_values(delta)

        # save visited state and chosen action
        self.last_state_str = state_str
        # self.last_state_in = self.state_in
        self.last_action = action
        if action is not None:  # end_episode calls this with action=None.
            key = self.last_state_str
            if key not in self.visited_in_episode:
                self.visit_count[key] = self.visit_count.get(key, 0) + 1
            self.visited_in_episode[key] = True

    def select_action(self):
        # self.last_played_as = self.state.player_to_move
        self.cache_network_values(self.state)
        # self.state_str = str(self.state)[:-2]

        # if self.state_str not in self.network_inputs:
        #     self.network_inputs[self.state_str] = self.encode_network_input(self.state)
        # self.state_in = self.network_inputs[self.state_str]

        if self.is_learning and (random.random() < self.epsilon):
            action = self.state.action_object.random_action(self.state)
        else:
            action = super(AgentNTD, self).select_action()
            # action_values = []
            # for checker in self.state.action_object.get_all_checkers():
            #     move_outcome = self.state.get_move_outcome(checker)
            #     if move_outcome is not None:
            #         move_value = self.get_state_value(move_outcome)
            #         # insert a random number to break the ties
            #         action_values.append(((move_value, random.random()), checker))
            #
            # if len(action_values) > 0:
            #     action_values_sorted = sorted(action_values, reverse=True)
            #     action = action_values_sorted[0][1]
            # else:
            #     action = self.state.action_object.action_forfeit_move

        # Update values.
        if self.is_learning:
            self.ntd_step(action)

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
        keys = self.visit_count.keys()
        keys.sort()
        print "Visit Counts:"
        # for key in Q_keys:
        #     print "Q%s -> %.2f" % (key, self.Q[key])
        for key, value in sorted(self.visit_count.iteritems(), key=lambda (k, v): (v, k)):
            print "%s: %s" % (key, value)

    def probe_network(self):
        print "Network predictions:"
        for state_str in sorted(self.network_inputs.iterkeys()):
            # state_value = self.network_outputs[state_str]
            state_value = self.network.activate(self.network_inputs[state_str])
            abs_value = state_value[0] - state_value[1]
            print "%s -> %s (%.2f)" % (state_str, state_value, abs_value)

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

    def print_values(self):
        self.print_visit_count()
        self.print_e()
        self.probe_network()
        self.print_traj_counts()


if __name__ == '__main__':
    make_data_folders()
    exp_params = ExpParams.get_exp_params_from_command_line_args()

    filename = exp_params.get_trial_filename(FILE_PREFIX_NTD)
    f = open(filename, 'w')

    agent_ntd1 = AgentNTD(exp_params.state_class)
    if not ALTERNATE_SEATS:
        agent_ntd2 = AgentNTD(exp_params.state_class)
    else:
        agent_ntd2 = agent_ntd1
    agent_eval = Experiment.create_eval_opponent_agent(exp_params)
    print 'Evaluation opponent is: %s' % agent_eval

    for i in range(NTD_NUM_ITERATIONS):
        print 'Iteration %d' % i
        print 'Evaluating against opponent (%d games)...' % NTD_NUM_EVAL_GAMES

        agent_ntd1.pause_learning()
        if not ALTERNATE_SEATS:
            agent_ntd2.pause_learning()
        for agent in [agent_ntd1]:
            game_set = GameSet(exp_params, NTD_NUM_EVAL_GAMES,
                               agent, agent_eval)
            count_wins = game_set.run()
            win_rate = float(count_wins[0]) / NTD_NUM_EVAL_GAMES
            # Report some useful information about the state of the learner.
            agent_ntd1.print_values()
            print 'Win rate against evaluation opponent: %.2f' % win_rate
            f.write('%d %f\n' % (i, win_rate))
        agent_ntd1.resume_learning()
        if not ALTERNATE_SEATS:
            agent_ntd2.resume_learning()

        print 'Training against self (%d games)...' % NTD_NUM_TRAINING_GAMES
        game_set = GameSet(exp_params, NTD_NUM_TRAINING_GAMES,
                           agent_ntd1, agent_ntd2)
        count_wins = game_set.run()
        print 'Win rate in training: %.2f' % (float(count_wins[0]) /
                                              NTD_NUM_TRAINING_GAMES)

    f.close()
