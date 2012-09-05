'''
Created on Jun 25, 2012

@author: reza
'''
from common import PLAYER_WHITE, PLAYER_BLACK
import random
import cPickle
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

    def get_another_successor_check_distance(self, node_id, current_successor):
        result = None
        node_distance = self.node_attrs[node_id]['d']
        successors = self.get_all_successors(node_id)
        other_successors = [n_id for n_id in successors
                            if n_id != current_successor and
                            self.node_attrs[n_id]['d'] >= node_distance] 
        if len(other_successors) > 1:
            result = random.choice(other_successors)
        return result
    
    def get_another_successor_check_hit(self, node_id, current_successor):
        result = None
        successors = self.get_all_successors(node_id)
        other_successors = [n_id for n_id in successors
                            if (n_id != current_successor) and
                            ('0' not in self.node_names[n_id][2:])]
        if len(other_successors) > 1:
            result = random.choice(other_successors)
        return result
    
    def compute_bfs(self):
        print 'Computing BFS...'
        for node_id in range(len(self.node_names)):
            self.set_attr(node_id, 'bfscolor', 'w')
            self.set_attr(node_id, 'd', -1)
        Q = Queue()
        for s in (self.sources[PLAYER_WHITE] + self.sources[PLAYER_BLACK]):
            self.set_attr(s, 'bfscolor', 'g')
            self.set_attr(s, 'd',  0)
            self.add_to_distance_bucket(s, 0)
            Q.put(s)
        while not Q.empty():
            u = Q.get()
#            print 'Processing %s' % self.node_names[u]
            u_d = self.get_attr(u, 'd')
            for v in self.get_all_successors(u):
                if self.get_attr(v, 'bfscolor') == 'w':
                    self.set_attr(v, 'bfscolor', 'g')
                    v_d = u_d + 1
                    self.set_attr(v, 'd', v_d)
                    self.add_to_distance_bucket(v, v_d)
                    Q.put(v)
            self.set_attr(u, 'bfscolor', 'b')
        print 'Done.'
    
    def print_all_edges(self):
        for node_id in range(len(self.node_names)):
            node_dist = self.get_attr(node_id, 'd')
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        successor_dist = self.get_attr(successor, 'd')
                        is_replaceable = False 
                        flags = ''
                        if '0' in self.node_names[successor][2:]:
                            flags += '-HIT'
                        if successor_dist < node_dist:
                            flags += '-BACK'
                            new_successor = self.get_another_successor_check_distance(node_id, successor)
                            if new_successor is not None:
                                is_replaceable = True
                        print 'Found edge %s -> %s, id: %d -> %d, dist: %d -> %d %s' % \
                        (self.node_names[node_id], self.node_names[successor],
                         node_id, successor,
                         node_dist, successor_dist, flags),
                        if is_replaceable:
                            print 'replaceable with %s' % self.node_names[new_successor]
                        else:
                            print ''  
                            
    def print_back_edges(self):
        for node_id in range(len(self.node_names)):
            node_dist = self.get_attr(node_id, 'd')
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        successor_dist = self.get_attr(successor, 'd')
                        if successor_dist < node_dist:
                            flags = ''
                            is_replaceable = False 
                            new_successor = self.get_another_successor_check_distance(node_id, successor)
                            if new_successor is not None:
                                is_replaceable = True
                            if '0' in self.node_names[successor][2:]:
                                flags += '-HIT'
                                
                            print 'Found back edge %s -> %s, id: %d -> %d, dist: %d -> %d %s' % \
                            (self.node_names[node_id], self.node_names[successor],
                             node_id, successor,
                             node_dist, successor_dist, flags),
                            if is_replaceable:
                                print 'replaceable to %s' % self.node_names[new_successor]
                            else:
                                print ''  
                            
    def trim_back_edges(self, prob_keep = 0.0):
        print 'Trimming back edges, keeping %d%%...' % (prob_keep * 100)
        count_back_edges = 0
        count_replaceable = 0
        count_replaced = 0
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
#                            print 'Found back edge %s -> %s' % (self.node_names[node_id], self.node_names[successor]) 
#                            new_successor = self.get_random_node_at_distance(
#                                    self.node_colors[successor], node_dist + 1)
#                            new_successor = self.get_random_successor_at_distance(
#                                    successor, self.node_colors[successor],
#                                    node_dist + 1)
                            new_successor = self.get_another_successor_check_distance(node_id, successor)
                            if new_successor is not None:
                                count_replaceable += 1
                                p = random.random()
                                if p >= prob_keep:
                                    count_replaced += 1
                                    self.successors[node_id][roll_index][action] = new_successor
#                                    print 'Replaced back edge %s -> %s with %s -> %s' % \
#                                    (self.node_names[node_id], self.node_names[successor],
#                                     self.node_names[node_id], self.node_names[new_successor]) 
#                                print 'Replacing edge %s -> %s' % (self.node_names[node_id], self.node_names[new_successor])
#                            else:
#                                print 'Couldn\'t replace. Keeping the back edge'
                                
        print 'Found %d back edges, %d replaceable, %d replaced' % (
                count_back_edges, count_replaceable, count_replaced)

    def trim_hit_edges(self, prob_keep = 0.0):
        print 'Trimming hit edges, keeping %d%%...' % (prob_keep * 100)
        count_hit_edges = 0
        count_replaceable = 0
        count_replaced = 0
        for node_id in range(len(self.node_names)):
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        if '0' in self.node_names[successor][2:]:
                            count_hit_edges += 1
                            new_successor = self.get_another_successor_check_hit(node_id, successor)
                            if new_successor is not None:
                                count_replaceable += 1
                                p = random.random()
                                if p >= prob_keep:
                                    count_replaced += 1
                                    self.successors[node_id][roll_index][action] = new_successor
                                
        print 'Found %d hit edges, %d replaceable, %d replaced' % (
                count_hit_edges, count_replaceable, count_replaced)

    def cleanup_attrs(self):
        for node_id in range(len(self.node_names)):
            del self.node_attrs[node_id]['d']
            del self.node_attrs[node_id]['bfscolor']

    def save_to_file(self, path_to_file):
        print 'Saving graph %s...' % path_to_file
        f = open(path_to_file, 'w')
        cPickle.dump(self, f)
#        marshal.dump(self, f)
        f.close()
        print 'Done.'
       
    @classmethod 
    def load_from_file(cls, path_to_file):
        print 'Loading graph %s...' % path_to_file
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
    
    