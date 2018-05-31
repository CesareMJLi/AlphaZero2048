'''
train the differnt computing model
'''

from __future__ import print_function
import random
import numpy as np
from collections import defaultdict, deque
from game import board, game

from mcts_player import mctsPlayer
# from mcts_alphaZero import mctsAZPlayer
# from policy_value_net import policyValueNet

class TrainPipeline():
    def __init__(self, init_model=None):
        self.board = board()
        self.game = game(self.board)
        # Training parameter
        self.learn_rate = 2e-3
        self.lr_multiplier = 1.0
        self.temp = 1.0
        self.n_playout = 400
        self.c_puct = 5
        self.buffer_size = 10000
        self.batch_size = 512
        self.data_buffer = deque(maxlen = self.buffer_size)
        self.play_batch_size = 1
        self.epochs = 5
        self.kl_targ = 0.02
        self.check_freq = 50
        self.game_batch_num = 1500
        self.best_win_ratio = 0.0

        # num of simulations used for pure mcts
        self.pure_mcts_playout_num = 1000
        if init_model:
            # start from an existing policy value net
            self.policy_value_net = PolicyValueNet(model_file = init_model)
        else:
            self.policy_value_net = PolicyValueNet()

        # self.mcts_player = mctsAZPlayer()

    def get_equiv_data(self, play_data):
        '''since the board could be mirrored or flipped, while the actual
        problem we are going to solve would not change'''
        extend_data = []
        for state, mcts_prob, winner in play_data:
            for i in [1,2,3,4]:
                # rotate counterclockwise
                equi_state = np.array([np.rot90(s,i) for s in state])
                equi_mcts_prob = np.rot90(np.flipud(
                    mcts_prob.reshape(self.board_height, self.board_width)),
                    extend_data.append((equi_state,np.flipud(equi_mcts_prob).flatten(),winner)))
                # flip horizontally
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)

                extend_data,append((equi_state, np.flipud(equi_mcts_prob).flatten(),winner))

        return extend_data

    def collect_selfplay_data(self, n_games = 1):
        '''collect self-play data for training'''
        for _ in range(n_games):
            winner, play_data = self.game.start_ai_play(self.mcts_player, temp= self.temp)
            play_data = list(play_data)[:]
            self.episode_len = len(play_data)
            play_data = self.get_equiv_data(play_data)
            self.data_buffer.extend(play_data)