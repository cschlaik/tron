#!/usr/bin/python

import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue
from abcutoff import *
from copy import deepcopy
from dijkstra import *

# Throughout this file, ASP means adversarial search problem.

#BOTS VERSION 1.2
#new best is neighboring_tiles_eval_func
#wins ~30/40 times on python gamerunner.py -bots student ta1 -map maps/empty room.txt -multi test 15 -no image
#need to: modify ab_cutoff to include speed
#would be good to make all functions inside StudentBot

#BOTS VERSION 1.1
#moved ab_cutoff into imported file abcutoff.py – this seems to be working
#rewrote astar implementation – this is in imported file dijkstra.py

#BOTS VERSION 1.0
#added minimax ab_cutoff
#structured decide as call to ab_cutoff with either startgame or endgame eval_func
#skeleton start_eval_func
#end_eval_func based on distances and basic consideration of powerups
#distance function


CUTOFF_PLY = 8 #how many look-ahead for abcutoff

def manhattan_distance(loc1, loc2):
    '''
    calculates the Manhattan/taxicab distance pathlength between two cells.
    using this will APPROXIMATE what could be found with astar. 
    '''
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

def start_eval_func(asp, tron_gamestate):
    '''
    for startgame strategy,
        a function that takes in a Tron GameState and outputs
        a real number indicating how good that state is for the
        player who is using alpha_beta_cutoff to choose their action.

        (skeleton implementation) counts powerups that can be accessed
        from this location, increasing score for each.
        if there are no possibilities, returns -1

        ** trying to box in opponent
        ** avoid speed powerups
    '''
    locs = tron_gamestate.player_locs
    board = tron_gamestate.board
    ptm = tron_gamestate.ptm #the player to move
    loc = locs[ptm]
    possibilities = list(TronProblem.get_safe_actions(board, loc))
    if ptm == 0:  #the other player –– always only two?
        op = 1
    else:
        op = 0
    score = 0
    if possibilities:
        for action in possibilities:
            score += weight_cell(TronProblem.move(loc, action), op)
        return score
    return float("-inf")

def pathlengths_eval_func(asp, tron_gamestate):
    '''
    for endgame strategy,
        a function that takes in a Tron GameState and outputs
        a real number indicating how good that state is for the
        player who is using alpha_beta_cutoff to choose their action.

        assigns this number based on the number of cells ptm can reach before the 
        other player. once we have a list of pathlengths to each cell from both 
        players, we compare these two lists to determine number of cells that ptm
        can reach first. 

        ** trying to outlast opponent
        ** weight speed powerups heavily
    '''
    locs = tron_gamestate.player_locs
    board = tron_gamestate.board
    
    #the player to move
    ptm = tron_gamestate.ptm 
    loc_ptm = locs[ptm] 
    op = get_other_player(ptm)
    loc_op = locs[op]
    pathlengths_ptm = {} #a dictionary of (cell, dist_to_that_cell)
    pathlengths_op = {}
    
    empty_locs = []
    for r in range(len(board)):
        for c in range(len(board[r])):
            cell = board[r][c]
            if not(cell in BAD_CELLS):
                newloc = (r,c)
                pathlengths_ptm[newloc] = manhattan_distance(loc_ptm, newloc) 
                                        #astar(loc_ptm, newloc, board)
                pathlengths_op[newloc] = manhattan_distance(loc_op, newloc) 
                                        #astar(loc_op, newloc, board) 
                empty_locs.append(newloc)

    score_ptm = 0
    score_op = 0

    
    for loc in empty_locs:
        dist_ptm = pathlengths_ptm.get(loc)
        dist_op = pathlengths_op.get(loc)
        cell = board[loc[0]][loc[1]]
        if (dist_op == None) and (dist_ptm == None):
            pass
        elif (dist_op == None) or (dist_op < dist_ptm):
            score_ptm += weight_cell(cell, op)
        else:
            score_op += weight_cell(cell, ptm)
    #print("score_ptm", score_ptm)
    #print("score_op", score_op)
    return score_ptm - score_op

