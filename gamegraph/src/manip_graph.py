'''
Created on Aug 22, 2012

@author: reza
'''
from midgammon import Domain

from common import Experiment

class GraphManipulator(object):
    
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
        g.print_stats()
        g.compute_bfs()
        g.trim_back_edges()
        g.cleanup_attrs()
        g.save_to_file(new_graph_file)

    @classmethod
    def create_ergo_range(cls, exp_params, g):
        g.compute_bfs()

        keep_probs = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
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
#            g.print_stats()
            g.save_to_file(new_graph_file)
            print ''

if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
    g = GraphManipulator.generate_graph(exp_params)
    GraphManipulator.create_ergo_range(exp_params, g)
    
