'''
Created on Aug 22, 2012

@author: reza
'''
from midgammon import Domain

from state_graph import StateGraph
from common import Experiment

class GraphManipulator(object):
    
    @classmethod
    def generate_graph(cls, exp_params):
        g = Domain.StateClass.generate_graph(exp_params)
        graph_file = '../graph/%s-%s' % (Domain.name, exp_params.get_file_suffix_no_trial())
        g.print_stats()
        g.save_to_file(graph_file)

    @classmethod
    def test_remove_cycles(cls):
        g = StateGraph.load_from_file('../graph/minigammon-graph-offset-0')
        g.print_stats()
        g.compute_bfs()
        g.remove_back_edges()
        g.print_stats()
        g.save_to_file('../graph/minigammon-graph-offset-0-nocycle')
        
if __name__ == '__main__':
    exp_params = Experiment.get_command_line_args()
    GraphManipulator.generate_graph(exp_params)
    
#    s = m.graph.get_node_id('1-3949')
#    print m.graph.successors[s]
#    successors = m.graph.get_all_successors(s)
#    print successors
#    for successor in successors:
#        print m.graph.get_node_name(successor)
#
#    for sink in m.graph.sinks[PLAYER_WHITE] + m.graph.sinks[PLAYER_BLACK]:
#        print 'sink %s, d: %d' % (m.graph.get_node_name(sink),
#                             m.graph.get_attr(sink, 'd'))
#    count_ok = 0
#    count_bad = 0
#    for n in range(len(m.graph.node_names)):
#        if m.graph.get_attr(n, 'd') < 0:
#            count_bad += 1
#            print 'node %s, d: %d, color: %s, succ: %s' % (m.graph.get_node_name(n),
#                                 m.graph.get_attr(n, 'd'), m.graph.get_attr(n, 'color'),
#                                 m.graph.successors[n])
#        else:
#            count_ok += 1
#        
#    print 'Count OK: %d, Count Bad: %d' % (count_ok, count_bad)