def board_eval_func(asp, tron_gamestate):
    '''
    NO LONGER USING
        a function that takes in a Tron GameState and outputs
        a real number indicating how good that state is for the
        player who is using alpha_beta_cutoff to choose their action.

        evaluates the entire board at this moment in time
    '''
    locs = tron_gamestate.player_locs
    board = tron_gamestate.board
    
    #the player to move
    ptm = tron_gamestate.ptm 
    loc_ptm = locs[ptm] 
    ptm_score = 0

    if ptm == 0:  #the other player –– always only two?
        op = 1
    else:
        op = 0
    loc_op = locs[op]
    op_score = 0

   
    for l in location_ring(loc_ptm, 1):
        ptm_score += 30*weight_cell(tron_gamestate.board[l[0]][l[1]], op)
    for l in location_ring(loc_op, 1):
        op_score += 30*weight_cell(tron_gamestate.board[l[0]][l[1]], ptm)

    for l in location_ring(loc_ptm, 2):
        ptm_score += 10*weight_cell(tron_gamestate.board[l[0]][l[1]], op)
    for l in location_ring(loc_op, 2):
        op_score += 10*weight_cell(tron_gamestate.board[l[0]][l[1]], ptm)

    for l in location_ring(loc_ptm, 3):
        ptm_score += weight_cell(tron_gamestate.board[l[0]][l[1]], op)
    for l in location_ring(loc_op, 3):
        op_score += weight_cell(tron_gamestate.board[l[0]][l[1]], ptm)

    return ptm_score - op_score

def neighboring_tiles_eval_func(asp, tron_gamestate):
    '''
        a function that takes in a Tron GameState and outputs
        a real number indicating how good that state is for the
        player who is using alpha_beta_cutoff to choose their action.

        only looks at IMMEDIATELY PROXIMATE TILES + 1 remove
        a simplification of pathlengths_eval_func
    '''
    locs = tron_gamestate.player_locs
    board = tron_gamestate.board
    
    #the player to move
    ptm = tron_gamestate.ptm 
    ptm_loc = locs[ptm]
    op = get_other_player(ptm)
    op_loc = locs[op]
      

    ptm_score = calculate_score(asp, ptm, board, tron_gamestate, ptm_loc, True)
   # print("ptm score ", ptm_score)
    op_score = calculate_score(asp, op, board, tron_gamestate, op_loc, True)
    #print("op score ", op_score)

    return ptm_score - op_score

GOOD_POWERUP_WEIGHT = 100 
BAD_CELLS = [CellType.WALL, CellType.BARRIER, CellType.SPEED] #make this change w strategy
GOOD_POWERUPS = [CellType.ARMOR, CellType.BOMB, CellType.TRAP]
#DEATH_CELLS = [CellType.WALL, CellType.BARRIER]

def calculate_score(asp, player, board, tron_gamestate, loc, recur):
    '''
    The core of project –– figuring out weights and so on based on experimentation
    THIS is why we do not need to weight powerups in ab_cutoff itself
    should check for armor here, or elsewhere?

    "recur" boolean indicates whether another recursion should be performed
    '''

    #check if terminal state
    if asp.is_terminal_state(tron_gamestate):
        if asp.evaluate_state(tron_gamestate)[player] == 0.0:
            return(-1000)
        else:
            return(1000)

    actions = TronProblem.get_safe_actions(board, loc)
    score_sum = 0

    #print("player ", player, "'s score here is ", score_sum, ", available actions ", actions)

    if len(actions) > 0:
        for a in actions:
            #print("in for loop score_sum is ", score_sum)
            next_loc = get_next_loc(loc, a) #a (x,y) tuple
            next_cell = board[next_loc[0]][next_loc[1]] # a celltype "#", "@" etc
            next_state = asp.transition(tron_gamestate, a) #a gamestate

            if next_state.player_has_armor(player):
                if ((next_cell in [CellType.WALL, CellType.SPEED]) or next_cell.isdigit()): #isdigit should check for other player
                    score_sum += -10
                elif next_cell in GOOD_POWERUPS:
                    score_sum += GOOD_POWERUP_WEIGHT
                else: 
                    assert next_cell == CellType.SPACE or next_cell == CellType.BARRIER #delte l8r
                    score_sum += 1
            else:
                if ((next_cell in [CellType.WALL, CellType.BARRIER, CellType.SPEED]) or next_cell.isdigit()):
                    score_sum += -10
                elif next_cell in GOOD_POWERUPS:
                    score_sum += GOOD_POWERUP_WEIGHT
                else:
                    assert next_cell == CellType.SPACE #delte l8r
                    score_sum += 1
            
            #a state is less favourable if it is directly adjacent to walls
            score_sum += (8 - adjacent_walls(board, loc))

            #doesn't work rn
            #if recur: #kind of weird bc actually, it will be next player
                #score_sum += 0.5*calculate_score(asp, player, next_state.board, next_state, next_loc, False)
    
    else: #NEXT move will be terminal state for player
        #print("player has no available actions")
        score_sum = -600 #should be less than 1000
    
    return score_sum

