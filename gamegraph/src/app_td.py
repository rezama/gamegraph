'''
Created on Dec 9, 2011

@author: reza
'''
#import pickle
import random

from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.supervised.trainers.backprop import BackpropTrainer
from common import Experiment, PLAYER_WHITE, GameSet, other_player, REWARD_LOSE,\
    REWARD_WIN, FILE_PREFIX_TD
from params import TD_LEARNING_RATE, TD_EPSILON, TD_LAMBDA, TD_ALPHA, TD_GAMMA,\
    TD_TRAIN_EPOCHS, TD_USE_ALPHA_ANNEALING, TD_NUM_ITERATIONS,\
    TD_NUM_EVAL_GAMES, TD_NUM_TRAINING_GAMES, EVAL_OPPONENT, EVAL_OPPONENT_Q_LEARNING
from app_q_learning import AgentQLearning
from domain import AgentNeural, AgentRandom

class AgentTD(AgentNeural):
    
    def __init__(self, state_class, load_knowledge = False):
#        super(AgentTD, self).__init__(2, init_weights = 0.15)
        super(AgentTD, self).__init__(state_class, 2)

        self.trainer = BackpropTrainer(self.network, 
                                       learningrate = TD_LEARNING_RATE, 
                                       momentum = 0.0, verbose = False)
        
        self.epsilon = TD_EPSILON
        self.lamda = TD_LAMBDA
        self.alpha = TD_ALPHA
        self.gamma = TD_GAMMA
        
        self.state_str = None
        self.state_in = None
        self.last_state_str = None
        self.last_state_in = None
        self.last_action = None
        self.processed_final_reward = False
#        self.last_played_as = None
        
        self.is_learning = True
        
        self.e = {}
        self.updates = {}
        self.visit_count = {}
        self.visited_in_episode = {}
        self.network_inputs = {}
        self.network_outputs = {}

        if load_knowledge:
            self.load_knowledge()
            self.is_learning = False
                
    def begin_episode(self):
        self.e = {}
        self.updates = {}
        self.network_outputs = {}
        self.visited_in_episode = {}
        self.state_str = None
#        self.state_in = None
        self.last_state_str = None
#        self.last_state_in = None
        self.last_action = None
        self.processed_final_reward = False
        
    def end_episode(self, reward):
        if self.is_learning and (not self.processed_final_reward):
            s = self.last_state_str
#            s_in = self.last_state_in
            a = self.last_action
            
            winner = other_player(self.state.player_to_move)
            reward_list = [REWARD_LOSE, REWARD_LOSE]
            reward_list[winner] = REWARD_WIN
            
            current_value = self.get_network_value(s)
            delta = [a - b for a, b in zip(reward_list, current_value)]
            self.update_values(delta)
            self.apply_updates()
            self.processed_final_reward = True

    def update_values(self, delta):
        if delta == [0.0, 0.0]:
            return
        alpha = self.alpha
        for si in self.e.iterkeys():
            if TD_USE_ALPHA_ANNEALING:
                alpha = 1.0 / self.visit_count.get(si, 1)
            if self.e[si] != 0.0:
                change = [alpha * e * self.e[si] for e in delta]
#                network_in = self.network_inputs[si]
                current_update = self.updates.get(si, [0.0, 0.0])
                self.updates[si] = [a + b for a, b in zip(current_update, change)]
    
    def apply_updates(self):
        dataset = SupervisedDataSet(self.inputdim, 2)
        for si in self.updates.iterkeys():
            network_in = self.network_inputs[si]
            current_value = self.get_network_value(si)
            new_value = [a + b for a, b in zip(current_value, self.updates[si])]
            dataset.addSample(network_in, new_value)
#            print 'updating %s from [%.2f, %.2f] to [%.2f, %.2f]' % (si, 
#                current_value[0], current_value[1], new_value[0], new_value[1])
        if len(dataset) > 0:
            self.trainer.setData(dataset)
            self.trainer.trainEpochs(TD_TRAIN_EPOCHS)
#        print '----'
        
    def get_state_value(self, state):
        self.cache_network_values(state)
        state_str = str(state)[:-2]
        network_out = self.get_network_value(state_str)
        # if player to move is white, it means black is considering
        # a move outcome, so black is evaluating the position
        if state.player_to_move == PLAYER_WHITE:
            multiplier = -1.0
        else:
            multiplier = 1.0
        return multiplier * (network_out[0] - network_out[1])
#        if state.player_to_move == PLAYER_WHITE:
#            return network_out[1]
#        else:
#            return network_out[0]

    def cache_network_values(self, state):
        state_str = str(state)[:-2]
        if state_str not in self.network_inputs:
            self.network_inputs[state_str] = state.encode_network_input()
        network_in = self.network_inputs[state_str]
        if state_str not in self.network_outputs:
            self.network_outputs[state_str] = self.network.activate(network_in)
    
    def get_network_value(self, state_str):
        return self.network_outputs[state_str]

    def select_action(self):
