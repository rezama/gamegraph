'''
Created on Jun 25, 2012

@author: reza
'''
from common import PLAYER_WHITE, PLAYER_BLACK
import random

class Graph(object):

    def __init__(self):
        self.neighbors = {}
        self.sources = {PLAYER_WHITE: [], PLAYER_BLACK: []}
        self.sinks = {PLAYER_WHITE: [], PLAYER_BLACK: []}
    
    def add_source(self, node, player):
        if node not in self.sources[player]:
            self.sources[player].append(node)
    
    def add_sink(self, node, player):
        if node not in self.sinks[player]:
            self.sinks[player].append(node)
    
    def add_edge(self, node1, node2, edge):
        if node1 not in self.neighbors:
            self.neighbors[node1] = {}
            
        if edge not in self.neighbors[node1]:
            self.neighbors[node1][edge] = {}
            
        if node2 not in self.neighbors[node1][edge]:
            self.neighbors[node1][edge][node2] = 0
            
        self.neighbors[node1][edge][node2] += 1
    
    def get_neighbors(self, node, edge):
        if node in self.neighbors:
            if edge in self.neighbors[node]:
                return self.neighbors[node][edge].keys()
        return []
    
    def get_source(self, player_to_start):
        return random.choice(self.sources[player_to_start])
        
    def move(self, node, edge):
        destinations_map = self.neighbors[node][edge]
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
    
    def convert_freq_to_prob(self):
        for node1 in self.neighbors:
            for edge in self.neighbors[node1]:
                sum_freq = 0
                for node2 in self.neighbors[node1][edge]:
                    sum_freq += self.neighbors[node1][edge][node2]
                for node2 in self.neighbors[node1][edge]:
                    self.neighbors[node1][edge][node2] = \
                        float(self.neighbors[node1][edge][node2]) / sum_freq
    
    def print_stats(self):
        print "G stats:"
        print "Number of nodes: %d" % len(self.neighbors)
        total_edges = 0
        total_transitions = 0
        for node1 in self.neighbors:
            for edge in self.neighbors[node1]:
                for node2 in self.neighbors[node1][edge]:
                    total_edges += 1
                    total_transitions += self.neighbors[node1][edge][node2]
        print "Number of edges: %d" % total_edges
        print "Number of transitions: %d" % total_transitions
    
if __name__ == '__main__':
    g = Graph()
    g.add_edge("1", "2", "r")
    g.add_edge("2", "3", "r")
    g.add_edge("3", "4", "r")
    g.add_edge("3", "5", "r")
    g.add_edge("3", "5", "r")
    print g.get_neighbors("3", "r")
    print g.get_neighbors("2", "r")
    print g.get_neighbors("5", "r")
    print g.get_neighbors("0", "r")
    print g.neighbors["3"]
    g.print_stats()
    
