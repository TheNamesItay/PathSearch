from main import *

import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np


# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)


def draw_grid(mat, state, t, comps):
    current_node = state[0]
    path = state[1]
    height = len(mat)
    width = len(mat[0])
    data = [[(255, 255 * (1 - x), 255 * (1 - x)) for x in m] for m in mat]
    for comp in comps:
        for c in comp:
            data[c[0]][c[1]] = (50,50,50)
    for v in path:
        data[v[0]][v[1]] = (50, 50, 150)
    data[current_node[0]][current_node[1]] = (255, 0, 255)
    data[t[0]][t[1]] = (0, 255, 0)

    fig, ax = plt.subplots()
    ax.imshow(data, )

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
    ax.set_xticks(np.arange(-.5, width, 1))
    ax.set_yticks(np.arange(-.5, height, 1))

    plt.show()


def add_rectangle(x, y, h, w, mat):
    mat2 = mat.copy()
    for i in range(h):
        for j in range(w):
            mat2[y+j][x+i] = 1
    return mat2


mat = [
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

mat = add_rectangle(5,3,4,3,mat)
mat = add_rectangle(10,0,5,8,mat)
mat = add_rectangle(10,5,9,1,mat)

g = just_grid(mat)
s = (0, 0)
t = (10, 10)

start_state = (s, (), tuple(g.nodes))
reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(start_state,
                                                                                                    g, t)
best_comp = max(relevant_comps, key=len)
node = (6,2)
path = next(nx.all_simple_paths(g, source=s, target=node))

av = diff(g.nodes, path)

state = (node, tuple(path), tuple(av))

reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                    g, t)
draw_grid(mat, state, t, relevant_comps)

flow_res = ex_pairs_using_flow(state, g, t)
