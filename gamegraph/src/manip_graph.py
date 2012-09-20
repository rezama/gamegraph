'''
Created on Aug 22, 2012

@author: reza
'''
from common import Experiment
from state_graph import StateGraph

class GraphManipulator(object):
    
    @classmethod
    def trim_back_edges(cls, exp_params, g, prob_keep = 0.0):
        new_graph_filename = exp_params.get_graph_filename() + \
                ('-%dback' % (prob_keep * 100))
        g.compute_bfs()
        g.trim_back_edges(prob_keep)
        g.cleanup_attrs()
        g.save_to_file(new_graph_filename)

#    @classmethod
#    def trim_hit_edges(cls, exp_params, g, prob_keep = 0.0):
#        new_graph_filename = exp_params.get_graph_filename() + \
#                ('-%dhit' % (prob_keep * 100))
#        g.trim_hit_edges(prob_keep)
#        g.save_to_file(new_graph_filename)

    @classmethod
    def create_back_range(cls, exp_params, g):
        g.compute_bfs()

#        prob_keep_range = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
        prob_keep_range = [1.0, 0.85, 0.5, 0.15, 0.0]
        prob_keep_range_inc = []
        currently_kept = 1.0
        for p in prob_keep_range:
            must_keep_inc = p / currently_kept
            prob_keep_range_inc.append(must_keep_inc)
            currently_kept = p
#        print 'Going to trim back edges by these percentages:'
#        print prob_keep_range_inc
        
        for i in range(len(prob_keep_range)):
            filename_suffix = '-%dback' % (prob_keep_range[i] * 100)
            g.trim_back_edges(prob_keep_range_inc[i])
            g.save(exp_params, filename_suffix)
            print ''

#    @classmethod
#    def create_hit_range(cls, exp_params, g):
#        g.compute_bfs()
#
##        prob_keep_range = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
#        prob_keep_range = [1.0, 0.85, 0.5, 0.15, 0.0]
#        prob_keep_range_inc = []
#        currently_kept = 1.0
#        for p in prob_keep_range:
#            must_keep_inc = p / currently_kept
#            prob_keep_range_inc.append(must_keep_inc)
#            currently_kept = p
##        print 'Going to trim back edges by these percentages:'
##        print prob_keep_range_inc
#        
#        for i in range(len(prob_keep_range)):
#            filename_suffix = '-%dhit' % (prob_keep_range[i] * 100)
#            g.trim_back_edges(prob_keep_range_inc[i])
#            g.save(exp_params, filename_suffix)
#            print ''

if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()

    g = StateGraph.load(exp_params)
    g.compute_bfs()
    g.value_iteration(exp_params)
#    g.print_all_edges()
    
#    GraphManipulator.create_back_range(exp_params, g)

#    g = GraphManipulator.generate_graph(exp_params)
##    g = GraphManipulator.load_graph(exp_params)
#    GraphManipulator.trim_back_edges(exp_params, g)

#    g = GraphManipulator.generate_graph(exp_params)
#    g = GraphManipulator.load_graph(exp_params)
#    GraphManipulator.create_back_range(exp_params, g)
#    g = GraphManipulator.load_graph(exp_params)
#    GraphManipulator.create_hit_range(exp_params, g)
    
#    g = GraphManipulator.load_graph(exp_params)
#    g.compute_bfs()
#    g.print_all_edges()

#    g = GraphManipulator.generate_graph(exp_params)
#    GraphManipulator.trim_back_edges(exp_params, g)
#    g = GraphManipulator.generate_graph(exp_params)
#    GraphManipulator.trim_back_edges(exp_params, g, 0.5)
#    g = GraphManipulator.generate_graph(exp_params)
#    GraphManipulator.trim_hit_edges(exp_params, g)
#    g = GraphManipulator.generate_graph(exp_params)
#    GraphManipulator.trim_hit_edges(exp_params, g, 0.5)
