'''
Created on Jun 25, 2012

@author: reza
'''
from common import PLAYER_WHITE, PLAYER_BLACK
import random
import pickle

class StateGraph(object):

    def __init__(self, dice_sides):
        self.neighbors = {}
        self.sources = {PLAYER_WHITE: [], PLAYER_BLACK: []}
        self.sinks = {PLAYER_WHITE: [], PLAYER_BLACK: []}
        self.dice_sides = dice_sides
                
    def get_random_source(self, player_to_start):
        return random.choice(self.sources[player_to_start])
        
    def move(self, node, roll, edge):
        destinations_map = self.neighbors[node][roll][edge]
        target = None
        p = random.random()
        sum_prob = 0.0
        for (node, prob) in destinations_map:
            sum_prob += prob
            if prob > p:
                target = node
                break
        return target

    def is_sink(self, node):
        return (node in self.sinks[PLAYER_WHITE]) or \
               (node in self.sinks[PLAYER_BLACK])
    
    def get_sink_color(self, node):
        if node in self.sinks[PLAYER_WHITE]:
            return PLAYER_WHITE
        elif node in self.sinks[PLAYER_BLACK]:
            return PLAYER_BLACK
        else:
            return None
    
    def add_source(self, node, player):
        if node not in self.sources[player]:
            self.sources[player].append(node)
    
    def add_sink(self, node, player):
        if node not in self.sinks[player]:
            self.sinks[player].append(node)
    
    def add_edge(self, node1, roll, edge, node2):
        if node1 not in self.neighbors:
            self.neighbors[node1] = {}
            
        if roll not in self.neighbors[node1]:
            self.neighbors[node1][roll] = {}
            
        if edge not in self.neighbors[node1][roll]:
            self.neighbors[node1][roll][edge] = {}
            
        if node2 not in self.neighbors[node1][roll][edge]:
            self.neighbors[node1][roll][edge][node2] = 0
            
        self.neighbors[node1][roll][edge][node2] += 1
    
    def get_neighbors(self, node, roll, edge):
        if node in self.neighbors:
            if roll in self.neighbors[node]:
                if edge in self.neighbors[node][roll]:
                    return self.neighbors[node][roll][edge].keys()
        return []
    
    def convert_freq_to_prob(self):
        for node1 in self.neighbors:
            for roll in self.neighbors[node1]:
                for edge in self.neighbors[node1][roll]:
                    sum_freq = 0
                    for node2 in self.neighbors[node1][roll][edge]:
                        sum_freq += self.neighbors[node1][roll][edge][node2]
                    for node2 in self.neighbors[node1][roll][edge]:
                        self.neighbors[node1][roll][edge][node2] = \
                            float(self.neighbors[node1][roll][edge][node2]) / sum_freq
    
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
        print 'Number of nodes: %d' % len(self.neighbors)
        total_edges = 0
        total_transitions = 0
        for node1 in self.neighbors:
            for roll in self.neighbors[node1]:
                for edge in self.neighbors[node1][roll]:
                    for node2 in self.neighbors[node1][roll][edge]:
                        total_edges += 1
                        total_transitions += self.neighbors[node1][roll][edge][node2]
        print 'Number of edges: %d' % total_edges
        print 'Number of transitions: %d' % total_transitions
    
if __name__ == '__main__':
    g = StateGraph([1, 2])
    g.add_source('1', PLAYER_WHITE)
    g.add_edge('1', 1, 'r', '2')
    g.add_edge('2', 1, 'r', '3')
    g.add_edge('3', 1, 'r', '4')
    g.add_edge('4', 1, 'r', '5')
    g.add_edge('3', 1, 'r', '6')
    g.add_edge('3', 1, 'r', '6')
    g.add_edge('6', 1, 'r', '7')
    g.add_sink('5', PLAYER_WHITE)
    g.add_sink('7', PLAYER_BLACK)
    print g.get_neighbors('1', 1, 'r')
    print g.get_neighbors('7', 1, 'r')
    print g.get_neighbors('3', 1, 'r')
    print g.get_neighbors('0', 1, 'r')
    print g.neighbors['3']
    g.print_stats()
    
    g.convert_freq_to_prob()
    print g.neighbors['3']
    
