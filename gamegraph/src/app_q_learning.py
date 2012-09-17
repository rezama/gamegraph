'''
Created on Dec 10, 2011

@author: reza
'''
from minigammon import Domain

import random
from common import Experiment, Game, GameSet, FILE_PREFIX_Q_LEARNING, \
    FOLDER_QTABLE_VS_SELF, FOLDER_QTABLE_VS_RANDOM
import pickle
from params import Q_EPSILON, Q_LAMBDA, Q_ALPHA, Q_GAMMA,\
    Q_LEARNING_USE_ALPHA_ANNEALING, Q_LEARNING_MIN_ALPHA, Q_LEARNING_TRAIN_AGAINST_SELF,\
    Q_LEARNING_SAVE_TRIAL_DATA, Q_LEARNING_NUM_ITERATIONS, Q_LEARNING_SAVE_TABLES,\
    Q_LEARNING_SAVE_STATE_VALUES_IN_GRAPH, Q_LEARNING_NUM_FINAL_EVAL

class AgentQLearning(Domain.AgentClass):

    def __init__(self, load_knowledge = False):
        super(AgentQLearning, self).__init__()
        self.algorithm = SarsaLambda()

        if load_knowledge:
            self.algorithm.load_knowledge()
            self.algorithm.is_learning = False

    def begin_episode(self):
        self.algorithm.begin_episode(self.state)
        
    def end_episode(self, reward):
        self.algorithm.end_episode(self.state, reward)

    def select_action(self):
        return self.algorithm.select_action(self.state)
    
    def get_board_value(self, board_str):
        return self.algorithm.get_board_value(board_str)
    
    def pause_learning(self):
        self.algorithm.pause_learning()

    def resume_learning(self):
        self.algorithm.resume_learning()
    
#    def save_learning_state(self):
#        if self.algorithm is not None:
#            self.algorithm.save_learning_state()
#
#    def restore_learning_state(self):
#        if self.algorithm is not None:
#            self.algorithm.restore_learning_state()
#
#    def reset_learning(self):
#        if self.algorithm is not None:
#            self.algorithm.reset_learning()

class SarsaLambda(object):

    def __init__(self):
        self.epsilon = Q_EPSILON
        self.lamda = Q_LAMBDA
        self.alpha = Q_ALPHA
        self.gamma = Q_GAMMA
        
        self.state_str = None
        self.last_state_str = None
        self.last_action = None
        
        self.is_learning = True
        self.Q = {}
        self.Q_save = {}
        self.e = {}
        self.visit_count = {}
        
        self.default_q = Game.get_max_episode_reward() #* 1.1
        
    def begin_episode(self, state):
        self.e = {}
        self.state_str = None
        self.last_state_str = None
        self.last_action = None
        
    def end_episode(self, state, reward):
        if self.is_learning:
            s = self.last_state_str
            a = self.last_action
            
            delta = reward - self.Q.get((s, a), self.default_q)
    
            self.update_values(delta)
    
    def select_action(self, state):
        self.state_str = str(state)
        
        if self.is_learning and (random.random() < self.epsilon):
            action = Domain.ActionClass.random_action(state)
        else:
            action_values = []
            for checker in Domain.ActionClass.ALL_CHECKERS:
                move_outcome = state.get_move_outcome(checker)
                if move_outcome is not None:
                    move_value = self.Q.get((self.state_str, checker), self.default_q)
                    # insert a random number to break the ties
                    action_values.append(((move_value, random.random()), checker))
                
            if len(action_values) > 0:
                action_values_sorted = sorted(action_values, reverse=True)
                action = action_values_sorted[0][1]
            else:
                action = Domain.ActionClass.ACTION_FORFEIT_MOVE
            
        # update values
        
        if self.is_learning:
            s = self.last_state_str
            a = self.last_action
            sp = self.state_str
            ap = action
            
            reward = 0

            if s is not None:
                # update e
                for key in self.e.iterkeys():
                    self.e[key] *= (self.gamma * self.lamda)
                        
                # replacing traces
                self.e[(s, a)] = 1.0
                # set the trace for the other actions to 0
                for other_action in Domain.ActionClass.ALL_ACTIONS:
                    if other_action != a:
                        self.e[(s, other_action)] = 0
                
                
                if state.is_final():
                    delta = reward - self.Q.get((s, a), self.default_q)
                else:
                    delta = reward + self.gamma * self.Q.get((sp, ap), self.default_q) - \
                            self.Q.get((s, a), self.default_q)
        
                self.update_values(delta)
        
            # save visited state and chosen action
            self.last_state_str = self.state_str
            self.last_action = action
            key = (self.last_state_str, self.last_action)
            self.visit_count[key] = self.visit_count.get(key, 0) + 1
                
        return action

    def get_board_value(self, board_str):
        INVALID_ACTION_VALUE = -2
        sum_values = 0.0
        count = 0
        for roll in Domain.DieClass.SIDES:
            state_str = board_str + ('-%d' % roll)
            action_values = []
            for action in Domain.ActionClass.ALL_ACTIONS:
                action_value = self.Q.get((state_str, action), INVALID_ACTION_VALUE)
                # insert a random number to break the ties
                action_values.append(((action_value, random.random()), action))
                
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
            if Q_LEARNING_USE_ALPHA_ANNEALING:
                alpha = 1.0 / self.visit_count.get((si, ai), 1)
                alpha = max(alpha, Q_LEARNING_MIN_ALPHA)
            if self.e[(si, ai)] != 0.0:
                change = alpha * delta * self.e[(si, ai)]
                self.Q[(si, ai)] = self.Q.get((si, ai), self.default_q) + change
                        
    
    def get_knowledge_filename(self):
        exp_params = Experiment.get_command_line_args()
        if Q_LEARNING_TRAIN_AGAINST_SELF:
            table_folder = FOLDER_QTABLE_VS_SELF
        else:
            table_folder = FOLDER_QTABLE_VS_RANDOM
        filename = exp_params.get_custom_filename_no_trial(table_folder,
                                                FILE_PREFIX_Q_LEARNING, Domain.name)
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

