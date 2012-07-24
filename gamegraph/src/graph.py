'''
Created on Jun 25, 2012

@author: reza
'''

class Graph(object):

    def __init__(self):
        self.neighbors = {}
        
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
    
    def print_stats(self):
        print "G stats:"
        print "Number of nodes: %d" % len(self.neighbors)
        total_edges = 0
        total_transitions = 0
        for node1 in self.neighbors:
            node_edges = 0
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
    
    