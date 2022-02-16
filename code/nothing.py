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


mat, g, start, t, index_to_node, node_to_index = build_small_grid2()

node = start
path = []
av = diff(g.nodes, path)
state = (node, tuple(path), tuple(av))

reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state, g, t)

comp_g = g.subgraph(max(relevant_comps, key=len))
# comp_g = sage.graphs
print()