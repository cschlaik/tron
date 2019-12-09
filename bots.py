#!/usr/bin/python

import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue
from abcutoff import *
from copy import deepcopy
from dijkstra import *
#from voronoi import *

# Throughout this file, ASP means adversarial search problem.
#BOTS V1.8


#experiment w changing these
AB_CUTOFF_PLY = 5
CALC_SCORE_NUM_RECURSIONS = 3
WALL_HUG = False
WALL_HUG_NEIGHBORING_TILES = True
VORONOI = True

def voronoi(asp, state, ptm, op, ptm_loc, op_loc):
    '''
    returns how much space ptm has vs how much space op has.
    '''
#    ptm_explored = set()
#    op_explored = set()
#    ptm_frontier = set([ptm_loc])
#    op_frontier = set([op_loc])

    ptm_explored = []
    op_explored = []
    ptm_frontier = []
    ptm_frontier.append(ptm_loc)
    op_frontier = []
    op_frontier.append(op_loc)
    ptm_distances = {}
    ptm_distances[ptm_loc] = 0
#    print("ptm loc ", ptm_loc)
#    print("op loc ", op_loc)
    #print("dict has key ", ptm_distances.has_key(ptm_loc))
    op_distances = {}
    op_distances[op_loc] = 0
    ptm_score = 0
    op_score = 0
    
    #changed from and to or

    while not(len(ptm_frontier) == 0) or not(len(op_frontier) == 0):
       # print("ptm eval")
        #is duplicate name a problem
       # print("BEFORE CALL op dist ", op_distances.keys())
        (ptm_frontier, ptm_explored, ptm_distances, ptm_score) = helper(state, ptm_frontier, ptm_explored, ptm_distances, ptm_score)
        #print("AFTER CALL op dist ", op_distances.keys())
        #print("op eval")
        (op_frontier, op_explored, op_distances, op_score) = helper(state, op_frontier, op_explored, op_distances, op_score)

        
        #how to iterate both through our actions and opponent's actions at the same time??
        #not sure this solution works / wouldn't lead to concurrency problems 
        #(i.e, both loops editing the same frontier or explored at the same time)

        #might be ok, since they should only be touching their own frontiers in each?

    #keep track of depth of bfs, use as score/path length
    #return len(ptm_explored) - len(op_explored)
#    print("ptm score " , ptm_score)
#    print("op_score ", op_score)
    return ptm_score - op_score

def helper(state, my_frontier, my_explored, distances, score):
    #print("frontier ", my_frontier)
    #print("keys ", distances.keys())
    #MOVE THIS, pass around?
    #cumulativeDists = 0
   
    while my_frontier:
       curr_loc = my_frontier.pop()
       #print("curr loc ", curr_loc)
       #when should this be incremented?
       score += distances[curr_loc]
       actions = TronProblem.get_safe_actions(state.board, curr_loc)
       my_explored.append(curr_loc)
       for a in actions:
           next_loc = TronProblem.move(curr_loc, a)
           if not(next_loc in my_explored):
               distances[next_loc] = (distances[curr_loc] + 1)
               #print("keys ", distances.keys())
               distances[next_loc] = (distances[curr_loc] + 1)
               #print("next loc dist ", distances[next_loc])
               my_frontier.append(next_loc)

    return (my_frontier, my_explored, distances, score)
       
    #new_my_frontier = set()

#    if len(my_frontier) > 0:
#        for loc in my_frontier:
#            actions = TronProblem.get_safe_actions(state.board, loc)
#            my_explored.add(loc)
#            for a in actions:
#                # i think we should write a function that simulates move, bc TronProblem.move actually moves the player?
#                next_loc = TronProblem.move(loc, a)
#                level += 1
#                if not(next_loc in op_explored):
#                    new_my_frontier.add(next_loc)
#        return (new_my_frontier, my_explored)
#


    

    

