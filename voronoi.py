import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue
from abcutoff import *
from max_abcutoff import *
from copy import deepcopy
from dijkstra import *

@static
def helper(state, my_frontier, my_explored, op_frontier, op_explored):
	new_my_frontier = {}
    #check not empty
    if len(my_frontier) > 0 :
        for loc in my_frontier:
            actions = TronProblem.get_safe_actions(state.board, loc)
            my_explored.add(loc)
            for a in actions:
                # i think we should write a function that simulates move, bc TronProblem.move actually moves the player?
                next_loc = TronProblem.move(loc, a)
                if not(next_loc in op_explored):
                    my_frontier.add(next_loc)
        return (new_my_frontier, my_explored)
    
    #what to return if frontier empty?
    return {}
    
@static
def altVoronoi(asp, state, ptm, op, ptm_loc, op_loc):

    ptm_explored = {}
    op_explored = {}
    ptm_frontier = {ptm_loc}
    op_frontier = {op_loc}
    
    while not(len(ptm_frontier) == 0) or not(len(ptm_frontier) == 0):
    new_my_frontier = {}
    new_op_fronier = {}
    #check not empty
        for loc in ptm_frontier:
            actions = TronProblem.get_safe_actions(state.board, loc)
            my_explored.add(loc)
            for a in actions:
                # i think we should write a function that simulates move, bc TronProblem.move actually moves the player?
                next_loc = TronProblem.move(loc, a)
                if not(next_loc in op_explored):
                    my_frontier.add(next_loc)
        return (new_my_frontier, my_explored)
    }
    #what to return if frontier empty?
    return {}
    
def voronoi(asp, state, ptm, op, ptm_loc, op_loc):
	'''
	returns how much space ptm has vs how much space op has.
	'''
	ptm_explored = {}
	op_explored = {}
	ptm_frontier = {ptm_loc}
	op_frontier = {op_loc}
    
    #changed from and to or
	while not(len(ptm_frontier) == 0) or not(len(ptm_frontier) == 0):
		(ptm_frontier, ptm_explored) = helper(state, ptm_frontier, ptm_explored, op_frontier, op_explored)
		(op_frontier, op_explored) = helper(state, op_frontier, op_explored, ptm_frontier, ptm_explored)
		
		#how to iterate both through our actions and opponent's actions at the same time??
		#not sure this solution works / wouldn't lead to concurrency problems 
		#(i.e, both loops editing the same frontier or explored at the same time)

        #might be ok, since they should only be touching their own frontiers in each?
        
	return len(ptm_explored) - len(op_explored)

	
