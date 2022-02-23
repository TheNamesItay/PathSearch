import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from graph_builder import *
from helper_functions import *
from playing_around import shimony_pairs_bcc as shimony
from playing_around import set_itn, pairs_lst, lpf_misses, regf_misses, specific_lpf_misses, specific_regf_misses
from heuristics import *
from playing_around import is_legit_shimony_pair as is_shimony
import time


mat, g, start, t = generate_grids(1, 15, 15, 0.3)[0]

node = start
path = []
av = diff(g.nodes, path)
state = (node, tuple(path), tuple(av))

print(time.time())
reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state, g, t)
print(time.time())

comp_g = g.subgraph(max(relevant_comps, key=len))

print(len(comp_g))
print(triconnected_components(g.subgraph(comp_g)))
print(time.time())