def get_safe_actions_state(state, player, loc, has_armor):
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

        changed to take in loc -- why would this change things?
        """
        safe = set()
        board = state.board
        if has_armor:
            for action in {U, D, L, R}:
                r1, c1 = TronProblem.move(state.player_locs[player], action) #loc
                #assert (r1, c1) == loc
                #assert board[r1][c1].isdigit()==TronProblem.is_cell_player(board, (r1, c1))
                if not (
                    board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(board, (r1, c1))
                ):
                    safe.add(action)
            return safe
        else:
            for action in {U, D, L, R}:
                r1, c1 = TronProblem.move(state.player_locs[player], action)
                #assert (r1, c1) == loc
                #assert board[r1][c1].isdigit()==TronProblem.is_cell_player(board, (r1, c1))
                if not (
                    board[r1][c1] == CellType.BARRIER
                    or board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(board, (r1, c1))
                ):
                    safe.add(action)
            return safe

def get_safe_actions(board, player, loc, has_armor):
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

        changed to take in loc -- why would this change things?
        """
        safe = set()

        if has_armor:
            for action in {U, D, L, R}:
                r1, c1 = loc #TronProblem.move(state.player_locs[player], action) #loc
                #assert (r1, c1) == loc
                #assert board[r1][c1].isdigit()==TronProblem.is_cell_player(board, (r1, c1))
                if not (
                    board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(board, (r1, c1))
                ):
                    safe.add(action)
            return safe
        else:
            for action in {U, D, L, R}:
                r1, c1 = loc #TronProblem.move(state.player_locs[player], action)
                #assert (r1, c1) == loc
                #assert board[r1][c1].isdigit()==TronProblem.is_cell_player(board, (r1, c1))
                if not (
                    board[r1][c1] == CellType.BARRIER
                    or board[r1][c1] == CellType.WALL
                    or TronProblem.is_cell_player(board, (r1, c1))
                ):
                    safe.add(action)
            return safe

def manhattan_distance(loc1, loc2):
    '''
    calculates the Manhattan/taxicab distance pathlength between two cells.
    using this will APPROXIMATE what could be found with astar. 
    '''
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

def determine_divider_board(board):
    '''
    determines whether the board is the divider board
    '''
    return board[8] == ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']

def wall_hug(asp, state, order):
    '''
    don't need to take other player into account
    '''
    locs = state.player_locs
    board = state.board
    ptm = state.ptm
    loc = locs[ptm]
    possibilities = list(TronProblem.get_safe_actions(board, loc))
    if not possibilities:
        return "U"
    decision = possibilities[0]
    for move in order:
        if move not in possibilities:
            continue
        next_loc = TronProblem.move(loc, move)
        next_cell = board[next_loc[0]][next_loc[1]]
        #print("next_cell", next_cell)

        next_state = asp.transition(state, move)
        
        if next_cell == CellType.SPEED:
            #print("found speed")
            decision = move
            continue
        if (next_cell == CellType.TRAP):
             #print("found trap")
             if len(TronProblem.get_safe_actions(next_state.board, next_loc)) > 0:
                decision = move
                break
             #decision = move
             #break

        if len(TronProblem.get_safe_actions(board, next_loc)) < 3:
            #assert next_cell == CellType.SPACE or next_cell == CellType.ARMOR
            if len(TronProblem.get_safe_actions(next_state.board, next_loc)) > 0:
                decision = move
                break
    #print("decision", decision)
    return decision

def wallhug_neighboring_tiles_eval_func(asp, tron_gamestate):
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

    ptm_score = wallhug_calculate_score(asp, ptm, board, tron_gamestate, ptm_loc, 1, tron_gamestate.player_has_armor(ptm))
    #print("ptm score ", ptm_score)
    op_score = wallhug_calculate_score(asp, op, board, tron_gamestate, op_loc, 1, tron_gamestate.player_has_armor(op))
    #print("op score ", op_score)

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

    ptm_score = calculate_score(asp, ptm, board, tron_gamestate, ptm_loc, 1, tron_gamestate.player_has_armor(ptm))
    #print("ptm score ", ptm_score)
    op_score = calculate_score(asp, op, board, tron_gamestate, op_loc, 1, tron_gamestate.player_has_armor(op))
    #print("op score ", op_score)

    return ptm_score - op_score

def voronoi_eval_func(asp, tron_gamestate):
    locs = tron_gamestate.player_locs
    
    #the player to move
    ptm = tron_gamestate.ptm 
    ptm_loc = locs[ptm]
    op = get_other_player(ptm)
    op_loc = locs[op]

    return voronoi(asp, tron_gamestate, ptm, op, ptm_loc, op_loc)

