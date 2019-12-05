import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from queue import Queue, LifoQueue, PriorityQueue
from abcutoff import *
from copy import deepcopy
from cellnode import *

def astar(startloc, endloc, board):
	'''
	RETURN DISTANCE RATHER THAN LIST
	'''

	if startloc == endloc:
		return 0
		
	else:
		frontier = PriorityQueue()
		currNode = CellNode(board, startloc, 0, endloc)
		#print("currnode ", currNode._loc)
		frontier.put(currNode)
		explored = {currNode}

		adjacent_nodes = currNode.get_valid_adjacent_nodes()
		for n in adjacent_nodes:
			frontier.put(n)

		while not(frontier.empty()):
			#print("frontier", frontier.get())
			currNode = frontier.get()
			if currNode._loc == endloc:
				return currNode._pathdistance
			else:
				adjacent_nodes = currNode.get_valid_adjacent_nodes()
				for n in adjacent_nodes:
					if n not in explored:
						explored.add(n)
						frontier.put(n)
