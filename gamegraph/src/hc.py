'''
Created on Dec 9, 2011

@author: reza
'''
from minigammon import Domain

import random
from common import Experiment, PLAYER_WHITE, PLAYER_BLACK, GameSet
#from vanilla_rl import AgentVanillaRL

NUM_GENERATIONS = 500
NUM_CHALLENGE_GAMES = 8
CHALLENGER_NEEDS_TO_WIN = 7
NUM_EVAL_GAMES = 1024
EVALUATE_EVERY = 10

RATIO_KEEP_CHAMPION_WEIGHTS = 0.95
MUTATE_WEIGHT_SIGMA = 0.22 # 0.05

class AgentHC(Domain.AgentNeuralClass):
    
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
        ratio_challenger_weights = 1.0 - RATIO_KEEP_CHAMPION_WEIGHTS
        self.network.params[:] = [RATIO_KEEP_CHAMPION_WEIGHTS * pair[0] +
                                  ratio_challenger_weights * pair[1]
                                  for pair in zip(self.network.params, 
                                                  challenger.network.params)]

    def mutate_challenger(self, challenger):
#        challenger.network.params[:] = [random.gauss(w, w * MUTATE_WEIGHT_SIGMA)
#                                     for w in self.network.params]
        challenger.network.params[:] = [random.gauss(w, MUTATE_WEIGHT_SIGMA)
                                     for w in self.network.params]
    
if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
   
    eval_filename = '../data/trials/hc-%s-%s.txt' % (Domain.name, exp_params.get_file_suffix())
    eval_f = open(eval_filename, 'w')
    chal_filename = '../data/trials/hc-challenge-%s-%s.txt' % (Domain.name, exp_params.get_file_suffix())
    chal_f = open(chal_filename, 'w')
    
    agent_champion = AgentHC();
    agent_challenger = AgentHC();
    agent_opponent = Domain.AgentRandomClass() 
#    agent_opponent = AgentVanillaRL(load_knowledge = True)
    print 'Opponent is: %s' % agent_opponent

    for generation_number in range(NUM_GENERATIONS):
        print 'Generation %d' % generation_number
        
        if generation_number % EVALUATE_EVERY == 0: 
            print 'Evaluating against the opponent...'
            game_set = GameSet(Domain, exp_params, NUM_EVAL_GAMES,
                               agent_champion, agent_opponent)
            count_wins = game_set.run()
            ratio_win = float(count_wins[0]) / NUM_EVAL_GAMES
            print 'Win ratio: %.2f against opponent (out of %d games)' % (
                            ratio_win, NUM_EVAL_GAMES)
            eval_f.write('%d %f\n' % (generation_number, ratio_win))
            eval_f.flush()
        
        print 'Finding a good challenger...'
        found_good_challenger = False
        tries = 1
        while not found_good_challenger:
            # update challenger to have Gaussian distribution around champion
#            print 'Mutating challenger...'
            agent_champion.mutate_challenger(agent_challenger)
            game_set = GameSet(Domain, exp_params, NUM_CHALLENGE_GAMES,
                               agent_champion, agent_challenger)
            count_wins = game_set.run()
#            print 'Challenger won %d out of %d games.' % (count_wins[1], NUM_CHALLENGE_GAMES)
            # if the champion loses more games than the challenger
            if count_wins[PLAYER_BLACK] >= CHALLENGER_NEEDS_TO_WIN:
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
