'''
Created on Dec 5, 2011

@author: reza
'''

from minigammon import Domain

from common import NUM_STATS_GAMES, Experiment
from state_graph import StateGraph

if __name__ == '__main__':
    (p, reentry_offset) = Experiment.get_command_line_args()
    
    num_games = NUM_STATS_GAMES
    agent_white = Domain.AgentRandomClass()
    agent_black = Domain.AgentRandomClass()
    game_set = Domain.GameSetClass(num_games, agent_white, agent_black,
                                   p, reentry_offset)
    count_wins = game_set.run()
    total_plies = game_set.get_sum_count_plies()
    
    # printing overall stats
    print '----'
    print 'P was: %.2f' % p
    print 'Re-entry offset was: %d' % reentry_offset
    
    avg_num_plies_per_game = float(total_plies) / num_games
    print 'Games won by White: %d, Black: %d' % (count_wins[Domain.StateClass.PLAYER_WHITE], count_wins[Domain.StateClass.PLAYER_BLACK])
    print 'Average plies per game: %.2f' % avg_num_plies_per_game 
    
