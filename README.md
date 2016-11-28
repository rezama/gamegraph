# GameGraph

This codebase contains tools to study the impact of domain stochasticity and ergodicity on efficiency of Reinforcement Learning in board games through self-play.  It explores the hypothesis that RL through self-play works better in domains that are more stochastic and more ergodic.

![Minigammon Game Board](/minigammon.png?raw=true "Minigammon Game Board")

The implementation contains three learning algorithms:

  - Sarsa(λ) + neural network function approximation
  - Tabular Sarsa(λ)
  - Hill Climbing as a simple evolutionary algorithm

### Learning and Evaluation

The learning algorithms go though a number of iterations.  Every iteration consists of two phases:

1. The learning agent plays a number of evaluation games against an optimal player for the given domain.  The optimal agent is created using *Value Iteration*.  The agents play both as white and as black during the evaluation games.
2. The learning agent plays a number of training games against itself.

### Games as Stochastic Graphs

Games are represented as stochastic graphs where the nodes represent particular game states and the edges represents actions available to the players.  An implementation for the following games are included:

  - Minigammon: A tiny version of backammon.
  - Variants of Minigammon: Midgammon (larger board), Nohitgammon (hitting is not allowed).
  - Nannon: Tiny backgammon designed by JB Pollack.
  - [Nim](http://en.wikipedia.org/wiki/Nim)

### Varying Stochasticity

The stochasticity of domains is controlled by the `--chooseroll` flag.  It determines the probability that a player is free to set their desired dice roll on their turn.  Setting `--chooseroll=0.0` (default) results in games where dice rolls are always chosen randomly.  Setting `--chooseroll=1.0` results in fully-deterministic dice rolls.

In this approach, stochasticity is varied by controlling the randomness of dice rolls.  This is different from the more common approach where stochasticity is implemented as randomeness in the outcome of moves.

### Varying Ergodicity

An ergodic MDP is defined to be an MDP in which every state can be reached from every other state.  We use a relaxed definition of ergodicity leading to a measure of *degree of ergodicity*, which is defined as the average likelihood of revisiting game states.

The degree of ergodicity in backgammon-like domains can be varied through different mechanisms:

  - Using `--offset=n`: Changes the reentry position for checkers that are hit and need to reenter the game.  By default they enter from the end of the board (`offset=0`).  Setting higher values will cause checkers to enter from later positions, reducing the likelihood of future fights and thereby reducing the degree of ergodicity in the domain.
  - Using `--graph=path/to/graph/file`: In this approach, the degree of ergodicity can be modified by directly modifying the state tranistion graph of the game.  The `manip_graph.py` utility can trim a requested percentage of back edges (as defined in Depth-First-Search) from the state transition graph of a game and save the modified graph to disk.  Removing the back edges reduces the degree of ergodicity in the domain.  When `--graph` is used, the actions that are available to the players are limited to the edges that are present in the active graph.  Therefore, the learning algorithms are trained to play the modified game which is defined by the supplied state transition graph.

### Usage Examples

Invoke the following commands from inside the `src` directory:

```sh
# Runs the tabular Sarsa algorithm on Minigammon.
$ python app_sarsa.py --domain=minigammon
```

```sh
# Runs the Neural-network-based Sarsa algorithm on Minigammon with 80% deterministic dice rolls:
$ python app_ntd.py --domain=minigammon --chooseroll=0.8
```

```sh
# Runs the hill climbing algorithm on Minigammon:
$ python app_hc.py --domain=minigammon
```

```sh
# Runs the Neural-network-based Sarsa algorithm on standard Nim with fully-deterministic dice rolls:
$ python app_ntd.py --domain=nim --chooseroll=1.0
```

```sh
# Runs games between optimal agents trained using value iteration.
$ python app_optimal.py --domain=nim --chooseroll=1.0
```

```sh
# Runs games between agents making random moves.
$ python app_random.py --domain=nim --chooseroll=1.0
```

```sh
# Generate graphs for modified versions of Minigammon with varying degrees of ergodicity.
$ python manip_graph.py --domain=minigammon
# Train a neural-network-based agent on one of the generated graphs.
$ python app_ntd.py --domain=minigammon --graph=minigammon-822-back-50
```

### Requirements

- PyBrain (included in `gamegraph/lib/`)