TRAP_WEIGHT = 300
ARMOR_WEIGHT = 60
BOMB_WEIGHT = 100 #this one is most contingent on game_state
SPACE_WEIGHT = 10
BAD_CELL_WEIGHT = -50
SPEED_WEIGHT = -100
NEXT_STATE_DEATH_WEIGHT = -600 #should be less than 1000
HUG_WEIGHT = 50

def calculate_score(asp, player, board, tron_gamestate, loc, recur, has_armor):
    '''
    The core of project –– figuring out weights and so on based on experimentation
    THIS is why we do not need to weight powerups in ab_cutoff itself
    "recur" > 0 indicates whether another recursion should be performed
    '''

    if asp.is_terminal_state(tron_gamestate):
        if asp.evaluate_state(tron_gamestate)[player] == 0.0:
            return(-1000)
        else: #opponent dead
            return(1000)
    if tron_gamestate.get_remaining_turns_speed(player) > 0: #avoid Speeds
        return SPEED_WEIGHT

    actions = get_safe_actions_state(tron_gamestate, player, loc, has_armor)
    #actions = TronProblem.get_safe_actions(board, loc)
    score_sum = 0

    if len(actions) > 0:
        for a in actions:
            here_has_armor = has_armor
            next_loc = TronProblem.move(loc, a)#get_next_loc(loc, a) #a (x,y) tuple
            next_cell = board[next_loc[0]][next_loc[1]] # a celltype "#", "@" etc
            next_state = asp.transition(tron_gamestate, a) #a gamestate
            #assert next_loc == next_state.player_locs[player]
            #should_recur = True
            
            if (next_cell == CellType.WALL) or next_cell.isdigit(): #isdigit should check for other player
                score_sum += BAD_CELL_WEIGHT
                #should_recur = False
                continue
            elif (next_cell == CellType.BARRIER):
                if here_has_armor:
                    score_sum += SPACE_WEIGHT
                    here_has_armor = False
                else:
                    score_sum += BAD_CELL_WEIGHT
                    #should_recur = False
                    continue
            elif next_cell == CellType.SPEED:
                score_sum += SPEED_WEIGHT 
            elif next_cell == CellType.BOMB:
                score_sum += BOMB_WEIGHT 
            elif next_cell == CellType.ARMOR:
                score_sum += ARMOR_WEIGHT
                here_has_armor = True
            elif next_cell == CellType.TRAP:
                score_sum += TRAP_WEIGHT
            else: #next_cell == CellType.SPACE
                score_sum += SPACE_WEIGHT
                    
                        
            if recur<CALC_SCORE_NUM_RECURSIONS:
                score_sum += (1.0/recur)*calculate_score(asp, player, next_state.board, next_state, next_loc, recur+1, here_has_armor)
    
    else: #NEXT move will be terminal state for player
        #print("player", player, " has no available actions, recur level ", recur)
        score_sum = NEXT_STATE_DEATH_WEIGHT 
    
    return score_sum

