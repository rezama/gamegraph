'''
Created on Aug 22, 2012

@author: reza
'''
from minigammon import Domain

from common import Experiment
from state_graph import StateGraph

class GraphManipulator(object):
    
    @classmethod
    def load_graph(cls, exp_params):
        graph_file = '../graph/%s-%s' % (Domain.name, exp_params.get_file_suffix_no_trial())
        g = StateGraph.load_from_file(graph_file)
        return g

    @classmethod
    def generate_graph(cls, exp_params):
        g = Domain.StateClass.generate_graph(exp_params)
        graph_file = '../graph/%s-%s' % (Domain.name, exp_params.get_file_suffix_no_trial())
        g.print_stats()
        g.save_to_file(graph_file)
        return g

    @classmethod
    def trim_all_legible_back_edges(cls, exp_params, g):
        new_graph_file = '../graph/%s-%s-nocycle' % (Domain.name, exp_params.get_file_suffix_no_trial())
        g.compute_bfs()
        g.trim_back_edges()
        g.cleanup_attrs()
        g.save_to_file(new_graph_file)

    @classmethod
    def trim_all_legible_hit_edges(cls, exp_params, g):
        new_graph_file = '../graph/%s-%s-nohit' % (Domain.name, exp_params.get_file_suffix_no_trial())
        g.trim_hit_edges()
        g.save_to_file(new_graph_file)

    @classmethod
    def create_ergo_range(cls, exp_params, g):
        g.compute_bfs()

        keep_probs = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
#        keep_probs = [1.0, 0.8, 0.5, 0.2, 0.0]
        keep_probs_inc = []
        currently_kept = 1.0
        for p in keep_probs:
            must_keep_inc = p / currently_kept
            keep_probs_inc.append(must_keep_inc)
            currently_kept = p
#        print 'Going to trim back edges by these percentages:'
#        print keep_probs_inc
        
        for i in range(len(keep_probs)):
            new_graph_file = '../graph/%s-%s-ergo%d' % (Domain.name, 
                    exp_params.get_file_suffix_no_trial(), keep_probs[i] * 100)
            g.trim_back_edges(keep_probs_inc[i])
            g.save_to_file(new_graph_file)
            print ''

if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
    g = GraphManipulator.generate_graph(exp_params)
#    GraphManipulator.trim_all_legible_hit_edges(exp_params, g)
    GraphManipulator.trim_all_legible_back_edges(exp_params, g)
#    g.print_back_edges()
#    g = GraphManipulator.load_graph(exp_params)
#    GraphManipulator.create_ergo_range(exp_params, g)
    
