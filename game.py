
from __future__ import print_function
import numpy as np
import random

class board(object):
    def __init__(self):
        self.actions_available = [0,1,2,3]
        self.width = 4
        self.height = 4
        self.state = {}
        self.availables = []
        self.last_move = -1

    def initialize_state(self):
        # self.state = {
        #     0:8, 1:2, 2:4, 3:4,
        #     4:8, 5:0, 6:0, 7:0,
        #     8:4, 9:0, 10:2, 11:4,
        #     12:2, 13:2, 14:0, 15:0,
        # }
        self.state = {
            0:0, 1:0, 2:0, 3:0,
            4:0, 5:0, 6:0, 7:0,
            8:0, 9:0, 10:0, 11:0,
            12:0, 13:0, 14:0, 15:0,
        }

    # "move" expression inherit the method used in gomoku
    # it is a representation of a location in one integer number
    def move_to_location(self, move):
        h = move // self.width
        w = move % self.width
        return [h,w]

    def location_to_move(self, location):
        if len(location)!= 2:
            return -1
        move = location[0] * self.width + location[1]
        if move not in range(self.width * self.height):
            return -1
        return move

    def current_state(self):
        # state is a dictionary, the key is the moves
        # while the value is the value at the location of the move
        return self.state

    def update_availables(self):
        self.availables = []
        for pos, val in self.state.items():
            if val==0:
                self.availables.append(pos)
        
    def generateNew(self):
        availables = []
        for pos, value in self.state.items():    # for name, age in list.items():  (for Python 3.x)
            if value == 0:
                availables.append(pos)
        if len(availables)>0:
            # new_moves make the positiion for the new 2
            new_move = random.choice(availables)
            new_val = random.choice([0,1])
            if new_val==0:
                self.state[new_move]=2
            else:
                self.state[new_move]=4
        self.update_availables()

    def game_end(self):
        values = self.state.values()
        countZero = 0
        for i in values:
            if i==512:
                return True, 1
            if i==0:
                countZero+=1
        if countZero == 0:
            # if the board is full while the game still has not come to an end
            # we would have to check whether for a pair of elements, there
            # exists a pair of equal elements
            moves = self.state.keys()
            for i in moves:
                if i<4 :
                    res = self.checkCol(i)
                    if not res:
                        return True, -1
                if i%4 == 0:
                    res = self.checkRow(i)
                    if not res:
                        return True, -1
        return False, 0
        
    def checkCol(self, ind):
        nextInd = ind+4
        while nextInd < 16:
            if self.state[ind] == self.state[nextInd]:
                return True
            ind+=4
            nextInd+=4
        return False

    def checkRow(self, ind):
        nextInd = ind+1
        while nextInd%4!=0:
            if self.state[ind] ==  self.state[nextInd]:
                return True
            ind+=1
            nextInd+=1
        return False
    
    def moveUp(self):
        # divide the move function into two steps
        # 1. check each row whether there is two elements could be combined
        # 2. move the combined elements
        elements = self.state.keys()
        # combine
        for i in reversed(elements):
            if i<4:
                break
            else:
                if self.state[i]==self.state[i-4]:
                    self.state[i]=2*self.state[i]
                    self.state[i-4]=0
                elif i>7 and self.state[i]==self.state[i-8] and self.state[i-4]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i-8]=0
                elif i>11 and self.state[i]==self.state[i-12] and self.state[i-4]==0 and self.state[i-8]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i-12]=0
        # move
        for i in reversed(elements):
            if i>11:
                continue
            else:
                if self.state[i]==0:
                    continue
                else:
                    while i+4<16:
                        if self.state[i+4]==0:
                            self.state[i+4]=self.state[i]
                            self.state[i]=0
                            i+=4
                        else: break
        self.update_availables()

    def moveLeft(self):
        elements = self.state.keys()
        # combine
        for i in elements:
            if i%4 == 3:
                continue
            else:
                if self.state[i]==self.state[i+1]:
                    self.state[i]=2*self.state[i]
                    self.state[i+1]=0
                elif (i%4==0 or i%4==1) and self.state[i]==self.state[i+2] and self.state[i+1]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i+2]=0
                elif i%4==0 and self.state[i]==self.state[i+3] and self.state[i+1]==0 and self.state[i+2]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i+3]=0
        # move
        for i in elements:
            if i%4 == 0:
                continue
            else:
                if self.state[i]==0:
                    continue
                else:
                    while (i-1)%4!=3:
                        if self.state[i-1]==0:
                            self.state[i-1]=self.state[i]
                            self.state[i]=0
                            i-=1
                        else: break
        self.update_availables()
   
    def moveDown(self):
        elements = self.state.keys()
        # combine
        for i in elements:
            if i>=12:
                break
            else:
                if self.state[i]==self.state[i+4]:
                    self.state[i]=2*self.state[i]
                    self.state[i+4]=0
                elif i<8 and self.state[i]==self.state[i+8] and self.state[i+4]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i+8]=0
                elif i<4 and self.state[i]==self.state[i+12] and self.state[i+4]==0 and self.state[i+8]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i+12]=0
        # move
        for i in elements:
            if i<4:
                continue
            else:
                if self.state[i]==0:
                    continue
                else:
                    while i-4>=0:
                        if self.state[i-4]==0:
                            self.state[i-4]=self.state[i]
                            self.state[i]=0
                            i-=4
                        else: break
        self.update_availables()

    def moveRight(self):
        elements = self.state.keys()
        # combine
        for i in reversed(elements):
            if i%4 == 0:
                continue
            else:
                if self.state[i]==self.state[i-1]:
                    self.state[i]=2*self.state[i]
                    self.state[i-1]=0
                elif (i%4==3 or i%4==2) and self.state[i]==self.state[i-2] and self.state[i-1]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i-2]=0
                elif i%4==3 and self.state[i]==self.state[i-3] and self.state[i-1]==0 and self.state[i-2]==0:
                    self.state[i]=2*self.state[i]
                    self.state[i-3]=0
        # move
        for i in reversed(elements):
            if i%4 == 3:
                continue
            else:
                if self.state[i]==0:
                    continue
                else:
                    while (i+1)%4!=0:
                        if self.state[i+1]==0:
                            self.state[i+1]=self.state[i]
                            self.state[i]=0
                            i+=1
                        else: break
        self.update_availables()
            




class game(object):
    def __init__(self, board):
        self.board = board
        self.board.initialize_state()

    def graphic(self, board, player):
        """Draw the board and show game info"""
        width = board.width
        height = board.height

        print("Press W/A/S/D to move the numbers on the board to reach 2048")
        # print(board.availables)

        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(height - 1, -1, -1):     # print from top to the bottom
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.state[loc]
                if p==0:
                    print('_'.center(8), end='')
                else:
                    print(str(p).center(8), end = ' ')
            print('\r\n\r\n')

    def start_play(self, player, is_shown=1):
        if is_shown:
            self.board.generateNew()
            self.board.generateNew()
            self.board.generateNew()
            self.graphic(self.board, player)
        while True:
            player.get_action(self.board)
            self.board.generateNew()
            if is_shown:
                self.graphic(self.board, player)
            end, result = self.board.game_end()
            if end:
                if is_shown:
                    if result == 1:
                        print("Game end. You win! XD")
                    else:
                        print("Game end. You lose :(")