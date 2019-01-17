# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 22:44:13 2018

@author: Mclovin
"""
import sys
from random import randint
import datetime
import wx;

class Node:
    def __init__(self, x, y, black, alive):
        self.x = x
        self.y = y
        self.isBlack = black
        self.isAlive = alive
        
    def position(self):
        return (self.x, self.y)
    
    def getAlive(self):
        return self.isAlive
    
    def setAlive(self, alive):
        self.isAlive = alive
    
    def isBlack(self):
        return self.isBlack
    
    def print_node(self):
        if self.isAlive:
            if self.isBlack:
                return '#'
            else:
                return 'o'
        else:
            return ' '
    def copy_node(self):
        new_node = Node(self.x, self.y, self.isBlack, self.isAlive)
        return new_node

class Game:
    def __init__(self, parent = None):
        self.evaluation_ct = 0
        self.branching_ct = 0
        self.node_ct = 0
        self.cutoff_ct = 0

        self.total_time = datetime.datetime.now()
        self.total_step = 0

        if parent is None:
            self.board = self.init_board()
            self.last_board = parent
        else:
            self.board = self.copy_board(parent.get_board())
            self.last_board = parent
            
    def get_board(self):
        return self.board
    
    def get_parent(self):
        return self.last_board
        
        
    def copy_board(self, cp):
        board = []
        for i in range(8):
            row = []
            for j in range(8):
                row.append(cp[i][j].copy_node())
            board.append(row)
        return board


    def init_board(self):
        #an array of rows
        board = []
        for i in range(8):
            row = []
            for j in range(8):
                if (i + j)%2 == 0:
                    black = True
                else:
                    black = False
                row.append(Node(i, j, black, True))
            board.append(row)
        return board
    
    def print_board(self, board):
        for i in range(8):
            for j in range(8):
                print(board[i][j].print_node()),
            print('\n')
        
    #x is row, y is col
    def remove_token(self, x, y, board):
        board[x][y].isAlive = False
        
    def jump(self, board, x1, y1, x2, y2):
        start = board[x1][y1]
        victim = board[(x1+x2)/2][(y1+y2)/2]
        end = board[x2][y2]
        if start.isAlive and victim.isAlive and not end.isAlive:
            board[x1][y1].setAlive(False)
            board[(x1+x2)/2][(y1+y2)/2].setAlive(False)
            board[x2][y2].setAlive(True)
            return board
        else:
            #print('Invalid action: from ', x1, ' ', y1, ' to ', x2, ' ', y2)
            return None


        
    #helper function for find legal action     
    def look(self, board, x, y):
        candidates = []
        if (x - 2) >= 0:
            if board[x-2][y].isAlive and board[x-1][y].isAlive:
                candidates.append(((x-2, y), (x, y)))
        if (x + 2) <= 7:
            if board[x+2][y].isAlive and board[x + 1][y].isAlive:
                candidates.append(((x+2, y), (x, y)))
        if (y - 2) >= 0:
            if board[x][y-2].isAlive and board[x][y - 1].isAlive:
                candidates.append(((x, y-2), (x, y)))
        if (y + 2) <= 7:
            if board[x][y+2].isAlive and board[x][y + 1].isAlive:
                candidates.append(((x, y+2), (x, y)))
        return candidates
        
        
    def find_legal_action(self, board, black):
        candidates = []
        for i in range(8):
            for j in range(8):
                if board[i][j].isBlack == black:
                    if not board[i][j].isAlive:
                        candidates.extend(self.look(board, i, j))
        return candidates
        
            
    def evaluation(self, child, black):
        black_actions = self.find_legal_action(child, True)
        white_actions = self.find_legal_action(child, False)
        black_ct = 0
        white_ct = 0
        board = self.copy_board(child)
        for black_action in black_actions:
            x1 = black_action[0][0]
            y1 = black_action[0][1]
            x2 = black_action[1][0]
            y2 = black_action[1][1]
            temp = self.jump(board, x1, y1, x2, y2)
            if temp is not None:
                black_ct = black_ct + 1    
                board = temp
        board = self.copy_board(child)
        for white_action in white_actions:
            x1 = white_action[0][0]
            y1 = white_action[0][1]
            x2 = white_action[1][0]
            y2 = white_action[1][1]
            temp = self.jump(board, x1, y1, x2, y2)
            if temp is not None:
                white_ct = white_ct + 1   
                board = temp
        if not black and white_ct == 0:
            return (True, black_ct - white_ct)
        if black and black_ct == 0:
            return (True, black_ct - white_ct)
        return (False, black_ct - white_ct)
        
    
    # alpha beta pruning with forward pruning
    def minimax_fp(self, n, level, black, alphabeta):
        if black:
            (v, action) = self.maxVal_fp(n, -sys.maxint - 1, sys.maxint, level, alphabeta)
        else:
            (v, action) = self.minVal_fp(n, -sys.maxint - 1, sys.maxint, level, alphabeta)
        return (v, action)
        
    # max(blackMove-whiteMove) for BLACK
    def maxVal_fp(self, n, alpha, beta, level, alphabeta):
        eval = self.evaluation(n, True)
        self.evaluation_ct = self.evaluation_ct + 1
        if eval[0] or level == 0:
            # return evaluation function value
            if eval[0]:
                self.evaluation_ct = self.evaluation_ct - 1
            return (eval[1], None)

        self.node_ct = self.node_ct + 1
        # explore children and prune
        v = -sys.maxint - 1
        current_best_move = None
        legal_actions = self.find_legal_action(n, True)
        self.branching_ct = self.branching_ct + len(legal_actions)
        children = []
        for action in legal_actions:
            child = self.jump(self.copy_board(n), action[0][0],action[0][1],action[1][0],action[1][1])
            if child is not None:  
                children.append((child, action, self.evaluation(child, True)[1]))
        children = sorted(children, key = lambda x: x[2])

        children = list(reversed(children))
        #print [i[2] for i in children]
        good_children = children[0: len(children)]        
        for child in good_children: 
                this_value = self.minVal_fp(child[0], alpha, beta, level-1, alphabeta)[0]
                if  this_value > v:
                    v = this_value
                    if not alphabeta:
                        current_best_move = child[1]               
                if alphabeta:
                    if v >= beta:
                        self.cutoff_ct = self.cutoff_ct + 1
                        return (v, child[1] )
                    if v > alpha :
                        alpha = v
                        current_best_move = child[1] 
     
        return (v, current_best_move)
    
    # min(blackMove-whiteMove) for WHITE
    def minVal_fp(self, n, alpha, beta, level, alphabeta):
        eval = self.evaluation(n, False)
        self.evaluation_ct = self.evaluation_ct + 1
        if eval[0] or level == 0:
            if eval[0]:
                self.evaluation_ct = self.evaluation_ct - 1
            return (eval[1], None)
        # other restriction
        self.node_ct = self.node_ct + 1
        # explore children and prune
        v = sys.maxint
        current_best_move = None
        legal_actions = self.find_legal_action(n, False)
        self.branching_ct = self.branching_ct + len(legal_actions)
        children = []
        for action in legal_actions:
            child = self.jump(self.copy_board(n), action[0][0],action[0][1],action[1][0],action[1][1])
            if child is not None:  
                children.append((child, action, self.evaluation(child, True)[1]))
        children = sorted(children, key = lambda x: x[2])

        good_children = children[0:len(children)]       
        for child in good_children: 
                this_value = self.maxVal_fp(child[0], alpha, beta, level-1, alphabeta)[0]
                if  this_value < v:
                    v = this_value
                    if not alphabeta:
                        current_best_move = child[1]
                if alphabeta:
                    if v <= alpha:
                        self.cutoff_ct = self.cutoff_ct + 1
                        return (v, child[1])
                    if v < beta:           
                        beta = v
                        current_best_move = child[1]
        return (v, current_best_move)
    
    
    # alpha beta pruning
    def minimax(self, n, level, black, alphabeta):
        if black:
            (v, action) = self.maxVal(n, -sys.maxint - 1, sys.maxint, level, alphabeta)
        else:
            (v, action) = self.minVal(n, -sys.maxint - 1, sys.maxint, level, alphabeta)
        return (v, action)
        
    # max(blackMove-whiteMove) for BLACK
    def maxVal(self, n, alpha, beta, level, alphabeta):
        eval = self.evaluation(n, True)
        self.evaluation_ct = self.evaluation_ct + 1
        if eval[0] or level == 0:
            # return evaluation function value
            if eval[0]:
                self.evaluation_ct = self.evaluation_ct - 1
            return (eval[1], None)

        self.node_ct = self.node_ct + 1
        # explore children and prune
        v = -sys.maxint - 1
        current_best_move = None
        legal_actions = self.find_legal_action(n, True)
        self.branching_ct = self.branching_ct + len(legal_actions)

        for action in legal_actions:
            child = self.jump(self.copy_board(n), action[0][0],action[0][1],action[1][0],action[1][1])
            if child is not None:  
                this_value = self.minVal(child, alpha, beta, level-1, alphabeta)[0]
                if  this_value > v:
                    v = this_value
                    if not alphabeta:
                        current_best_move = action               
                if alphabeta:
                    if v >= beta:
                        self.cutoff_ct = self.cutoff_ct + 1
                        return (v, action)
                    if v > alpha :
                        alpha = v
                        current_best_move = action
                  
        return (v, current_best_move)
    
    # min(blackMove-whiteMove) for WHITE
    def minVal(self, n, alpha, beta, level, alphabeta):
        eval = self.evaluation(n, False)
        self.evaluation_ct = self.evaluation_ct + 1
        if eval[0] or level == 0:
            if eval[0]:
                self.evaluation_ct = self.evaluation_ct - 1
            return (eval[1], None)
        # other restriction
        self.node_ct = self.node_ct + 1
        # explore children and prune
        v = sys.maxint
        current_best_move = None
        legal_actions = self.find_legal_action(n, False)
        self.branching_ct = self.branching_ct + len(legal_actions)

        for action in legal_actions:
            child = self.jump(self.copy_board(n), action[0][0],action[0][1],action[1][0],action[1][1])
            if child is not None:
                this_value = self.maxVal(child, alpha, beta, level-1, alphabeta)[0]
                if  this_value < v:
                    v = this_value
                    if not alphabeta:
                        current_best_move = action
                if alphabeta:
                    if v <= alpha:
                        self.cutoff_ct = self.cutoff_ct + 1
                        return (v, action)
                    if v < beta:           
                        beta = v
                        current_best_move = action
        return (v, current_best_move)
    
    def get_user_action(self, board, user_action):
        a_list = user_action.split()
        if len(a_list) != 4:
            print ('invalid user input')
            return board
        else:
            return self.jump(board, int(a_list[0])-1,int(a_list[1])-1, int(a_list[2])-1, int(a_list[3])-1)

    def e_v_e(self, board, level, alphabeta):
        #self.first_move_black(board)
        #self.first_move_white(board)
        self.remove_token(3, 3, board)
        self.remove_token(3,4,board)
        # self.total_time = datetime.datetime.now()
        # print(self.total_time)
        #self.print_board(board)
        x = 0
        black = True
        while x == 0:
            if black:
                a = (datetime.datetime.now())
                (v, action) = self.minimax(board, level, black, alphabeta)
                #print("Black: ")
                #a1 = datetime.datetime.now()-a
                #print(a1)
                #self.total_step = self.total_step + 1
                #self.total_time = self.total_time + a1
            if not black:
                b = (datetime.datetime.now())
                (v, action) = self.minimax_fp(board, level, black, alphabeta)
                #print("White: ")
                #b1 = datetime.datetime.now()-b
               # print(b1)
                #self.total_step = self.total_step + 1
               # self.total_time = self.total_time + b1
            if action == None:
                if black:
                    print('White won!')
                else:
                    print('Black won!')
                x = 1
            else:
                board = self.jump(board, action[0][0], action[0][1], action[1][0], action[1][1])
                black = not black
        #self.print_board(board)

    # user is black/white
    def p_v_e(self, board, black, alphabeta):
        x = 0
        human = black
        while x == 0:
            if human:
                my_action = raw_input("my_action: ")               
                if my_action == "0":
                    print('Computer wins!')
                    x = 1
                    break
                if (len(my_action.split()) != 4):
                    x = 1
                else:
                    board = self.get_user_action(board, my_action)
                    (v, action) = self.minimax(new_board, 2, not black, alphabeta)
                    self.convert_action(action[0][0], action[0][1], action[1][0], action[1][1])
                    if action == None:
                        print('Human wins!')
                        x = 1
                    else:
                        board = self.jump(board, action[0][0], action[0][1], action[1][0], action[1][1])
                        self.print_board(board)
            else:
                (v, action) = self.minimax(new_board, 2, not black, alphabeta)
                self.convert_action(action[0][0], action[0][1], action[1][0], action[1][1])
                if action == None:
                    print('Human wins!')
                    x = 1
                else:
                    board = self.jump(board, action[0][0], action[0][1], action[1][0], action[1][1])
                    self.print_board(board)
                human = not human
    
    def convert_action(self, x1, y1, x2, y2):
        print (x1+1," ",y1+1," ",x2+1," ",y2+1)
    
    def first_move_white(self, board):
        possible_pick = []
        for i in range (8):
            for j in range (8):
                if not board[i][j].isAlive:
                    if i - 1 > 0:
                        possible_pick.append((i-1,j))
                    if i + 1 < 7:
                        possible_pick.append((i+1,j))
                    if j -1 > 0:
                        possible_pick.append((i,j-1))
                    if j + 1 < 7:
                        possible_pick.append((i,j+1))       
        x = randint(0, len(possible_pick)-1)
        self.remove_token(possible_pick[x][0],possible_pick[x][1], board)
        return board
            
    def first_move_black(self, board):
       possible_pick = [(3,3), (4, 4)]
       x = randint(0, len(possible_pick)-1)
       self.remove_token(possible_pick[x][0],possible_pick[x][1], board)
       return board
            
    def start_game(self, new_board):
       human_side = raw_input("Pick your side: B/W\n")
       if human_side == 'B':
           human_action = raw_input("first_pick: x1 y1\n")
           h_action = human_action.split()
           if len(h_action) == 2:
               self.remove_token(int(h_action[0])-1, int(h_action[1])-1, new_board)
               new_board = self.first_move_white(new_board)
               self.print_board(new_board)
               self.p_v_e(new_board,True, True)
           else:
               print 'Invalid input'
       elif human_side == 'W':
           new_board = self.first_move_black(new_board)
           self.print_board(new_board)
           human_action = raw_input("your_pick: x1 y1\n")
           h_action = human_action.split()
           if len(h_action) == 2:
               self.remove_token(int(h_action[0])-1, int(h_action[1])-1, new_board)
               self.p_v_e(new_board,False, True)
           else:
               print 'Invalid input'

                            
        
#________________________________________________________________#        
a=wx.App(); wx.Frame(None, title="Hello World").Show(); a.MainLoop()
myBoard = Game()
new_board = myBoard.init_board()
#myBoard.start_game(new_board)
i = 4
print('Level ',i)
#a = (datetime.datetime.now())
myBoard.e_v_e(new_board, i, True)

#print(datetime.datetime.now()-a)
#print('Evaluation Count: ',myBoard.evaluation_ct)
#print('Branching Factor: ',myBoard.branching_ct/float(myBoard.node_ct))
#print('Cutoff Count: ',myBoard.cutoff_ct)
#print('Total timeL', myBoard.total_time)
#print('Total step', myBoard.total_step)
#print('Average time', myBoard.total_time/myBoard.total_step)




