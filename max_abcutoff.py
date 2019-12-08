import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue

def get_safe_actions(state):
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
        if state.player_has_armor(state.ptm):

            for action in {U, D, L, R}:
                r1, c1 = TronProblem.move(state.player_locs[state.ptm], action)
                if not (
                    state.board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(state.board, (r1, c1))
                ):
                    safe.add(action)
            return safe
        else:
            for action in {U, D, L, R}:
                r1, c1 = TronProblem.move(state.player_locs[state.ptm], action)
                if not (
                    state.board[r1][c1] == CellType.BARRIER
                    or state.board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(state.board, (r1, c1))
                ):
                    safe.add(action)
            return safe

def max_alpha_beta_cutoff(asp, tron_state, cutoff_ply, eval_func):
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

    best_move = max_move_ab_cutoff(asp, tron_state, None,
    float("-inf"), float("inf"), cutoff_ply, eval_func)
    
    #print("********BEST MOVE", best_move, "\n")
    assert not(best_move == None)
    if not(best_move == None):
        return best_move[0]
    else:
        #print("NO MORE MOVES for player", tron_state.player_to_move())
        return 'U' #arbitrarily

def max_move_ab_cutoff(asp, curr_state, move_to_here, alpha, beta, cutoff_ply, eval_func):
    assert curr_state.ptm == 0
    #print("max level", cutoff_ply, " move to here", move_to_here) 
    #print(TronProblem.visualize_state(curr_state, False))

    if asp.is_terminal_state(curr_state):
        #print(" terminal state\n")
        return (move_to_here, cutoff_ply*eval_func(asp, curr_state))
    elif cutoff_ply == 0:
        #print(" reached cutoff\n")
        return (move_to_here, eval_func(asp, curr_state))
    else:
        best_action = None
        loc = curr_state.player_locs[curr_state.ptm]
        actions = get_safe_actions(curr_state)
        #print (" actions are ", actions)

        if len(actions) == 0:
            #print("max level", cutoff_ply,  "NO MORE SAFE ACTIONS for player ", curr_state.ptm)
            best_action = (move_to_here, (cutoff_ply-1)*eval_func(asp, curr_state))
            #print("returning ", best_action)    
            return best_action

        for action in actions: #looking at the next level
            next_state = asp.transition(curr_state, action)
            if curr_state.get_remaining_turns_speed(curr_state.ptm) > 0: #correct!?
                #print("on speed")
                result = max_move_ab_cutoff(asp, next_state, action, alpha, beta, cutoff_ply-1, eval_func)
            else:
                result = min_move_ab_cutoff(asp, next_state, action, alpha, beta, cutoff_ply-1, eval_func)
            #print("max, result is", result)
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
