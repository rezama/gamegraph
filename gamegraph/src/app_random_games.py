'''
Created on Sep 17, 2012

@author: reza
'''
from common import Experiment, PLAYER_WHITE, GameSet, AgentRandom, PLAYER_BLACK,\
    FOLDER_DOMAINSTATS
from params import NUM_STATS_GAMES, RECORD_GRAPH, SAVE_STATS, COLLECT_STATS

if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
   
    num_games = NUM_STATS_GAMES
    agent_white = AgentRandom(exp_params.state_class)
    agent_black = AgentRandom(exp_params.state_class)
    game_set = GameSet(exp_params, num_games, agent_white, agent_black)

    count_wins = game_set.run()
    total_plies = game_set.get_sum_count_plies()
    
    if RECORD_GRAPH and (exp_params.graph_name is None):
        record_graph = exp_params.state_class.RECORD_GAME_GRAPH
        record_graph.print_stats()
        record_graph.adjust_probs()
        filename = exp_params.get_graph_filename()
#            filename = '../graph/%s-%s' % (exp_params.domain_name, 
#                                           Experiment.get_filename_suffix_no_trial())
        record_graph.save_to_file(filename)
    
    # printing overall stats
    print '----'
    print 'P was: %.2f' % exp_params.p
    print 'Re-entry offset was: %d' % exp_params.offset
    print 'Graph name was: %s' % exp_params.graph_name
        
    if SAVE_STATS:
        # general info
#            filename = '../data/%s-%s-overall-stats.txt' % (domain.name, 
#                                            cls.get_filename_suffix_with_trial())
        filename = exp_params.get_custom_filename_with_trial(FOLDER_DOMAINSTATS,
                                        'overall-stats')
        f = open(filename, 'w')
        
    avg_num_plies_per_game = float(total_plies) / num_games
    print 'Games won by agent: %d, opponent: %d' % (count_wins[PLAYER_WHITE], 
                                                    count_wins[PLAYER_BLACK])
    print 'Average plies per game: %.2f' % avg_num_plies_per_game 
    if SAVE_STATS:
        f.write('Games won by agent: %d, opponent: %d\n' % (count_wins[PLAYER_WHITE],
                                                          count_wins[PLAYER_BLACK]))
        f.write('Average plies per game: %.2f\n' % avg_num_plies_per_game) 
        
    if COLLECT_STATS:
        total_states_visited = len(exp_params.state_class.states_visit_count)
        print 'Total number of states encountered: %d' % total_states_visited
        print 'per 1000 plies: %.2f' % (float(total_states_visited) / 
                                        avg_num_plies_per_game)
        if SAVE_STATS:
            f.write('Total number of states encountered: %d\n' % total_states_visited)
            f.write('per 1000 plies: %.2f\n' % (float(total_states_visited) / 
                                              avg_num_plies_per_game))
        
        avg_visit_count_to_states = sum(exp_params.state_class.states_visit_count.itervalues()) / float(total_states_visited)
        print 'Average number of visits to states: %.2f' % avg_visit_count_to_states
        print 'per 1000 plies: %.2f' % (float(avg_visit_count_to_states) / 
                                        avg_num_plies_per_game)
        if SAVE_STATS:
            f.write('Average number of visits to states: %.2f\n' % avg_visit_count_to_states)
            f.write('per 1000 plies: %.2f\n' % (float(avg_visit_count_to_states) / 
                                              avg_num_plies_per_game))
        
        sum_squared_diffs = sum([(e - avg_visit_count_to_states) ** 2 
                                 for e in exp_params.state_class.states_visit_count.itervalues()])
        var_visit_count_to_states =  sum_squared_diffs / float(total_states_visited) 
        print 'Variance of number of visits to states: %.2f' % var_visit_count_to_states
        if SAVE_STATS:
            f.write('Variance of number of visits to states: %.2f\n' % var_visit_count_to_states)
        
        exp_params.state_class.compute_overall_stats(avg_num_plies_per_game)
        Experiment.save_stats(exp_params.state_class, exp_params)        

    if SAVE_STATS:
        f.close()