def wallhug_calculate_score(asp, player, board, tron_gamestate, loc, recur, has_armor):
    '''
    calc scores w wallhug
    "recur" > 0 indicates whether another recursion should be performed
    '''
    #print("armor", has_armor)

    #THIS ALL COULD BE MOVED INTO EVALFUNC
    if asp.is_terminal_state(tron_gamestate):
        if asp.evaluate_state(tron_gamestate)[player] == 0.0:
            assert recur==1
            return(-1000)
        else: #opponent dead
            return(1000)
    if tron_gamestate.get_remaining_turns_speed(player) > 0: #avoid Speeds
        return SPEED_WEIGHT #this seems wrong

    actions = get_safe_actions(board, player, loc, has_armor) 
    #actions = get_safe_actions_state(tron_gamestate, player, loc, has_armor) 
    #actions = TronProblem.get_safe_actions(board, loc)
    score_sum = 0

    if len(actions) > 0:
        for a in actions:
            here_has_armor = has_armor

            #print("action", a)
            print("curr loc", loc)
            print("action", a)
            next_loc = TronProblem.move(loc, a) #a (x,y) tuple
            next_cell = board[next_loc[0]][next_loc[1]] # a celltype "#", "@" etc
            next_state = asp.transition(tron_gamestate, a) #a gamestate
            print("next loc", next_loc)
            #print("state next loc", next_state.player_locs[player])
            #assert next_loc == next_state.player_locs[player] #FIX THIS PROBLEM!!!!

            next_board = copy.deepcopy(board)
            next_board[loc[0]][loc[1]] = CellType.BARRIER
            next_board[next_loc[0]][next_loc[1]] = str(player + 1)

            #should_recur = True
            # if (next_cell == CellType.WALL) or next_cell.isdigit(): #isdigit should check for other player
            #     #score_sum += BAD_CELL_WEIGHT
            #     continue
            if (next_cell == CellType.BARRIER):
                #assert here_has_armor
                if here_has_armor:
                    score_sum += SPACE_WEIGHT
                    here_has_armor = False
                else:
                    #score_sum += BAD_CELL_WEIGHT
                    #this should not happen
                    continue

            # if asp.is_terminal_state(next_state):
            #     if asp.evaluate_state(next_state)[player] == 0.0:
            #         #print("death for me")
            #        score_sum += BAD_CELL_WEIGHT
            #     #should_recur = False
            #     continue
            
            if next_cell == CellType.SPEED:
                score_sum += SPEED_WEIGHT 
            elif next_cell == CellType.BOMB:
                score_sum += BOMB_WEIGHT 
            elif next_cell == CellType.ARMOR:
                score_sum += ARMOR_WEIGHT
                here_has_armor = True
            elif next_cell == CellType.TRAP:
                score_sum += TRAP_WEIGHT
            else: #next_cell == CellType.SPACE
                score_sum += SPACE_WEIGHT

            #next_actions_len = len(get_safe_actions_state(next_state, player, next_loc, here_has_armor))
            next_actions_len = len(get_safe_actions(next_board, player, next_loc, here_has_armor)) #changed this
            #next_actions_len = len(TronProblem.get_safe_actions(next_state.board, next_loc))
            if (next_actions_len < 3) and (next_actions_len > 0):
                #assert (next_actions_len > 0)
                #print("wallhug")
                score_sum += HUG_WEIGHT
                    
            #print("score_sum", score_sum)        
            if recur<CALC_SCORE_NUM_RECURSIONS:
                score_sum += (1.0/recur)*wallhug_calculate_score(asp, player, next_board, next_state, next_loc, recur+1, here_has_armor)
                #score_sum += (1.0/recur)*wallhug_calculate_score(asp, player, next_state.board, next_state, next_state.player_locs[player], recur+1, here_has_armor)
    
    else: #NEXT move will be terminal state for player
        #print("player", player, " has no available actions, recur level ", recur)
        #TronProblem.visualize_state(tron_gamestate, False)
        score_sum = NEXT_STATE_DEATH_WEIGHT 
    
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
        return (loc[0]-1, loc[1])
    if action == "D":
        return (loc[0]+1, loc[1])
    if action == "L":
        return (loc[0], loc[1]-1)
    if action == "R":
        return (loc[0], loc[1]+1)

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
        self.divider_board = False
        self.first_turn = True

    def decide(self, asp):
        """
        Input: asp, a TronProblem
        Output: A direction in {'U','D','L','R'}
        To get started, you can get the current state by calling asp.get_start_state()
        """
        start_state = asp.get_start_state()
        if VORONOI:
            return alpha_beta_cutoff(asp, start_state, AB_CUTOFF_PLY, voronoi_eval_func)

        if self.first_turn and WALL_HUG:
            self.divider_board = determine_divider_board(start_state.board)
            if self.divider_board:
                print("DIVIDER BOARD")
            self.first_turn = False

        if self.divider_board or WALL_HUG:
            order = ["U", "D", "L", "R"]
            random.shuffle(order)
            #return wall_hug_lookahead(asp, start_state, order)
            return wall_hug(asp, start_state, order)
        elif WALL_HUG_NEIGHBORING_TILES:
            return alpha_beta_cutoff(asp, start_state, AB_CUTOFF_PLY, wallhug_neighboring_tiles_eval_func)
        else:
            return alpha_beta_cutoff(asp, start_state, AB_CUTOFF_PLY, neighboring_tiles_eval_func)
        # if self.start: 
        #     if change_strategy(start_state): #checks whether to change into endgame strategy
        #         self.start = False

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