def adjacent_walls(board, loc):
    '''takes in the board and a loc and returns the number of
    adjacent cells that are occupied by a wall'''
    safeLocs = TronProblem.get_safe_actions(board, loc)
    unsafeLocs = 8 - len(safeLocs)
    return unsafeLocs
    

def get_next_loc(loc, action):
    '''
    takes in a loc and action ('u', 'd', etc) and gets the next location
    I think this is necessary bc if you transition into the next state,
    you can't tell if it's a powerup?
    returns a tuple of location
    '''
    if action == "U":
        return (loc[0], loc[1]-1)
    if action == "D":
        return (loc[0], loc[1]+1)
    if action == "L":
        return (loc[0]-1, loc[1])
    if action == "R":
        return (loc[0]+1, loc[1])

def get_other_player(p1):
    if p1 == 0:  #the other player –– always only two?
        return 1
    else:
        return 0

def location_ring(loc, remove):
    '''
    NO LONGER USING
    '''
    return[(loc[0], loc[1]+remove), (loc[0], loc[1]-remove), (loc[0]+remove, loc[1]), (loc[0]-remove, loc[1])]

def weight_cell(cell, op):
    '''
    NO LONGER USING
    A primitive way to weight powerups
    '''
    if ((cell in BAD_CELLS) or (cell == op)): #not sure this second check works
        return -POWERUP_WEIGHT
    elif (cell in GOOD_POWERUPS):
        return POWERUP_WEIGHT
    else: #just a space
        return 1

def change_strategy(tron_state):
    '''
    Takes in a tron game and decides whether or not to change from 
    the startgame into the endgame strategy (a boolean)

    should kick in when we have boxed in our opponent
    '''
    return False    

class StudentBot:
    """ Write your student bot here"""

    def __init__(self):
        self.start = False #indicates we are in the startgame strategy
        #self.has_armor = False
        #self.tronproblem = None

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}

        To get started, you can get the current
        state by calling asp.get_start_state()
        """
        #self.tronproblem = asp
        start_state = asp.get_start_state()
        #self.has_armor = start_state.player_has_armor(start_state.ptm)

        if self.start:
            return alpha_beta_cutoff(asp, start_state, CUTOFF_PLY, start_eval_func)
        else:
            return alpha_beta_cutoff(asp, start_state, CUTOFF_PLY, neighboring_tiles_eval_func)

        if self.start: 
            if change_strategy(start_state): #checks whether to change into endgame strategy
                self.start = False

    def cleanup(self):
        """
        Input: None
        Output: None

        This function will be called in between
        games during grading. You can use it
        to reset any variables your bot uses during the game
        (for example, you could use this function to reset a
        turns_elapsed counter to zero). If you don't need it,
        feel free to leave it as "pass"
        """
        
class RandBot:
    """Moves in a random (safe) direction"""

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}
        """
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board, loc))
        if possibilities:
            return random.choice(possibilities)
        return "U"

    def cleanup(self):
        pass

class WallBot:
    """Hugs the wall"""

    def __init__(self):
        order = ["U", "D", "L", "R"]
        random.shuffle(order)
        self.order = order

    def cleanup(self):
        order = ["U", "D", "L", "R"]
        random.shuffle(order)
        self.order = order

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}
        """
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board, loc))
        if not possibilities:
            return "U"
        decision = possibilities[0]
        for move in self.order:
            if move not in possibilities:
                continue
            next_loc = TronProblem.move(loc, move)
            if len(TronProblem.get_safe_actions(board, next_loc)) < 3:
                decision = move
                break
        return decision

#def main():


#if __name__ == "__main__":
    #main()