#        self.last_played_as = self.state.player_to_move
        self.cache_network_values(self.state)
        self.state_str = str(self.state)[:-2]
#        if self.state_str not in self.network_inputs:
#            self.network_inputs[self.state_str] = self.encode_network_input(self.state)
#        self.state_in = self.network_inputs[self.state_str]
        
        if self.is_learning and (random.random() < self.epsilon):
            action = self.state.action_object.random_action(self.state)
        else:
            action = self.state.select_greedy_action(self)
#            action_values = []
#            for checker in self.state.action_object.get_all_checkers():
#                move_outcome = self.state.get_move_outcome(checker)
#                if move_outcome is not None:
#                    move_value = self.get_state_value(move_outcome)
#                    # insert a random number to break the ties
#                    action_values.append(((move_value, random.random()), checker))
#                
#            if len(action_values) > 0:
#                action_values_sorted = sorted(action_values, reverse=True)
#                action = action_values_sorted[0][1]
#            else:
#                action = self.state.action_object.action_forfeit_move
            
        # update values
        
        if self.is_learning:
            s = self.last_state_str
#            s_in = self.last_state_in
            a = self.last_action
            sp = self.state_str
#            sp_in = self.state_in
            ap = action #@UnusedVariable
            
            reward = [0, 0]

            if s is not None:
                # update e
                for key in self.e.iterkeys():
                    self.e[key] *= (self.gamma * self.lamda)
                        
                # replacing traces
                self.e[s] = 1.0
#                # set the trace for the other actions to 0
#                for other_action in Domain.ActionClass.ALL_ACTIONS:
#                    if other_action != a:
#                        self.e[(s, other_action)] = 0
                
                if self.state.is_final():
#                    delta = reward - self.Q.get((s, a), self.default_q)
                    print 'Shouldn\'t happen'
                    delta = reward - self.get_network_value(s)
                else:
#                    delta = reward + self.gamma * self.Q.get((sp, ap), self.default_q) - \
#                            self.Q.get((s, a), self.default_q)
                    delta = [self.gamma * a - b for a, b in
                             zip(self.get_network_value(sp), self.get_network_value(s))]
#                    delta = reward + self.gamma * self.get_network_value(sp_in) - \
#                            self.get_network_value(s_in)
        
                self.update_values(delta)
        
            # save visited state and chosen action
            self.last_state_str = self.state_str
            self.last_state_in = self.state_in
            self.last_action = action
            key = self.last_state_str
            if key not in self.visited_in_episode:
                self.visit_count[key] = self.visit_count.get(key, 0) + 1
            self.visited_in_episode[key] = True
                
        return action

#    def save_knowledge(self):
#        filename = './td-network.txt' % Domain.name
#        f = open(filename, 'w')
#        pickle.dump(self.network, f)
#        f.close()
#
#    def load_knowledge(self):
#        filename = './td-network-%s.txt' % Domain.name
#        f = open(filename, 'r')
#        self.network = pickle.load(f)
#        f.close()
        
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
#        for key in Q_keys:
#            print "Q%s -> %.2f" % (key, self.Q[key])
        for key, value in sorted(self.visit_count.iteritems(), key=lambda (k,v): (v,k)):
            print "%s: %s" % (key, value)
    
    def print_values(self):
        self.print_visit_count()
        self.print_e()
           
if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
   
    filename = exp_params.get_trial_filename(FILE_PREFIX_TD)
    f = open(filename, 'w')

    agent_td1 = AgentTD(exp_params.state_class)
#    agent_td2 = AgentTD()
    if EVAL_OPPONENT == EVAL_OPPONENT_Q_LEARNING:
        agent_opponent = AgentQLearning(exp_params.state_class, load_knowledge = True)
    else:
        agent_opponent = AgentRandom(exp_params.state_class)
    print 'Opponent is: %s' % agent_opponent

    for i in range(TD_NUM_ITERATIONS):
        print 'Iteration %d' % i
        print 'Evaluating against opponent...'

        agent_td1.pause_learning()
#        agent_td2.pause_learning()
        for agent in [agent_td1]:
            game_set = GameSet(exp_params, TD_NUM_EVAL_GAMES,
                               agent, agent_opponent)
            count_wins = game_set.run()
            win_ratio = float(count_wins[0]) / TD_NUM_EVAL_GAMES
            print 'Win ratio against the opponent: %.2f' % win_ratio
            f.write('%d %f\n' % (i, win_ratio))
        agent_td1.resume_learning()        
#        agent_td2.resume_learning()

        print 'Training against self...'
#        game_set = Domain.GameSetClass(NUM_TRAINING_GAMES, agent_td1, agent_td1,
#                                       p, reentry_offset)
        game_set = GameSet(exp_params, TD_NUM_TRAINING_GAMES,
                           agent_td1, agent_td1)
        count_wins = game_set.run()

    f.close()
