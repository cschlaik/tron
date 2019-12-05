import numpy as np
from tronproblem import *
from trontypes import CellType, PowerupType
import random, math
from dataclasses import dataclass, field
from typing import Any

def heur(loc1, loc2):
    '''
    calculates the Manhattan/taxicab distance pathlength between two cells
    '''
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

@dataclass(order=True)
class CellNode():
	_priority: int
	_board: list=field(compare=False)
	_loc: tuple=field(compare=False)
	_pathdistance: int=field(compare=False)
	_endloc: tuple=field(compare=False)

	def __init__(self, board, loc, pathdistance, endloc):
		self._priority = heur(loc, endloc) + pathdistance
		self._board = board
		self._loc = loc
		self._pathdistance = pathdistance
		self._endloc = endloc

	def __hash__(self):
		return hash((self._priority, self._loc, self._pathdistance))

	def get_valid_adjacent_nodes(self):
		up = (self._loc[0], self._loc[1] -1)
		down = (self._loc[0], self._loc[1]+1)
		left = (self._loc[0]-1, self._loc[1])
		right = (self._loc[0]+1, self._loc[1])
		list_locs = {up, down, left, right}
		list_nodes = []
		for l in list_locs:
			cell = self._board[l[0]][l[1]]
			if not((cell == CellType.WALL) or (cell == CellType.BARRIER)):
				new_node = CellNode(self._board, l, self._pathdistance+1, self._endloc)
				list_nodes.append(new_node)
		return list_nodes