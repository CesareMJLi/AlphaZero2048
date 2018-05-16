

import numpy as np
import copy
from operator import itemgetter

def rollout_policy_fn(board):
    action_probs = np.random.rand(len(board.availables))
    return zip(board.availables, action_probs)

def policy_value_fn(board):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    action_probs = np.ones(len(board.availables))/len(board.availables)
    return zip(board.availables, action_probs), 0

class treeNode(object):
    def __init__(self, parent, prior_p):
        '''Parameters:
        value Q, prior probability P, visit-count-adjusted prior score u'''
        self.parent = parent
        self.children = {}
        self.n_visits = 0
        self.Q = 0
        self.P = prior_p
        self.u = 0

    def expand(self, action_probs):
        '''expand the tree to create new children from current state by differnt actions
        Parameters: action_priors a list of tuples of actions and their probability according to the policy function'''
        for action, prob in action_probs:
            if action not in self.children:
                self.children[action] = treeNode(self, prob)

    def select(self, c_puct):
        '''select action among the children which gives 
        maximum action value Q plus bonus u(P)
        return: A tuple of (action, next_node)
        c_puct: a number in (0, inf) controlling the relative impact of
        value Q, and prior probability P, on this node's score.

        here a potential condition is that at least one child node of current node exists.
        remember, each time we expand a node, we expand the node all the actions it could have
        so if we have one child nodes, we have all the child nodes'''
        return max(self.children.items(),
            key=lambda act_node: act_node[1].get_value(c_puct))
    
    def update(self, leaf_value):
        self.n_visits +=1
        self.Q += 1.0*(leaf_value - self.Q)/self.n_visits
        #---------------------------------
        # like for a MCTS 8/10->3/5->[0/1]
        # there are 10 plays and now we add a new 0/1 to the tree and its parent is 3/5
        # we should update the Q of 3/5 to be Q'=Q+1*(0/1-3/5)/(5+1)=3/6    updated!
        #---------------------------------

    def update_recursive(self, leaf_value):
        # a recursive root to leaves update starts from 8/10 in the same way to update it into 8/11
        if self.parent:
            self.parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior adjusted for its visit count, u.
        c_puct: a number in (0, inf) controlling the relative impact of value Q, and prior probability P, on this node's score.
        """
        self.u = (c_puct * self.P *
                   np.sqrt(self.parent.n_visits) / (1 + self.n_visits))
        return self.Q + self.u

    def is_leaf(self):
        return self.children == {}

    def is_root(self):
        return self.parent is None

class mctsTree(object):
    """A simple implementation of Monte Carlo Tree Search."""
    # after initialization
    # given current state, get the move for current state
    # it means in the given num of playouts, do a tree search
    # and return the best choice in the current situation and move root
    # both _playou() and _evaluate_rollout() serve get_move

    def __init__(self, policy_value_fn, c_puct=5, n_playout=1000):
        # the original n_playout = 10000
        """
        policy_value_fn: a function that takes in a board state and outputs
            a list of (action, probability) tuples and also a score in [-1, 1]
            (i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct: a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self.root = treeNode(None, 1.0)
        self.policy = policy_value_fn
        self.c_puct = c_puct
        self.n_playout = n_playout

    def _playout(self, state):
        """Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self.root
        # now the root is current board situation
        while(1):
            if node.is_leaf():
                break
            # Greedily select next move. until it reaches a leaf
            action, node = node.select(self.c_puct)
            state.do_move(action)

        # here reaches the end of tree but still maybe not end of the game
        # Check for end of game
        end, winner = state.game_end()
        action_probs, _ = self.policy(state)

        # according to the current state, derive a set of probabilities for each action
        # in this example, it's like a tuple of {w:0.1, a:0.2, s:0.3, d:0.4}
        if not end:
            # use the previous derived prob to expand the current leaf
            # like for each action build one child-node
            node.expand(action_probs)

        # Evaluate the leaf node by random rollout
        leaf_value = self._evaluate_rollout(state)
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)

    def _evaluate_rollout(self, state, limit=1000):
        # rollout operation for each possible state of the nodes just expanded
        """Use the rollout policy to play until the end of the game,
        returning 1 if the player win the game, 0 if he lost it.
        """
        # this is for one single MCTS process, do the random play
        for i in range(limit):
            end, result = state.game_end()
            if end:
                break
            action_probs = rollout_policy_fn(state)
            # this returns a set of [actions, probs]
            max_action = max(action_probs, key=itemgetter(1))[0]
            state.do_move(max_action)
            # take this action and continue unitl game end or out of limit
        else:
            # If no break from the loop, issue a warning.
            print("WARNING: rollout reached move limit")
        return result

    def get_move(self, state):
        """Runs all playouts sequentially and returns the most visited action.
        state: the current game state
        Return: the selected action
        """
        for n in range(self.n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)
            # play out is the core operation:
            # it includes selection/expansion/simulation/back propagation
        return max(self.root.children.items(),
                   key=lambda act_node: act_node[1].n_visits)[0]
                #  this is a beautiful expression of max(,key=lamba) format.
                #  https://stackoverflow.com/questions/18296755/python-max-function-using-key-and-lambda-expression

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know about the subtree."""
        if last_move in self.root.children:
            self.root = self.root.children[last_move]
            self.root.parent = None
        else:
            self.root = treeNode(None, 1.0)

    def __str__(self):
        # when print a class, the __str__ function is the content of the thing going to be printed out
        return "MCTS"

class mctsPlayer(object):
    """AI player based on MCTS"""
    def __init__(self, c_puct=5, n_playout=2000):
        self.mcts = mctsTree(policy_value_fn, c_puct, n_playout)

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board):
        end, result = board.game_end()
        if end:
            print("WARNING: the game is ended")
        else:
            move = self.mcts.get_move(board)
            self.mcts.update_with_move(move)
            return move