#    def save_learning_state(self):
#        self.Q_save = copy.deepcopy(self.Q)
#        
#    def restore_learning_state(self):
#        self.Q = copy.deepcopy(self.Q_save)

    def print_Q(self):
        Q_keys = self.Q.keys()
        Q_keys.sort()
        print "Q:"
#        for key in Q_keys:
#            print "Q%s -> %.2f" % (key, self.Q[key])
        for key, value in sorted(self.Q.iteritems(), key=lambda (k,v): (v,k)):
            print "%s: %s" % (key, value)
            
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
        self.print_Q()
        
if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
   
#    random.seed(0)
    agent_q_learning = AgentQLearning()
    if Q_LEARNING_TRAIN_AGAINST_SELF:
        agent_opponent = AgentQLearning()
    else:
        agent_opponent = Domain.AgentRandomClass()
    # use this for evaluating against pre-trained version of self:
#    agent_opponent = AgentQLearning(load_knowledge = True) 

    # when training for benchmark, have the RL agent play as black
#    game_set = Domain.GameSetClass(NUM_ITERATIONS, agent_opponent, agent_q_learning, 
#                                   p, reentry_offset,
#                                   print_learning_progress = True)
    if Q_LEARNING_SAVE_TRIAL_DATA:
#        progress_filename = '../data/trials/rl-%s-%s.txt' % (Domain.name, 
#                                                exp_params.get_filename_suffix_with_trial())
        progress_filename = exp_params.get_trial_filename(FILE_PREFIX_Q_LEARNING, 
                                                          Domain.name)
    else:
        progress_filename = None
    print 'Opponent is: %s' % agent_opponent
    game_set = GameSet(Domain, exp_params, Q_LEARNING_NUM_ITERATIONS,
                       agent_q_learning, agent_opponent, 
                       print_learning_progress = True,
                       progress_filename = progress_filename)
    count_wins = game_set.run()
#    print 'Won %d out of %d games against random agent.' % (
#                    count_wins[1], NUM_ITERATIONS)
    print 'Win ratio: %.2f against the opponent.' % (float(count_wins[0]) / 
                                                     Q_LEARNING_NUM_ITERATIONS)
    
#    agent_q_learning.algorithm.print_values()
    if Q_LEARNING_SAVE_TABLES and exp_params.is_first_trial():
        print 'Saving RL table...'
        agent_q_learning.algorithm.save_knowledge()

    if Q_LEARNING_SAVE_STATE_VALUES_IN_GRAPH and exp_params.is_graph_based() and \
                exp_params.is_first_trial():
        print 'Saving state values in graph...'
        Domain.StateClass.copy_state_values_to_graph(exp_params, agent_q_learning)
    
    if Q_LEARNING_TRAIN_AGAINST_SELF:
        # evaluate against random
        agent_q_learning.pause_learning()
        agent_opponent = Domain.AgentRandomClass()
        game_set = GameSet(Domain, exp_params, Q_LEARNING_NUM_FINAL_EVAL,
                           agent_q_learning, agent_opponent)
        count_wins = game_set.run()
    #    print 'Won %d out of %d games against random agent.' % (
    #                    count_wins[1], NUM_ITERATIONS)
        print 'Win ratio: %.2f against the opponent.' % (float(count_wins[0]) / 
                                                         Q_LEARNING_NUM_FINAL_EVAL)

