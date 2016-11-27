#!/usr/bin/env python3

import itertools

def eq(a, b, c, d, e):
    return a + b * (c ** 2) + (d ** 3) - e

values = (2, 3, 5, 7, 9)
for permu in itertools.permutations(values):
    vs = [x for x in permu]
    if eq(*vs) == 399:
        print(permu)

