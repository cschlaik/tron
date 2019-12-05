#OLD VERSION OF BOTS (V1)
#!/usr/bin/python

import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue
from abcutoff import *
from copy import deepcopy

# Throughout this file, ASP means adversarial search problem.

#BOTS VERSION 1.1
#moved ab_cutoff into imported file abcutoff.py – this seems to be working

#BOTS VERSION 1.0
#added minimax ab_cutoff
#structured decide as call to ab_cutoff with either startgame or endgame eval_func
#skeleton start_eval_func
#end_eval_func based on distances and basic consideration of powerups
#distance function
#NEED TO DO:
#figure out when to change from start -> endgame strategy
#flesh out start_eval_func and end_eval_func (esp powerups)

#GLOBAL VARIABLES TO EXPERIMENT WITH
CUTOFF_PLY = 5 #how many look-ahead for abcutoff
POWERUP_WEIGHT = 3 #weight for powerup cells in end_eval_func

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
    score = 0
    if possibilities:
        for action in possibilities:
            if CellType.is_powerup(TronProblem.move(loc, action)):
                score += 1
        return score
    return -1

def end_eval_func_OLD(asp, tron_gamestate):
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
    possibilities_ptm = list(TronProblem.get_safe_actions(board, loc_ptm))
    pathlengths_ptm = {} #a dictionary of (cell, dist_to_that_cell) 

    #the other player –– are there always only two?
    if ptm == 0:
        op = 1
    else:
        op = 0
    loc_op = locs[op]
    possibilities_op = list(TronProblem.get_safe_actions(board, loc_op))
    pathlengths_op = {}
    
    if possibilities_ptm:
        for action in possibilities_ptm:
            newloc = TronProblem.move(loc_ptm, action) #the cell, a tuple
            pathlengths_ptm[newloc] = distance(asp, loc_ptm, newloc)

    if possibilities_op:
        for action in possibilities_op:
            newloc = TronProblem.move(loc_op, action) #the cell, a tuple
            pathlengths_op[newloc] = distance(asp, loc_op, newloc)
        
    score_ptm = 0
    score_op = 0

    #loop through both dictionaries, comparing values
    #improve this implementation; lots of redundancy
    #basic way to weight powerups
    for cell in possibilities_ptm:
        dist = possibilities_ptm.get(cell)
        if (possibilities_op.get(cell) == None) or (possibilities_op.get(cell) < dist):
            if CellType.is_powerup(cell):
                score_ptm += POWERUP_WEIGHT 
            else:
                score_ptm += 1

    for cell in possibilities_op:
        dist = possibilities_op.get(cell)
        if (possibilities_ptm.get(cell) == None) or (possibilities_ptm.get(cell) < dist):
            if CellType.is_powerup(cell):
                score_op += POWERUP_WEIGHT
            else:
                score_op += 1

    return score_ptm - score_op

def end_eval_func(asp, tron_gamestate):
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
    if ptm == 0:  #the other player –– are there always only two?
        op = 1
    else:
        op = 0
    loc_op = locs[op]
    pathlengths_ptm = {} #a dictionary of (cell, dist_to_that_cell)
    pathlengths_op = {}


    empty_cells = find_empty_cells(board) #list of tuples of empty locations
    for newloc in empty_cells:
        new_locs_ptm = copy.deepcopy(locs)
        new_locs_ptm[ptm] = newloc
        ptm_state_from_cell = TronState(board, new_locs_ptm, op, tron_gamestate.player_powerups)
        pathlengths_ptm[newloc] = distance(asp, tron_gamestate, ptm_state_from_cell)

        new_locs_op = copy.deepcopy(locs)
        new_locs_op[op] = newloc
        op_state_from_cell = TronState(board, new_locs_op, ptm, tron_gamestate.player_powerups)
        pathlengths_op[newloc] = distance(asp, tron_gamestate, op_state_from_cell)

        
    score_ptm = 0
    score_op = 0

    #basic way to weight powerups
    for cell in empty_cells:
        dist_ptm = pathlengths_ptm.get(cell)
        dist_op = pathlengths_op.get(cell)
        if (dist_op == None) and (dist_op == None):
            pass
        elif (dist_op == None) or (possibilities_op.get(cell) < dist):
            if CellType.is_powerup(cell):
                score_ptm += POWERUP_WEIGHT 
            else:
                score_ptm += 1
        else:
            if CellType.is_powerup(cell):
                score_op += POWERUP_WEIGHT
            else:
                score_op += 1

    return score_ptm - score_op
def distance(asp, state1, state2):
    '''
    calculates the Manhattan/taxicab distance pathlength between two cells
    '''
    #return Math.abs(cell1[0] - cell2[0]) + Math.abs(cell1[1] - cell2[1])
    return astar(asp, path_heuristic, state1, state2)

def astar(tron_problem, heur, start_state, goal_state, goal_loc):
    """
    Implement A* search.

    The given heuristic function will take in a state of the search problem
    and produce a real number.

    Your implementation should be able to work with any heuristic
    that is for the given search problem (but, of course, without a
    guarantee of optimality if the heuristic is not admissible).

    Input:
        problem - the problem on which the search is conducted, a TronProblem
        heur - a heuristic function that takes in a state as input and outputs a number

    Output: a list of states representing the path of the solution

    """
    curr_state = start_state
    if start_state == goal_state:
        return [start_state]
    frontier = PriorityQueue()
    frontier.put((heur(curr_state), curr_state))
    explored = {curr_state}
    node_to_parent_dict = {curr_state: None}
    cost_dict = {curr_state: 0}

    while (not frontier.empty()):
        curr_state = frontier.get()[1]
        curr_loc = curr_state.player_locs[curr_state.ptm]
        moves = TronProblem.get_safe_actions(curr_state.board, curr_loc) #the moves, a list of {U, D, L, R}
        for m in moves: 
            next_state = tron_problem.transition(curr_state, m)
            if next_state not in explored:
                explored.add(next_state)
                node_to_parent_dict.update({next_state: curr_state})

                this_cost = cost_dict.get(curr_state) + 1
                cost_dict.update({next_state: this_cost})

                next_loc = next_state.player_locs[next_state.ptm]
                if next_loc == goal_loc:
                    return make_solution_path(next_state, node_to_parent_dict) #return list of states
                else:
                    frontier.put((heur(next_state) + cost_dict.get(next_state), next_state))

def make_solution_path(node, dict):
    solution = []
    curr_node = node
    while (not curr_node == None):
        solution.append(curr_node)
        curr_node = dict.get(curr_node)
    solution.reverse()
    return solution

def path_heuristic(tron_state):
    return 1.0

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

        if self.start:
            return alpha_beta_cutoff(asp, start_state, CUTOFF_PLY, start_eval_func) #changed
        else:
            return alpha_beta_cutoff(asp, start_state, CUTOFF_PLY, end_eval_func)

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
        self.tronproblem = None #correct??

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
