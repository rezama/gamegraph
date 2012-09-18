'''
Created on Dec 9, 2011

@author: reza
'''

import random
from common import Experiment, PLAYER_WHITE, PLAYER_BLACK, GameSet,\
    FILE_PREFIX_HC, FILE_PREFIX_HC_CHALLENGE, AgentNeural, AgentRandom
from params import HC_RATIO_KEEP_CHAMPION_WEIGHTS, HC_MUTATE_WEIGHT_SIGMA,\
    HC_NUM_GENERATIONS, HC_EVALUATE_EVERY_N_GENERATIONS, HC_NUM_EVAL_GAMES,\
    HC_NUM_CHALLENGE_GAMES, HC_CHALLENGER_NEEDS_TO_WIN, EVAL_OPPONENT,\
    EVAL_OPPONENT_Q_LEARNING
from app_q_learning import AgentQLearning

class AgentHC(AgentNeural):
    
    def __init__(self):
        super(AgentHC, self).__init__(1, init_weights = 0.0)
        self.network_inputs = {}

    def get_state_value(self, state):
        state_str = str(state)[:-2]
        if state_str not in self.network_inputs:
            self.network_inputs[state_str] = self.encode_network_input(state)
        network_in = self.network_inputs[state_str]
        network_out = self.network.activate(network_in)
        # if player to move is white, it means black is considering
        # a move outcome, so black is evaluating the position
        if state.player_to_move == PLAYER_WHITE:
            multiplier = -1.0
        else:
            multiplier = 1.0
        return multiplier * network_out[0]
    
    def move_weights_toward(self, challenger):
        ratio_challenger_weights = 1.0 - HC_RATIO_KEEP_CHAMPION_WEIGHTS
        self.network.params[:] = [HC_RATIO_KEEP_CHAMPION_WEIGHTS * pair[0] +
                                  ratio_challenger_weights * pair[1]
                                  for pair in zip(self.network.params, 
                                                  challenger.network.params)]

    def mutate_challenger(self, challenger):
#        challenger.network.params[:] = [random.gauss(w, w * MUTATE_WEIGHT_SIGMA)
#                                     for w in self.network.params]
        challenger.network.params[:] = [random.gauss(w, HC_MUTATE_WEIGHT_SIGMA)
                                     for w in self.network.params]
    
if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
   
    eval_filename = exp_params.get_trial_filename(FILE_PREFIX_HC)
    eval_f = open(eval_filename, 'w')
    chal_filename = exp_params.get_trial_filename(FILE_PREFIX_HC_CHALLENGE)
    chal_f = open(chal_filename, 'w')
    
    agent_champion = AgentHC();
    agent_challenger = AgentHC();
    if EVAL_OPPONENT == EVAL_OPPONENT_Q_LEARNING:
        agent_opponent = AgentQLearning(exp_params.state_class, load_knowledge = True)
    else:
        agent_opponent = AgentRandom(exp_params.state_class)
    print 'Opponent is: %s' % agent_opponent

    for generation_number in range(HC_NUM_GENERATIONS):
        print 'Generation %d' % generation_number
        
        if generation_number % HC_EVALUATE_EVERY_N_GENERATIONS == 0: 
            print 'Evaluating against the opponent...'
            game_set = GameSet(exp_params, HC_NUM_EVAL_GAMES,
                               agent_champion, agent_opponent)
            count_wins = game_set.run()
            ratio_win = float(count_wins[0]) / HC_NUM_EVAL_GAMES
            print 'Win ratio: %.2f against opponent (out of %d games)' % (
                            ratio_win, HC_NUM_EVAL_GAMES)
            eval_f.write('%d %f\n' % (generation_number, ratio_win))
            eval_f.flush()
        
        print 'Finding a good challenger...'
        found_good_challenger = False
        tries = 1
        while not found_good_challenger:
            # update challenger to have Gaussian distribution around champion
#            print 'Mutating challenger...'
            agent_champion.mutate_challenger(agent_challenger)
            game_set = GameSet(exp_params, HC_NUM_CHALLENGE_GAMES,
                               agent_champion, agent_challenger)
            count_wins = game_set.run()
#            print 'Challenger won %d out of %d games.' % (count_wins[1], NUM_CHALLENGE_GAMES)
            # if the champion loses more games than the challenger
            if count_wins[PLAYER_BLACK] >= HC_CHALLENGER_NEEDS_TO_WIN:
                found_good_challenger = True
                print 'Found with %d tries' % tries
                chal_f.write('%d %d\n' % (generation_number, tries))
                chal_f.flush()

                print 'Updating champion weights...'
                agent_champion.move_weights_toward(agent_challenger)
            tries += 1

        print '--'
        
    eval_f.close()
    chal_f.close()
