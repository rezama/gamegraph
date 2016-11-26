'''
Created on Jun 25, 2012

@author: reza
'''
from common import PLAYER_WHITE, PLAYER_BLACK, REWARD_WIN, REWARD_LOSE,\
    DIST_ATTR, BFS_COLOR_ATTR, VAL_ATTR, SUFFIX_GRAPH_OK, ExpParams
import random
import cPickle
from Queue import Queue
import gzip
import os
from params import VALUE_ITER_MIN_RESIDUAL
import math

USE_GZIP = True

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

    def get_num_nodes(self):
        return len(self.node_names)
    
    @classmethod
    def load(cls, exp_params):
        print 'Loading graph for signature: %s...' % exp_params.signature
        g = None
        graph_filename = exp_params.get_graph_filename()
        graph_ok_filename = graph_filename + SUFFIX_GRAPH_OK
        if os.path.isfile(graph_ok_filename):
            print 'Graph file exists.'
            g = cls.__load_from_file(graph_filename)
        else:
            print 'Graph file does not exist.'
#            if exp_params.is_first_trial():
#                print 'Going to generate...'
#                g = exp_params.state_class.generate_graph(exp_params)
#                g.save(exp_params)
#            else:
#                print 'Waiting for graph file to appear...'
#                while not os.path.isfile(graph_ok_filename):
#                    time.sleep(5)
#                g = cls.__load_from_file(graph_filename)
            g = exp_params.state_class.generate_graph(exp_params)
            g.save(exp_params)
        return g
                
    def save(self, exp_params, filename_suffix=None):
        if exp_params.is_first_trial():
            if not self.has_attr(0, VAL_ATTR):
                print 'Automatically calling value_iteration() in save()...'
                self.value_iteration(exp_params)

            if not self.has_attr(0, DIST_ATTR):
                print 'Automatically calling compute_bfs() in save()...'
                self.compute_bfs()

            print 'Saving graph for signature: %s, suffix: %s...' % (exp_params.signature,
                                                                     filename_suffix)
            graph_filename = exp_params.get_graph_filename()
            if filename_suffix is not None:
                graph_filename += filename_suffix
            graph_ok_filename = graph_filename + SUFFIX_GRAPH_OK
            if os.path.isfile(graph_ok_filename):
                os.remove(graph_ok_filename)
            self.__save_to_file(graph_filename)
            f = open(graph_ok_filename, 'w')
            f.close()

    @classmethod 
    def __load_from_file(cls, path_to_file):
        print 'Loading graph from file: %s...' % path_to_file
        if USE_GZIP:
            f = gzip.open(path_to_file + '.gz', 'r')
        else:
            f = open(path_to_file, 'r')
        g = cPickle.load(f)
#        g = marshal.load(f)
        f.close()
        print 'Done.'
        return g

    def __save_to_file(self, path_to_file):
        print 'Saving graph to file: %s...' % path_to_file
        if USE_GZIP:
            f = gzip.open(path_to_file + '.gz', 'w')
        else:
            f = open(path_to_file, 'w')
        cPickle.dump(self, f)
#        marshal.dump(self, f)
        f.close()
        print 'Done.'
           
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
            node_id = self.get_num_nodes()
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
        succ_list = []
        for roll in self.all_rolls:
            roll_index = roll - self.roll_offset
            for action in self.all_actions:
                succ_id = self.successors[node_id][roll_index][action]
                if (succ_id is not None) and (succ_id not in succ_list):
                    succ_list.append(succ_id)
        return succ_list
    
    def get_all_successors_for_roll(self, node_id, roll):
        succ_list = []
        roll_index = roll - self.roll_offset
        for action in self.all_actions:
            succ_id = self.successors[node_id][roll_index][action]
            if (succ_id is not None) and (succ_id not in succ_list):
                succ_list.append(succ_id)
        return succ_list
    
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
                    self.node_attrs[successor][DIST_ATTR] >= distance:
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
        node_distance = self.node_attrs[node_id][DIST_ATTR]
        successors = self.get_all_successors(node_id)
        other_successors = [n_id for n_id in successors
                            if n_id != current_successor and
                            self.node_attrs[n_id][DIST_ATTR] >= node_distance] 
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
        for node_id in range(self.get_num_nodes()):
            self.set_attr(node_id, BFS_COLOR_ATTR, 'w')
            self.set_attr(node_id, DIST_ATTR, -1)
        Q = Queue()
        for s in (self.sources[PLAYER_WHITE] + self.sources[PLAYER_BLACK]):
            self.set_attr(s, BFS_COLOR_ATTR, 'g')
            self.set_attr(s, DIST_ATTR,  0)
            self.add_to_distance_bucket(s, 0)
            Q.put(s)
        while not Q.empty():
            u = Q.get()
