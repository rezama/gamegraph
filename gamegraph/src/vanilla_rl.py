'''
Created on Dec 10, 2011

@author: reza
'''
from midgammon import Domain

import random
from common import Experiment
import pickle

GAMMA = 1.0
ALPHA = 0.1
EPSILON = 0.05
LAMBDA = 0.90

USE_ALPHA_ANNEALING = True
MIN_ALPHA = 0.05

NUM_ITERATIONS = 1024 * 200
NUM_FINAL_EVAL = 1024

TRAIN_AGAINST_SELF = False
SAVE_TABLES = False
SAVE_TRAINING_STATS = True

class AgentVanillaRL(Domain.AgentClass):

    def __init__(self, load_knowledge = False):
        super(AgentVanillaRL, self).__init__()
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
    
    def pause_learning(self):
        if self.algorithm is not None:
            self.algorithm.pause_learning()

    def resume_learning(self):
        if self.algorithm is not None:
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
        self.epsilon = EPSILON
        self.lamda = LAMBDA
        self.alpha = ALPHA
        self.gamma = GAMMA
        
        self.state_str = None
        self.last_state_str = None
        self.last_action = None
        
        self.is_learning = True
        self.Q = {}
        self.Q_save = {}
        self.e = {}
        self.visit_count = {}
        
        self.default_q = Domain.GameClass.get_max_episode_reward() #* 1.1
        
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

    def update_values(self, delta):
        alpha = self.alpha
        for (si, ai) in self.e.iterkeys():
            if USE_ALPHA_ANNEALING:
                alpha = 1.0 / self.visit_count.get((si, ai), 1)
                alpha = max(alpha, MIN_ALPHA)
            if self.e[(si, ai)] != 0.0:
                change = alpha * delta * self.e[(si, ai)]
                self.Q[(si, ai)] = self.Q.get((si, ai), self.default_q) + change
                        
    
    def save_knowledge(self):
        if TRAIN_AGAINST_SELF:
            tabledir = 'vsself'
        else:
            tabledir = 'vsrandom'
        filename = '../rl-table/%s/%s-%s.txt' % (tabledir, Domain.name,
                                                 Experiment.get_file_suffix())
        f = open(filename, 'w')
        pickle.dump(self.Q, f)
        f.close()

    def load_knowledge(self):
        if TRAIN_AGAINST_SELF:
            tabledir = 'vsself'
        else:
            tabledir = 'vsrandom'
        filename = '../rl-table/%s/%s-%s.txt' % (tabledir, Domain.name, 
                                                 Experiment.get_file_suffix())
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
    (p, reentry_offset, graph_name) = Experiment.get_command_line_args()
   
#    random.seed(0)
    agent_rl = AgentVanillaRL()
    if TRAIN_AGAINST_SELF:
        agent_opponent = AgentVanillaRL()
    else:
        agent_opponent = Domain.AgentRandomClass()
    # use this for evaluating against pre-trained version of self:
#    agent_opponent = AgentVanillaRL(load_knowledge = True) 

    # when training for benchmark, have the RL agent play as black
#    game_set = Domain.GameSetClass(NUM_ITERATIONS, agent_opponent, agent_rl, 
#                                   p, reentry_offset,
#                                   print_learning_progress = True)
    if SAVE_TRAINING_STATS:
        progress_filename = '../data/rl/rl-%s-%s.txt' % (Domain.name, Experiment.get_file_suffix())
    else:
        progress_filename = None
    print 'Opponent is: %s' % agent_opponent
    game_set = Domain.GameSetClass(NUM_ITERATIONS, agent_rl, agent_opponent, 
                                   p, reentry_offset, graph_name,
                                   print_learning_progress = True,
                                   progress_filename = progress_filename)
    count_wins = game_set.run()
#    print 'Won %d out of %d games against random agent.' % (
#                    count_wins[1], NUM_ITERATIONS)
    print 'Won ratio: %.2f against the opponent.' % (float(count_wins[0]) / NUM_ITERATIONS)
    
    
#    # evaluate against random
#    agent_rl.pause_learning()
#    agent_opponent = Domain.AgentRandomClass()
#    game_set = Domain.GameSetClass(NUM_FINAL_EVAL, agent_rl, agent_opponent, 
#                                   p, reentry_offset)
#    count_wins = game_set.run()
##    print 'Won %d out of %d games against random agent.' % (
##                    count_wins[1], NUM_ITERATIONS)
#    print 'Won ratio: %.2f against the opponent.' % (float(count_wins[0]) / NUM_FINAL_EVAL)

    if SAVE_TABLES:
        agent_rl.algorithm.save_knowledge()
#    agent_rl.algorithm.print_values()
