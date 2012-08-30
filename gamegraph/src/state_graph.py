'''
Created on Jun 25, 2012

@author: reza
'''
from common import PLAYER_WHITE, PLAYER_BLACK
import random
import cPickle
#import marshal
from Queue import Queue

class StateGraph(object):

    def __init__(self, all_rolls, roll_offset, all_actions):
        self.successors = []
        self.node_names = []
        self.node_colors = []
        self.node_attrs = []
        self.node_ids = {}
        self.sources = [[], []]
        self.sinks = [[], []]
        self.all_rolls = all_rolls
        self.roll_offset = roll_offset
        self.all_actions = all_actions
        
        self.distance_buckets = [[], []]
                
    def get_random_source(self, player_to_start):
        return random.choice(self.sources[player_to_start])
        
    def get_transition_outcome(self, node_id, roll, action):
        return self.successors[node_id][roll - self.roll_offset][action]

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
    
    def add_node(self, node_name, node_color):
#        if node_name not in self.node_names:
        if not self.node_ids.has_key(node_name):
            node_id = len(self.node_names)
            self.node_names.append(node_name)
            self.node_attrs.append({})
            self.node_ids[node_name] = node_id
            self.node_colors.append(node_color)
            self.successors.append([])
            for roll in self.all_rolls:
                self.successors[node_id].append([])
                for action in self.all_actions: #@UnusedVariable
                    self.successors[node_id][roll - self.roll_offset].append(None)
        else:
            node_id = self.node_ids[node_name]
        return node_id

    def has_attr(self, node_id, attr):
        return attr in self.node_attrs[node_id]
        
    def get_attr(self, node_id, attr):
        return self.node_attrs[node_id][attr]
    
    def set_attr(self, node_id, attr, val):
        self.node_attrs[node_id][attr] = val
        
    def get_node_name(self, node_id):
        return self.node_names[node_id]
    
    def get_node_color(self, node_id):
        return self.node_colors[node_id]
    
    def get_node_id(self, node_name):
        return self.node_ids[node_name]
    
    def add_to_distance_bucket(self, node_id, dist):
        buckets = self.distance_buckets[self.node_colors[node_id]]
        while dist >= len(buckets):
            buckets.append([])
        buckets[dist].append(node_id)
        
    def add_edge(self, node_from_id, roll, action, node_to_id):
        self.successors[node_from_id][roll - self.roll_offset][action] = node_to_id
                
    def get_successor(self, node_id, roll, action):
        return self.successors[node_id][roll - self.roll_offset][action]
    
    def get_all_successors(self, node_id):
        succ = []
        for roll in self.all_rolls:
            roll_index = roll - self.roll_offset
            for action in self.all_actions:
                succ_id = self.successors[node_id][roll_index][action]
                if (succ_id is not None) and (succ_id not in succ):
                    succ.append(succ_id)
        return succ
    
    def get_random_successor_at_distance(self, node_id, color, distance):
        result = None
        tries_left = 1000
        current_node = node_id
        while tries_left > 0:
            successors = self.get_all_successors(current_node)
            if len(successors) > 0:
                successor = random.choice(successors)
            else:
                break
            if self.node_colors[successor] == color and \
                    self.node_attrs[successor]['d'] >= distance:
                result = successor
                break
            else:
                current_node = successor
        return result

    def get_random_node_at_distance(self, color, distance):
        result = None
        buckets_for_color = self.distance_buckets[color]
        for d in range(distance, len(buckets_for_color)):
            bucket = buckets_for_color[d]
            if len(bucket) > 0:
                result = random.choice(bucket)
                break
        return result

    def get_another_successor(self, node_id, current_successor):
        result = None
        node_distance = self.node_attrs[node_id]['d']
        successors = self.get_all_successors(node_id)
        other_successors = [n_id for n_id in successors
                            if n_id != current_successor and
                            self.node_attrs[n_id]['d'] >= node_distance] 
        if len(other_successors) > 1:
            result = random.choice(successors)
        return result
    
    def compute_bfs(self):
        for node_id in range(len(self.node_names)):
            self.set_attr(node_id, 'bfscolor', 'white')
            self.set_attr(node_id, 'd', -1)
        Q = Queue()
        for s in (self.sources[PLAYER_WHITE] + self.sources[PLAYER_BLACK]):
            self.set_attr(s, 'bfscolor', 'gray')
            self.set_attr(s, 'd',  0)
            self.add_to_distance_bucket(s, 0)
            Q.put(s)
        while not Q.empty():
            u = Q.get()
