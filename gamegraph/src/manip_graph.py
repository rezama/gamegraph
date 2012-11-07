'''
Created on Aug 22, 2012

@author: reza
'''
from common import FOLDER_GRAPH, ExpParams, VAL_ATTR
from state_graph import StateGraph
from params import EXP_BACK_RANGE
import os

class ManipGraph(object):
    
    @classmethod
    def create_back_range(cls, exp_params):
        g = StateGraph.load(exp_params)
        g.compute_bfs()
#        prob_keep_range = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
        prob_keep_range = [x / 100.0 for x in EXP_BACK_RANGE]
        prob_keep_range_inc = []
        currently_kept = 1.0
        for p in prob_keep_range:
            must_keep_inc = p / currently_kept
            prob_keep_range_inc.append(must_keep_inc)
            currently_kept = p
#        print 'Going to trim back edges by these percentages:'
#        print prob_keep_range_inc
        
        for i in range(len(prob_keep_range)):
            filename_suffix = '-back-%d' % (prob_keep_range[i] * 100)
            g.trim_back_edges(prob_keep_range_inc[i])
            g.save(exp_params, filename_suffix)
            print ''

    @classmethod
    def get_all_graphs_infos(cls):
        for (dirpath, dirname, filenames) in os.walk(FOLDER_GRAPH): #@UnusedVariable
            for filename in filenames:
                if '.gz' in filename:
                    graph_name = filename.replace('.gz', '') # remove .gz extension
                    domain_name = filename.split('-', 1)[0]
                    options_list = ['--domain', domain_name, '--graph', graph_name] 
                    exp_params = ExpParams.get_exp_params(options_list)
                    g = StateGraph.load(exp_params)
                    g.print_stats()
            break

if __name__ == '__main__':
    exp_params = ExpParams.get_exp_params_from_command_line_args()
    StateGraph.print_graph_info(exp_params)
#    ManipGraph.create_back_range(exp_params)
#    ManipGraph.get_all_graphs_infos()
    
