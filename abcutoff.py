import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue

def alpha_beta_cutoff(asp, tron_state, cutoff_ply, eval_func):
    """
    This function should:
    - search through the asp using alpha-beta pruning
    - cut off the search after cutoff_ply moves have been made.

    Inputs:
        asp - an AdversarialSearchProblem
        cutoff_ply- an Integer that determines when to cutoff the search
            and use eval_func.
            For example, when cutoff_ply = 1, use eval_func to evaluate
            states that result from your first move. When cutoff_ply = 2, use
            eval_func to evaluate states that result from your opponent's
            first move. When cutoff_ply = 3 use eval_func to evaluate the
            states that result from your second move.
            You may assume that cutoff_ply > 0.
        eval_func - a function that takes in a GameState and outputs
            a real number indicating how good that state is for the
            player who is using alpha_beta_cutoff to choose their action.
            The eval_func we provide does not handle terminal states, so evaluate terminal states the
            same way you evaluated them in the previous algorithms.

    Output: an action(an element of asp.get_available_actions(asp.get_start_state()))
    """

    best_move = max_move_ab_cutoff(asp, tron_state, tron_state.player_to_move(), None,
    float("-inf"), float("inf"), cutoff_ply, eval_func)
    if not(best_move == None):
        return best_move[0]
    else:
        print("NO MORE MOVES")
        return 'U' #arbitrarily

def min_move_ab_cutoff(asp, curr_state, player, move_to_here, alpha, beta, cutoff_ply, eval_func):

    if asp.is_terminal_state(curr_state):
        return (move_to_here, asp.evaluate_state(curr_state)[player]) 
    elif cutoff_ply == 0:
        #WEIGHT BY POWERUP HERE?
        return (move_to_here, eval_func(asp, curr_state)) #assuming this is being updated continuously?
    else:
        best_action = None
        loc = curr_state.player_locs[player]
        actions = TronProblem.get_safe_actions(curr_state.board, loc)
        
        for action in actions:
            next_state = asp.transition(curr_state, action) #DOES THIS AUTOMATICALLY TAKE POWERUPS INTO ACCOUNT?
            result = max_move_ab_cutoff(asp, next_state, player, action, alpha, beta, cutoff_ply-1, eval_func) 
            if not(result == None):
                if best_action == None:
                    best_action = (action, result[1])
                elif (result[1] < best_action[1]): 
                    best_action = (action, result[1])

                #PRUNING
                if (best_action[1] <= alpha):
                    return best_action
                if (best_action[1] < beta):
                    beta = best_action[1]

        return best_action

def max_move_ab_cutoff(asp, curr_state, player, move_to_here, alpha, beta, cutoff_ply, eval_func):
    if asp.is_terminal_state(curr_state):
        return (move_to_here, asp.evaluate_state(curr_state)[player])
    elif cutoff_ply == 0:
        return (move_to_here, eval_func(asp, curr_state))
    else:
        best_action = None
        loc = curr_state.player_locs[player]
        actions = TronProblem.get_safe_actions(curr_state.board, loc)
        if len(actions) == 0:
            print("NO MORE SAFE ACTIONS")

        for action in actions: #looking at the next level
            next_state = asp.transition(curr_state, action)
            result = min_move_ab_cutoff(asp, next_state, player, action, alpha, beta, cutoff_ply-1, eval_func)
            if not(result == None):
                if best_action == None:
                    best_action = (action, result[1])
                elif (result[1] > best_action[1]): #the 1 index of tuple is the val
                    best_action = (action, result[1])

                #PRUNING
                if (best_action[1] >= beta):
                    return best_action
                if (best_action[1] > alpha):
                    alpha = best_action[1]
        return best_action