#            print 'Processing %s' % self.node_names[u]
            u_d = self.get_attr(u, 'd')
            for v in self.get_all_successors(u):
                if self.get_attr(v, 'bfscolor') == 'white':
                    self.set_attr(v, 'bfscolor', 'gray')
                    v_d = u_d + 1
                    self.set_attr(v, 'd', v_d)
                    self.add_to_distance_bucket(v, v_d)
                    Q.put(v)
            self.set_attr(u, 'bfscolor', 'black')
    
    def remove_back_edges(self):
        count_back_edges = 0
        count_replaced_back_edges = 0
        for node_id in range(len(self.node_names)):
            node_dist = self.get_attr(node_id, 'd')
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        successor_dist = self.get_attr(successor, 'd')
                        if successor_dist < node_dist:
                            count_back_edges += 1
#                            print 'removing edge %s -> %s' % (self.node_names[node_id], self.node_names[successor]) 
#                            new_successor = self.get_random_node_at_distance(
#                                    self.node_colors[successor], node_dist + 1)
#                            new_successor = self.get_random_successor_at_distance(
#                                    successor, self.node_colors[successor],
#                                    node_dist + 1)
                            new_successor = self.get_another_successor(node_id, 
                                                                       successor)
                            if new_successor is not None:
                                count_replaced_back_edges += 1
                                self.successors[node_id][roll_index][action] = new_successor
#                                print 'adding edge %s -> %s' % (self.node_names[node_id], self.node_names[new_successor])
#                            else:
#                                print 'Couldn\'t add a new edge. Restoring the back edge'
        print 'Found %d back edges, replaced %d' % (count_back_edges, count_replaced_back_edges)

    def save_to_file(self, path_to_file):
        print 'Saving graph...'
        f = open(path_to_file, 'w')
        cPickle.dump(self, f)
#        marshal.dump(self, f)
        f.close()
        print 'Done.'
       
    @classmethod 
    def load_from_file(cls, path_to_file):
        print 'Loading graph...'
        f = open(path_to_file, 'r')
        g = cPickle.load(f)
#        g = marshal.load(f)
        f.close()
        print 'Done.'
        return g
    
    def print_stats(self):
        print 'Graph Stats:'
        print 'Number of nodes: %d' % len(self.node_names)
        print 'Number of sources: %d' % (len(self.sources[PLAYER_WHITE]) + len(self.sources[PLAYER_BLACK]))
        print 'Number of sinks: %d' % (len(self.sinks[PLAYER_WHITE]) + len(self.sinks[PLAYER_BLACK]))
        total_edges = 0
        for node_id in range(len(self.node_names)):
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    if self.successors[node_id][roll_index][action] is not None:
                        total_edges += 1
        print 'Number of edges: %d' % total_edges

if __name__ == '__main__':
    g = StateGraph([0, 1], [1, 2], 1)
    n0 = g.add_node('0', PLAYER_WHITE)
    n1 = g.add_node('1', PLAYER_BLACK)
    n2 = g.add_node('2', PLAYER_WHITE)
    n3 = g.add_node('3', PLAYER_BLACK)
    n4 = g.add_node('4', PLAYER_WHITE)
    n5 = g.add_node('5', PLAYER_BLACK)
    n6 = g.add_node('6', PLAYER_WHITE)
    g.set_as_source(n0, PLAYER_WHITE)
    g.set_as_sink(n4, PLAYER_WHITE)
    g.set_as_sink(n6, PLAYER_BLACK)
    g.add_edge(n0, 1, 0, n1)
    g.add_edge(n1, 1, 0, n2)
    g.add_edge(n2, 1, 0, n3)
    g.add_edge(n3, 1, 0, n4)
    g.add_edge(n2, 1, 1, n5)
    g.add_edge(n5, 1, 0, n6)
    print g.get_successor(n0, 1, 0)
    print g.get_successor(n6, 1, 0)
    print g.get_successor(n2, 1, 0)
    print g.get_all_successors(n2)
    print g.successors[n2]
    g.print_stats()
    
    