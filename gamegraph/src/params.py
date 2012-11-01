'''
Created on Sep 11, 2012

@author: reza
'''
#--------------------------------------------------------------------

MAX_MOVES_PER_GAME = 200

NUM_TRIALS = 10

#NUM_STATS_GAMES = 10000
NUM_STATS_GAMES = 10000

COLLECT_STATS = False
SAVE_STATS = False
#COLLECT_STATS = True
#SAVE_STATS = True

PRINT_GAME_RESULTS = False
PRINT_GAME_DETAIL = False
#PRINT_GAME_RESULTS = True
#PRINT_GAME_DETAIL = True

ALTERNATE_SEATS = True
#ALTERNATE_SEATS = False
USE_SEEDS = ALTERNATE_SEATS

#CHOOSE_ROLL_P = 1.0

GENERATE_GRAPH_REPORT_EVERY_N_STATES = 1000
RECORD_GRAPH = False

EVAL_OPPONENT_RANDOM = 'EVAL_OPPONENT_RANDOM'
EVAL_OPPONENT_SARSA = 'EVAL_OPPONENT_SARSA'
EVAL_OPPONENT_OPTIMAL = 'EVAL_OPPONENT_OPTIMAL'
EVAL_OPPONENT = EVAL_OPPONENT_OPTIMAL

VALUE_ITER_MIN_RESIDUAL = 0.0001

EXP_BACK_RANGE = [100, 90, 50, 10, 0]
EXP_CHOOSEROLL_RANGE = ['0.0', '0.1', '0.5', '0.9', '1.0']

#--------------------------------------------------------------------

NTD_NUM_ITERATIONS = 500
NTD_NUM_TRAINING_GAMES = 128 # 64
NTD_NUM_EVAL_GAMES = 1024

NTD_GAMMA = 1.0
NTD_ALPHA = 1.0
NTD_EPSILON = 0.05
NTD_LAMBDA = 0.7

NTD_NETWORK_INIT_WEIGHTS = None

NTD_TRAIN_EPOCHS = 1
NTD_LEARNING_RATE = 0.1

NTD_USE_ALPHA_ANNEALING = False

#--------------------------------------------------------------------

SARSA_GAMMA = 1.0
SARSA_ALPHA = 0.1
SARSA_EPSILON = 0.05
SARSA_LAMBDA = 0.90

SARSA_USE_ALPHA_ANNEALING = True
SARSA_MIN_ALPHA = 0.05

SARSA_OPTIMISTIC_INIT = True

SARSA_NUM_TRAINING_ITERATIONS = 100
SARSA_NUM_EPISODES_PER_ITERATION = 5000
SARSA_NUM_EVAL_EPISODES = 1024

SARSA_TRAIN_AGAINST_SELF = True

SARSA_SAVE_TABLES = True
#SARSA_SAVE_STATE_VALUES_IN_GRAPH = False

#--------------------------------------------------------------------

HC_NUM_GENERATIONS = 1000
#HC_NUM_GENERATIONS = 5

HC_NUM_CHALLENGE_GAMES = 6
HC_CHALLENGER_NEEDS_TO_WIN = 5
HC_NUM_EVAL_GAMES = 1024
HC_EVALUATE_EVERY_N_GENERATIONS = 10

HC_RATIO_KEEP_CHAMPION_WEIGHTS = 0.95
HC_MUTATE_WEIGHT_SIGMA = 0.22 # 0.05

#--------------------------------------------------------------------

GAMESET_PROGRESS_REPORT_EVERY_N_GAMES = SARSA_NUM_TRAINING_ITERATIONS / 1000
GAMESET_RECENT_WINNERS_LIST_SIZE = 3000
GAMESET_PROGRESS_REPORT_USE_GZIP = False

