import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from graph_builder import *
from helper_functions import *
from playing_around import shimony_pairs_bcc as shimony
from playing_around import set_itn, pairs_lst, lpf_misses, regf_misses, specific_lpf_misses, specific_regf_misses
from heuristics import *
from playing_around import is_legit_shimony_pair as is_shimony


# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)


def draw_grid(mat, state, t, comps, index_to_node):
    current_node = index_to_node[state[0]]
    path = [index_to_node[x] for x in state[1]]
    height = len(mat)
    width = len(mat[0])
    data = [[(0, 0, 0) if mat[j][i] else (255,255,255) for j in range(len(mat[0]))] for i in range(len(mat))]
    if comps:
        for i in range(len(comps)):
            color = comp_colors[i]
            comp = comps[i]
            for c in comp:
                node = index_to_node[c]
                data[node[1]][node[0]] = color
        for v in path:
            data[v[1]][v[0]] = (50, 50, 150)
    data[current_node[1]][current_node[0]] = (255, 0, 255)
    data[t[1]][t[0]] = (0, 255, 0)

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


# mat = [
#     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# ]
#
# mat = add_rectangle(5,3,4,3,mat)
# mat = add_rectangle(10,0,5,8,mat)
# mat = add_rectangle(10,5,9,1,mat)

while True:
    try:
        block_p, width, height = 0.5, 4, 4

        while True:
            try:
                mat = [[(0 if random.uniform(0, 1) > block_p or j == 0 or j == height-1 else 1) for i in range(width)] for j in range(height)]
                # mat = [[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 1, 0, 1, 1], [1, 1, 0, 1, 0], [0, 0, 0, 0, 0]]
                mat, g, start, t, index_to_node, node_to_index = generate_grid_fortesting(mat)
                break
            except Exception as e:
                print(e)
                continue
        print(mat)
        set_itn(index_to_node)

        # print(node_to_index)
        # print(start, t)

        start_available = tuple(diff(list(g.nodes), g.nodes[start]["constraint_nodes"]))
        start_path = (start,)
        start_state = (start, start_path, start_available)

        # start_state = (s, (s,), tuple(g.nodes))
        reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(start_state, g, t)


        # print(' -- ', relevant_comps)
        best_comp = max(relevant_comps, key=len)

        print([index_to_node[x] for x in best_comp])

        node = start

        # print('getting path')
        print('huh')
        path = nx.shortest_path(g, source=start, target=node)
        # print('done path')

        av = diff(g.nodes, path)

        state = (node, tuple(path), tuple(av))
        print('state ', state)

        reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                            g, t)
        draw_grid(mat, state, index_to_node[t], relevant_comps, index_to_node)

        # draw_grid(mat, start_state, index_to_node[t], relevant_comps, index_to_node)

        brute_res, pairs = shimony(state, g, t)

        print('\n\n')
        print("pairs: ", len(pairs_lst), "\t", pairs_lst)
        print("3 flow misses: ", len(lpf_misses), "\t", lpf_misses)
        print("regular flow misses: ", len(regf_misses), "\t", regf_misses)
        print('\n\n')
        print("specific 3 flow misses: ", "\t", specific_lpf_misses)
        print("specific regular flow misses: ", specific_regf_misses)

        with open('test_results.txt', 'a') as f:
            f.write(str((mat, pairs_lst, lpf_misses, regf_misses)))
            f.write('\n')

        # flow_res = ex_pairs_using_flow(state, g, t)
        # flow_res, flow_pairs = ex_pairs_using_flow(s, g, t)
        # flow_res = ex_pairs_using_flow(state, g, t)
        # print('brute--', brute_res)
        # print('brute pairs - ', [(index_to_node[p[0]], index_to_node[p[1]]) for p in pairs])
        # print('flow --', flow_res)
        # print('brute pairs - ', [(index_to_node[p[0]], index_to_node[p[1]]) for p in flow_pairs])

        # ps1, ps2, res = is_shimony(g,
        #                  node_to_index[(2,1)],
        #                  node_to_index[(4,4)],
        #                  node_to_index[(0,2)],
        #                  node_to_index[(1,2)]
        #                  )
        #
        # print(res)
        # print('1:')
        # for p in [[[index_to_node[n] for n in pp] for pp in p] for p in ps1]:
        #     for ps in p:
        #         print(ps, " ----- ", end='')
        #     print()
        # print('2:')
        # for p in [[[index_to_node[n] for n in pp] for pp in p] for p in ps2]:
        #     for ps in p:
        #         print(ps, " ----- ", end='')
        #     print()

        continue
    except Exception as e:
        continue


p = [((0, 2), (1, 2)), ((0, 2), (2, 2)), ((0, 2), (2, 3)), ((0, 2), (3, 0)), ((0, 2), (3, 1)), ((0, 2), (3, 2)), ((0, 2), (4, 0)), ((0, 2), (4, 1)), ((0, 2), (4, 2)), ((0, 2), (4, 3)), ((0, 3), (1, 2)), ((0, 3), (2, 2)), ((0, 3), (2, 3)), ((0, 3), (3, 0)), ((0, 3), (3, 1)), ((0, 3), (3, 2)), ((0, 3), (4, 0)), ((0, 3), (4, 1)), ((0, 3), (4, 2)), ((0, 3), (4, 3)), ((0, 4), (1, 2)), ((0, 4), (2, 2)), ((0, 4), (2, 3)), ((0, 4), (3, 0)), ((0, 4), (3, 1)), ((0, 4), (3, 2)), ((0, 4), (4, 0)), ((0, 4), (4, 1)), ((0, 4), (4, 2)), ((0, 4), (4, 3)), ((1, 2), (2, 2)), ((1, 2), (2, 3)), ((1, 2), (3, 0)), ((1, 2), (3, 1)), ((1, 2), (3, 2)), ((1, 2), (4, 0)), ((1, 2), (4, 1)), ((1, 2), (4, 2)), ((1, 2), (4, 3)), ((1, 4), (2, 2)), ((1, 4), (2, 3)), ((1, 4), (3, 0)), ((1, 4), (3, 1)), ((1, 4), (3, 2)), ((1, 4), (4, 0)), ((1, 4), (4, 1)), ((1, 4), (4, 2)), ((1, 4), (4, 3)), ((2, 2), (3, 0)), ((2, 2), (3, 1)), ((2, 3), (3, 0)), ((2, 3), (3, 1)), ((2, 3), (3, 2)), ((2, 3), (4, 0)), ((2, 3), (4, 1)), ((2, 3), (4, 2)), ((2, 3), (4, 3)), ((2, 4), (3, 0)), ((2, 4), (3, 1)), ((2, 4), (3, 2)), ((2, 4), (4, 0)), ((2, 4), (4, 1)), ((2, 4), (4, 2)), ((2, 4), (4, 3)), ((3, 0), (3, 1)), ((3, 0), (3, 4)), ((3, 0), (4, 3)), ((3, 1), (3, 4)), ((3, 4), (4, 0)), ((3, 4), (4, 1)), ((3, 4), (4, 2)), ((3, 4), (4, 3))]

s = (5, (0, 5), (2, 3, 4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24))
