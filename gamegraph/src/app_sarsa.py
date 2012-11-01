'''
Created on Dec 10, 2011

@author: reza
'''

import random
import pickle

from common import Experiment, FILE_PREFIX_SARSA, FOLDER_QTABLE_VS_SELF,\
    FOLDER_QTABLE_VS_RANDOM, ExpParams
from params import SARSA_EPSILON, SARSA_LAMBDA, SARSA_ALPHA, SARSA_GAMMA,\
    SARSA_USE_ALPHA_ANNEALING, SARSA_MIN_ALPHA, SARSA_TRAIN_AGAINST_SELF,\
    SARSA_NUM_TRAINING_ITERATIONS, SARSA_SAVE_TABLES, SARSA_NUM_EVAL_EPISODES,\
    SARSA_NUM_EPISODES_PER_ITERATION
from domain import Agent, AgentRandom, Game, GameSet

class AgentSarsa(Agent):

    def __init__(self, state_class, load_knowledge = False):
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
            action = state.action_object.random_action(state)
        else:
            do_choose_roll = False
            if state.exp_params.choose_roll > 0.0:
                r = random.random()
                if r < state.exp_params.choose_roll:
                    do_choose_roll = True

            done = False
            while not done:
                roll_range = [state.roll]
                if do_choose_roll:
                    roll_range = state.die_object.get_all_sides()
                
                action_values = []
    
                for replace_roll in roll_range:
                    state.roll = replace_roll
                    self.state_str = str(state)
                    for checker in state.action_object.get_all_checkers():
                        move_outcome = state.get_move_outcome(checker)
                        if move_outcome is not None:
                            move_value = self.Q.get((self.state_str, checker), self.default_q)
                            # insert a random number to break the ties
                            action_values.append(((move_value, random.random()), (replace_roll, checker)))
                    
                if len(action_values) > 0:
                    action_values_sorted = sorted(action_values, reverse=True)
                    best_roll = action_values_sorted[0][1][0]
                    # set the best roll there
                    state.roll = best_roll
                    self.state_str = str(state)
                    action = action_values_sorted[0][1][1]
                else:
                    action = state.action_object.action_forfeit_move
        
                if (action != self.state.action_object.action_forfeit_move) or self.state.can_forfeit_move():
                    done = True
                else:
                    self.state.re_roll_dice()

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
                for other_action in state.action_object.get_all_actions():
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
                alpha = max(alpha, SARSA_MIN_ALPHA)
            if self.e[(si, ai)] != 0.0:
                change = alpha * delta * self.e[(si, ai)]
                self.Q[(si, ai)] = self.Q.get((si, ai), self.default_q) + change
                        
    
    def get_knowledge_filename(self):
        exp_params = ExpParams.get_exp_params_from_command_line_args()
        if SARSA_TRAIN_AGAINST_SELF:
            table_folder = FOLDER_QTABLE_VS_SELF
        else:
            table_folder = FOLDER_QTABLE_VS_RANDOM
        filename = exp_params.get_custom_filename_no_trial(table_folder,
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
    exp_params = ExpParams.get_exp_params_from_command_line_args()
   
    filename = exp_params.get_trial_filename(FILE_PREFIX_SARSA)
    f = open(filename, 'w')

    agent_sarsa = AgentSarsa(exp_params.state_class)
    if SARSA_TRAIN_AGAINST_SELF:
        agent_opponent = AgentSarsa(exp_params.state_class)
#        # use this for evaluating against pre-trained version of self:
#        agent_opponent = AgentSarsa(exp_params.state_class, load_knowledge = True) 
    else:
        agent_opponent = AgentRandom(exp_params.state_class)
    agent_eval = Experiment.create_eval_opponent_agent(exp_params)
    print 'Training opponent is: %s' % agent_opponent
    print 'Evaluation opponent is: %s' % agent_eval

    for i in range(SARSA_NUM_TRAINING_ITERATIONS):
        print 'Iteration %d' % i
        print 'Evaluating (%d games)...' % SARSA_NUM_EVAL_EPISODES

        agent_sarsa.pause_learning()
        game_set = GameSet(exp_params, SARSA_NUM_EVAL_EPISODES,
                           agent_sarsa, agent_eval)
        agent_sarsa.resume_learning()
        count_wins = game_set.run()
        win_rate = float(count_wins[0]) / SARSA_NUM_EVAL_EPISODES
        print 'Win rate against the opponent: %.2f' % win_rate
        f.write('%d %f\n' % (i * SARSA_NUM_EPISODES_PER_ITERATION, win_rate))
        agent_sarsa.resume_learning()

        print 'Training (%d games)...' % SARSA_NUM_EPISODES_PER_ITERATION
#        # when training for benchmark, have the RL agent play as black
#        game_set = Domain.GameSetClass(NUM_ITERATIONS, agent_eval, agent_sarsa, 
#                                       p, reentry_offset,
#                                       print_learning_progress = True)
        game_set = GameSet(exp_params, SARSA_NUM_EPISODES_PER_ITERATION,
                           agent_sarsa, agent_opponent)
        count_wins = game_set.run()
        print 'Win rate in training: %.2f' % (float(count_wins[0]) /
                                              SARSA_NUM_EPISODES_PER_ITERATION)
    
#    agent_sarsa.algorithm.print_values()
    if SARSA_SAVE_TABLES and exp_params.is_first_trial():
        print 'Saving RL table...'
        agent_sarsa.algorithm.save_knowledge()

#    if SARSA_SAVE_STATE_VALUES_IN_GRAPH and exp_params.is_graph_based() and \
#                exp_params.is_first_trial():
#        print 'Saving state values in graph...'
#        exp_params.domain.StateClass.copy_state_values_to_graph(exp_params, agent_sarsa)
    
