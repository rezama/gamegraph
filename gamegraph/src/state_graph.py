'''
Created on Jun 25, 2012

@author: reza
'''
from common import PLAYER_WHITE, PLAYER_BLACK
import random
import pickle

class StateGraph(object):

    def __init__(self, all_actions, all_rolls, roll_offset = 1):
        self.successors = []
        self.node_names = []
        self.node_attrs = []
        self.node_ids = {}
#        self.sources = {PLAYER_WHITE: [], PLAYER_BLACK: []}
#        self.sinks = {PLAYER_WHITE: [], PLAYER_BLACK: []}
        self.sources = [[], []]
        self.sinks = [[], []]
        self.all_actions = all_actions
        self.all_rolls = all_rolls
        self.roll_offset = roll_offset
                
    def get_random_source(self, player_to_start):
        return random.choice(self.sources[player_to_start])
        
    def get_transition_outcome(self, node_id, roll, action):
        next_node_id = None
        try:
            targets = self.successors[node_id][roll - self.roll_offset][action]
            p = random.random()
            sum_prob = 0.0
            for (target_id, prob) in targets.iteritems():
                sum_prob += prob
                if sum_prob > p:
                    next_node_id = target_id
                    break
        except KeyError:
            pass
        return next_node_id

    def set_as_source(self, node_id, player):
        if node_id not in self.sources[player]:
            self.sources[player].append(node_id)
    
    def set_as_sink(self, node_id, player):
        if node_id not in self.sinks[player]:
            self.sinks[player].append(node_id)
    
    def is_sink(self, node):
        return (node in self.sinks[PLAYER_WHITE]) or \
               (node in self.sinks[PLAYER_BLACK])
    
    def get_sink_color(self, node_id):
        if node_id in self.sinks[PLAYER_WHITE]:
            return PLAYER_WHITE
        elif node_id in self.sinks[PLAYER_BLACK]:
            return PLAYER_BLACK
        else:
            return None
    
    def add_node(self, node_name):
        if node_name not in self.node_names:
            node_id = len(self.node_names)
            self.node_names.append(node_name)
            self.node_attrs.append({})
            self.node_ids[node_name] = node_id            
            self.successors.append([])
            for roll in self.all_rolls:
                self.successors[node_id].append([])
                for action in self.all_actions: #@UnusedVariable
                    self.successors[node_id][roll - self.roll_offset].append({})
        else:
            node_id = self.node_ids[node_name]
        return node_id

#    def add_node(self, node, pos):
#        if node not in self.nodes:
#            self.nodes[node] = pos
            
    def has_attr(self, node_id, attr):
        return attr in self.node_attrs[node_id]
        
    def get_attr(self, node_id, attr):
        return self.node_attrs[node_id][attr]
    
    def set_attr(self, node_id, attr, val):
        self.node_attrs[node_id][attr] = val
        
    def get_node_name(self, node_id):
        return self.node_names[node_id]
    
    def get_node_id(self, node_name):
        return self.node_ids[node_name]

    def add_edge(self, node_from_id, roll, action, node_to_id):
        target_map = self.successors[node_from_id][roll - self.roll_offset][action]
        if node_to_id not in target_map:
            target_map[node_to_id] = 1.0
        else:
            target_map[node_to_id] += 1.0
                
    def get_successors(self, node_id, roll, action):
        return self.successors[node_id][roll - self.roll_offset][action]
    
    def convert_freq_to_prob(self):
        for node_id in range(len(self.node_names)):
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    sum_freq = sum(self.successors[node_id][roll_index][action].itervalues())
                    for (target_id, freq) in self.successors[node_id][roll_index][action].iteritems():
                        self.successors[node_id][roll_index][action][target_id] = \
                        float(freq) / sum_freq
    
    def save_to_file(self, path_to_file):
        f = open(path_to_file, 'w')
        pickle.dump(self, f)
        f.close()
       
    @classmethod 
    def load_from_file(cls, path_to_file):
        f = open(path_to_file, 'r')
        g = pickle.load(f)
        return g
    
    def print_stats(self):
        print 'Graph Stats:'
        print 'Number of nodes: %d' % len(self.node_names)
        print 'Number of sources: %d' % (len(self.sources[PLAYER_WHITE]) + len(self.sources[PLAYER_BLACK]))
        print 'Number of sinks: %d' % (len(self.sinks[PLAYER_WHITE]) + len(self.sinks[PLAYER_BLACK]))
        total_edges = 0
        total_transitions = 0
        for node_id in range(len(self.node_names)):
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    total_transitions += sum(self.successors[node_id][roll_index][action].itervalues())
                    for freq in self.successors[node_id][roll_index][action].itervalues():
                        if freq > 0:
                            total_edges += 1
        print 'Number of edges: %d' % total_edges
        print 'Number of transitions: %d' % total_transitions
    
if __name__ == '__main__':
    g = StateGraph([0, 1], [1, 2], 1)
    n0 = g.add_node('0')
    n1 = g.add_node('1')
    n2 = g.add_node('2')
    n3 = g.add_node('3')
    n4 = g.add_node('4')
    n5 = g.add_node('5')
    n6 = g.add_node('6')
    g.set_as_source(n0, PLAYER_WHITE)
    g.set_as_sink(n4, PLAYER_WHITE)
    g.set_as_sink(n6, PLAYER_BLACK)
    g.add_edge(n0, 1, 0, n1)
    g.add_edge(n1, 1, 0, n2)
    g.add_edge(n2, 1, 0, n3)
    g.add_edge(n3, 1, 0, n4)
    g.add_edge(n2, 1, 0, n5)
    g.add_edge(n2, 1, 0, n5)
    g.add_edge(n5, 1, 0, n6)
    print g.get_successors(n0, 1, 0)
    print g.get_successors(n6, 1, 0)
    print g.get_successors(n2, 1, 0)
    print g.successors[n2]
    g.print_stats()
    
    g.convert_freq_to_prob()
    print g.successors[n2]
    
    