#            print 'Processing %s' % self.node_names[u]
            u_d = self.get_attr(u, DIST_ATTR)
            for v in self.get_all_successors(u):
                if self.get_attr(v, BFS_COLOR_ATTR) == 'w':
                    self.set_attr(v, BFS_COLOR_ATTR, 'g')
                    v_d = u_d + 1
                    self.set_attr(v, DIST_ATTR, v_d)
                    self.add_to_distance_bucket(v, v_d)
                    Q.put(v)
            self.set_attr(u, BFS_COLOR_ATTR, 'b')
        print 'Done.'
    
    def value_iteration(self, exp_params):
        print 'Doing value iteration...'
        init_val = float(REWARD_WIN - REWARD_LOSE) / 2
#        init_val = -1.0
        for node_id in range(self.get_num_nodes()):
            self.set_attr(node_id, VAL_ATTR, init_val)
#        for node_id in range(self.get_num_nodes()):
#            if self.node_colors[node_id] == PLAYER_WHITE:
#                self.set_attr(node_id, VAL_ATTR, REWARD_WIN)
#            else:
#                self.set_attr(node_id, VAL_ATTR, REWARD_LOSE)
        for node_id in self.sinks[PLAYER_WHITE]:
            self.set_attr(node_id, VAL_ATTR, REWARD_WIN)
        for node_id in self.sinks[PLAYER_BLACK]:
            self.set_attr(node_id, VAL_ATTR, REWARD_LOSE)
        num_rolls = len(self.all_rolls)
        cont = True
        iteration = 0
        while cont:
            iteration += 1
            print 'Iteration %d... ' % iteration,
            max_residual = 0
            for node_id in reversed(range(self.get_num_nodes())):
                node_color = self.node_colors[node_id]
                if (node_id not in self.sinks[PLAYER_WHITE]) and \
                                    (node_id not in self.sinks[PLAYER_BLACK]):
#                    multiplier = 1
#                    if self.node_colors[node_id] == PLAYER_BLACK:
#                        multiplier = -1
#                    roll_values = [-multiplier * REWARD_WIN] * num_rolls
                    roll_values = [None] * num_rolls
                    for roll in self.all_rolls:
                        roll_index = roll - self.roll_offset
                        for action in self.all_actions:
                            successor = self.successors[node_id][roll_index][action]
                            if successor is not None:
                                successor_value = self.node_attrs[successor][VAL_ATTR]
                                if roll_values[roll_index] is None:
                                    roll_values[roll_index] = successor_value
                                else:
                                    if node_color == PLAYER_WHITE:
                                        if successor_value > roll_values[roll_index]:
                                            roll_values[roll_index] = successor_value
                                    else:
                                        if successor_value < roll_values[roll_index]:
                                            roll_values[roll_index] = successor_value
#                            if (multiplier * successor_value) > (multiplier * roll_values[roll_index]):
#                                    roll_values[roll_index] = successor_value
                    # have to remove Nones for rolls that are not legal
                    legal_roll_values = [v for v in roll_values if v is not None]
                    num_legal_rolls = len(legal_roll_values) 
                    avg_value = float(sum(legal_roll_values)) / num_legal_rolls
                    if node_color == PLAYER_WHITE:
                        value_with_choose_roll = exp_params.choose_roll * max(legal_roll_values)
                    else:
                        value_with_choose_roll = exp_params.choose_roll * min(legal_roll_values)
                    value_regular = (1 - exp_params.choose_roll) * avg_value
                    new_state_value = value_regular + value_with_choose_roll
                    residual = abs(self.node_attrs[node_id][VAL_ATTR] - new_state_value)
