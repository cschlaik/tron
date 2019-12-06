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
#BOTS V1.3
#493/600 for cutoffply = 3; playing against random bot on empty map
#513/600 for cutoffply=4; playing against random bot on empty map
# /600 for cutoffply=6; playing against random bot on empty map

#experiment w changing these
#generally seems better to have longer ab search than more recursions
AB_CUTOFF_PLY = 6
CALC_SCORE_NUM_RECURSIONS = 3

def get_safe_actions(state, player):
        """
        FROM TRONPROBLEM, BUT TAKES INTO ACCOUNT ARMOR 
        Given a game board and a location on that board,
        returns the set of actions that don't result in immediate collisions.
        Input:
            board- a list of lists of characters representing cells
            loc- location (<row>, <column>) to find safe actions from
        Output:
            returns the set of actions that don't result in immediate collisions.
            An immediate collision occurs when you run into a barrier, wall, or
            the other player
        """
        safe = set()
        if state.player_has_armor(player):

            for action in {U, D, L, R}:
                r1, c1 = TronProblem.move(state.player_locs[player], action)
                if not (
                    state.board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(state.board, (r1, c1))
                ):
                    safe.add(action)
            return safe
        else:
            for action in {U, D, L, R}:
                r1, c1 = TronProblem.move(state.player_locs[player], action)
                if not (
                    state.board[r1][c1] == CellType.BARRIER
                    or state.board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(state.board, (r1, c1))
                ):
                    safe.add(action)
            return safe

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

    ptm_score = calculate_score(asp, ptm, board, tron_gamestate, ptm_loc, CALC_SCORE_NUM_RECURSIONS)
    #print("ptm score ", ptm_score)
    op_score = calculate_score(asp, op, board, tron_gamestate, op_loc, CALC_SCORE_NUM_RECURSIONS)
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
    "recur" > 0 indicates whether another recursion should be performed
    '''

    if asp.is_terminal_state(tron_gamestate):
        #print("terminal state detected") 
        if asp.evaluate_state(tron_gamestate)[player] == 0.0:
            return(-1000)
        else: #opponent dead
            return(1000)
    if tron_gamestate.get_remaining_turns_speed(player) > 0: #avoid Speeds
        return -500

    actions = get_safe_actions(tron_gamestate, player) #** THIS WAS PROBLEM
    score_sum = 0

    if len(actions) > 0:
        for a in actions:
            next_loc = get_next_loc(loc, a) #a (x,y) tuple
            next_cell = board[next_loc[0]][next_loc[1]] # a celltype "#", "@" etc
            next_state = asp.transition(tron_gamestate, a) #a gamestate
            
            if next_state.player_has_armor(player):
                if ((next_cell in [CellType.WALL, CellType.SPEED]) or next_cell.isdigit()): #isdigit should check for other player
                    score_sum += -10
                elif next_cell in GOOD_POWERUPS:
                    score_sum += GOOD_POWERUP_WEIGHT
                    if recur>0: #kind of weird bc actually, it will be next player
                        score_sum += (1.0/recur)*calculate_score(asp, player, next_state.board, next_state, next_loc, recur-1)
                        
                else: 
                    assert next_cell == CellType.SPACE or next_cell == CellType.BARRIER #delte l8r
                    score_sum += 10
                    if recur>0:
                        score_sum += (1.0/recur)*calculate_score(asp, player, next_state.board, next_state, next_loc, recur-1)
                     
            else:
                if ((next_cell in [CellType.WALL, CellType.BARRIER, CellType.SPEED]) or next_cell.isdigit()):
                    score_sum += -10
                elif next_cell in GOOD_POWERUPS:
                    score_sum += GOOD_POWERUP_WEIGHT
                    if recur>0: 
                        score_sum += (1.0/recur)*calculate_score(asp, player, next_state.board, next_state, next_loc, recur-1)
                        
                else:
                    assert next_cell == CellType.SPACE #delete l8r
                    score_sum += 10
                    if recur>0:
                        score_sum += (1.0/recur)*calculate_score(asp, player, next_state.board, next_state, next_loc, recur-1)
                        
                        
            #keeps tunneling into bad spaces, trying to choose options with more space? :
            #print("safe acS len", TronProblem.get_safe_actions(board, loc))
            
            #a state is less favourable if it is directly adjacent to walls
            #this isn't necessarily true, bc wall-hugging can be good
            #score_sum += (8 - adjacent_walls(board, loc))
    
    else: #NEXT move will be terminal state for player
        #print("player", player, " has no available actions, recur level ", recur)
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

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}
        To get started, you can get the current state by calling asp.get_start_state()
        """
        start_state = asp.get_start_state()

        if self.start:
            return alpha_beta_cutoff(asp, start_state, AB_CUTOFF_PLY, start_eval_func)
        else:
            return alpha_beta_cutoff(asp, start_state, AB_CUTOFF_PLY, neighboring_tiles_eval_func)

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
