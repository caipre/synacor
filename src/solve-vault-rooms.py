#!/usr/bin/env python3

import operator
from copy import copy

grid = {
    (3, 0): operator.mul,
    (3, 1): 8,
    (3, 2): operator.sub,
    (3, 3): 1,

    (2, 0): 4,
    (2, 1): operator.mul,
    (2, 2): 11,
    (2, 3): operator.mul,

    (1, 0): operator.add,
    (1, 1): 4,
    (1, 2): operator.sub,
    (1, 3): 18,

    (0, 0): 22,
    (0, 1): operator.sub,
    (0, 2): 9,
    (0, 3): operator.mul,
}

def adjacent_to(room):
    i, j = room
    if i < 3: yield (i + 1, j) # north
    if j < 3: yield (i, j + 1) # east
    if i > 0: yield (i - 1, j) # south
    if j > 0: yield (i, j - 1) # west

def search(room, orb, path):
    for oproom in adjacent_to(room):
        op = grid[oproom]
        for valroom in adjacent_to(oproom):
            if len(path) > 12: continue
            path_ = copy(path) + [oproom, valroom]
            if valroom == (0, 0): continue
            x = op(orb, grid[valroom])
            if x <= 0: continue
            if valroom == (3, 3):
                if x != 30: continue
                print(path_)
                return True
            if search(valroom, x, path_):
                return True
    return False

start = (0, 0)
search(start, grid[start], [start])