#                    if residual > 0:
#                        print 'Updating state %s value from %.4f to %.4f' % (
#                                self.node_names[node_id], self.node_attrs[node_id][VAL_ATTR], new_state_value)
#                    if (new_state_value == init_val) and (avg_value != init_val):
#                        print 'Fucked here!'
                    if residual > max_residual:
                        max_residual = residual
                    self.node_attrs[node_id][VAL_ATTR] = new_state_value
            print 'maximum residual: %.4f' % max_residual
            if max_residual < VALUE_ITER_MIN_RESIDUAL:
                cont = False
        print 'Done.'
    
    def compute_dice_volatility(self, exp_params):
        num_rolls = len(self.all_rolls)
        sum_volatility = 0.0
        count_nodes = 0
        for node_id in range(self.get_num_nodes()):
            node_color = self.node_colors[node_id]
            if (node_id not in self.sinks[PLAYER_WHITE]) and (node_id not in self.sinks[PLAYER_BLACK]):
                count_nodes += 1
                roll_values = [None] * num_rolls
                for roll in self.all_rolls:
                    roll_index = roll - self.roll_offset
                    for action in self.all_actions:
                        successor = self.successors[node_id][roll_index][action]
                        if successor is not None:
                            successor_value = self.node_attrs[successor][VAL_ATTR]
                            if roll_values[roll_index] is None:
                                roll_values[roll_index] = successor_value
                            else:
                                if node_color == PLAYER_WHITE:
                                    if successor_value > roll_values[roll_index]:
                                        roll_values[roll_index] = successor_value
                                else:
                                    if successor_value < roll_values[roll_index]:
                                        roll_values[roll_index] = successor_value
                avg_value = float(sum(roll_values)) / num_rolls
                if self.node_colors[node_id] == PLAYER_WHITE:
                    value_with_choose_roll = exp_params.choose_roll * max(roll_values)
                else:
                    value_with_choose_roll = exp_params.choose_roll * min(roll_values)
                value_regular = (1 - exp_params.choose_roll) * avg_value #@UnusedVariable
                mean_value = self.node_attrs[node_id][VAL_ATTR]
                squared_diffs_regular = [(v - mean_value) * (v - mean_value)
                                         for v in roll_values]
                squared_diffs_regular_adjusted = [d * (1 - exp_params.choose_roll) / num_rolls
                                                  for d in squared_diffs_regular]
                squared_diff_choose_roll_adjusted = (value_with_choose_roll - mean_value) * (value_with_choose_roll - mean_value) * exp_params.choose_roll
                squared_diff_sum = sum(squared_diffs_regular_adjusted) + squared_diff_choose_roll_adjusted
                std_dev = math.sqrt(squared_diff_sum)
                sum_volatility += std_dev
        avg_volatility = sum_volatility / count_nodes
        return avg_volatility
    
    def compute_action_volatility(self, exp_params):
        sum_volatility = 0.0
        count_nodes = 0
        for node_id in range(self.get_num_nodes()):
            if (node_id not in self.sinks[PLAYER_WHITE]) and (node_id not in self.sinks[PLAYER_BLACK]):
                for roll in self.all_rolls:
                    roll_successors = self.get_all_successors_for_roll(node_id, roll)
                    if len(roll_successors) > 0:
                        count_nodes += 1
                        successor_values = [self.node_attrs[successor][VAL_ATTR]
                                            for successor in roll_successors]
                        
                        mean_value = float(sum(successor_values)) / len(successor_values)
                        squared_diffs = [(v - mean_value) * (v - mean_value)
                                                 for v in successor_values]
                        squared_diff_sum = sum(squared_diffs)
                        std_dev = math.sqrt(squared_diff_sum)
                        sum_volatility += std_dev
        avg_volatility = sum_volatility / count_nodes
        return avg_volatility
    
    def print_all_edges(self):
        for node_id in range(self.get_num_nodes()):
            node_dist = self.get_attr(node_id, DIST_ATTR)
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        successor_dist = self.get_attr(successor, DIST_ATTR)
                        is_replaceable = False 
                        flags = ''
                        if VAL_ATTR in self.node_attrs[node_id]:
                            flags += '(value: %.2f -> %.2f)' % (self.node_attrs[node_id][VAL_ATTR], self.node_attrs[successor][VAL_ATTR])
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
        for node_id in range(self.get_num_nodes()):
            node_dist = self.get_attr(node_id, DIST_ATTR)
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        successor_dist = self.get_attr(successor, DIST_ATTR)
                        if successor_dist < node_dist:
                            flags = ''
                            if VAL_ATTR in self.node_attrs[node_id]:
                                flags += '(value: %.2f -> %.2f)' % (self.node_attrs[node_id][VAL_ATTR], self.node_attrs[successor][VAL_ATTR])
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
        self.remove_value_attrs()
        count_back_edges = 0
        count_replaceable = 0
        count_replaced = 0
        for node_id in range(self.get_num_nodes()):
            node_dist = self.get_attr(node_id, DIST_ATTR)
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    successor = self.successors[node_id][roll_index][action]
                    if successor is not None:
                        successor_dist = self.get_attr(successor, DIST_ATTR)
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
        self.remove_value_attrs()
        count_hit_edges = 0
        count_replaceable = 0
        count_replaced = 0
        for node_id in range(self.get_num_nodes()):
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

    def transfer_state_values(self, agent):
        print 'Transferring state values...'
        for node_id in range(self.get_num_nodes()):
            node_name = self.node_names[node_id]
            if node_id in self.sinks[PLAYER_WHITE]:
                self.node_attrs[node_id][VAL_ATTR] = REWARD_WIN
            elif node_id in self.sinks[PLAYER_BLACK]:
                self.node_attrs[node_id][VAL_ATTR] = REWARD_LOSE
            else:
                value = agent.get_board_value(node_name)
                if self.node_colors[node_id] == PLAYER_BLACK:
                    value = REWARD_WIN - REWARD_LOSE - value
                self.node_attrs[node_id][VAL_ATTR] = value
                                
        print 'Done.'

    def remove_value_attrs(self):
        for node_id in range(self.get_num_nodes()):
            if self.node_attrs[node_id].has_key(VAL_ATTR):
                del self.node_attrs[node_id][VAL_ATTR]

    def remove_attrs(self):
        for node_id in range(self.get_num_nodes()):
            if self.node_attrs[node_id].has_key(BFS_COLOR_ATTR):
                del self.node_attrs[node_id][BFS_COLOR_ATTR]
            if self.node_attrs[node_id].has_key(DIST_ATTR):
                del self.node_attrs[node_id][DIST_ATTR]
            if self.node_attrs[node_id].has_key(VAL_ATTR):
                del self.node_attrs[node_id][VAL_ATTR]
            
    def print_stats(self):
        print 'Graph Stats:'
        print 'Number of nodes: %d' % self.get_num_nodes()
        print 'Number of sources: %d' % (len(self.sources[PLAYER_WHITE]) + len(self.sources[PLAYER_BLACK]))
        print 'Number of sinks: %d' % (len(self.sinks[PLAYER_WHITE]) + len(self.sinks[PLAYER_BLACK]))
        total_edges = 0
        for node_id in range(self.get_num_nodes()):
            for roll in self.all_rolls:
                roll_index = roll - self.roll_offset
                for action in self.all_actions:
                    if self.successors[node_id][roll_index][action] is not None:
                        total_edges += 1
        print 'Number of edges: %d' % total_edges

    @classmethod
    def print_graph_info(cls, exp_params):
        g = StateGraph.load(exp_params)
        g.print_stats()
        print '-----------'
        g.print_all_edges()
        print '-----------'
        num_nodes = len(g.node_names)
        for node_id in range(num_nodes):
            print node_id, 'color:', g.node_colors[node_id], g.node_attrs[node_id]
        print '-----------'
#        for node_id in range(10):
#            print node_id, g.node_attrs[node_id]
#        print '-----------'
#        for node_id in range(num_nodes - 10, num_nodes):
#            print node_id, g.node_attrs[node_id]
#        print '-----------'
        print 'White\'s win probability is: %s' % g.node_attrs[0][VAL_ATTR] 
#        print 'Dice volatility is: %s' % g.compute_dice_volatility(exp_params) 
#        print 'Action volatility is: %s' % g.compute_action_volatility(exp_params) 

def test_graph():
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

if __name__ == '__main__':
    exp_params = ExpParams.get_exp_params_from_command_line_args()
    StateGraph.print_graph_info(exp_params)
    
    