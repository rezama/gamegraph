'''
Created on Sep 11, 2012

@author: reza
'''
NUM_TRIALS = 10

NUM_STATS_GAMES = 10000

COLLECT_STATS = False
SAVE_STATS = False

PRINT_GAME_DETAIL = False
PRINT_GAME_RESULTS = False
#PRINT_GAME_DETAIL = True
#PRINT_GAME_RESULTS = True

ALTERNATE_SEATS = True
#ALTERNATE_SEATS = False
USE_SEEDS = ALTERNATE_SEATS

GAMESET_RECENT_WINNERS_LIST_SIZE = 3000
GAMESET_PROGRESS_REPORT_EVERY_N_GAMES = 10000
GAMESET_PROGRESS_REPORT_USE_GZIP = True

GENERATE_GRAPH_REPORT_EVERY_N_STATES = 1000
RECORD_GRAPH = False

#--------------------------------------------------------------------

#TD_NUM_ITERATIONS = 200
#TD_NUM_TRAINING_GAMES = 16 # 64
#TD_NUM_EVAL_GAMES = 1024
TD_NUM_ITERATIONS = 300
TD_NUM_TRAINING_GAMES = 16 # 64
TD_NUM_EVAL_GAMES = 512

TD_GAMMA = 1.0
TD_ALPHA = 1.0
TD_EPSILON = 0.05
TD_LAMBDA = 0.7

TD_TRAIN_EPOCHS = 1
TD_LEARNING_RATE = 0.1

TD_USE_ALPHA_ANNEALING = False

#--------------------------------------------------------------------

RL_GAMMA = 1.0
RL_ALPHA = 0.1
RL_EPSILON = 0.05
RL_LAMBDA = 0.90

RL_USE_ALPHA_ANNEALING = True
RL_MIN_ALPHA = 0.05

RL_NUM_ITERATIONS = 1024 * 200000
RL_NUM_FINAL_EVAL = 1024

RL_SAVE_TRIAL_DATA = True

RL_SAVE_TABLES = False

RL_TRAIN_AGAINST_SELF = False

RL_SAVE_STATE_VALUES_IN_GRAPH = True

#--------------------------------------------------------------------

HC_NUM_GENERATIONS = 500
HC_NUM_CHALLENGE_GAMES = 8
HC_CHALLENGER_NEEDS_TO_WIN = 7
HC_NUM_EVAL_GAMES = 1024
HC_EVALUATE_EVERY_N_GENERATIONS = 10

HC_RATIO_KEEP_CHAMPION_WEIGHTS = 0.95
HC_MUTATE_WEIGHT_SIGMA = 0.22 # 0.05
