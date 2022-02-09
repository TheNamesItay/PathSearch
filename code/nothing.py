# ex_pairs = {}
    # for x, y in possible_pairs:
    #     # print("possible pairs len: ",len(possible_pairs))
    #     success1, solution1 = flow_linear_programming(s, x, y, t, g_di)
    #     if success1:
    #         possible_pairs = delete_not_possible_pairs(possible_pairs, solution1, s, x, y, t, g_di)
    #     else:
    #         print('failed with ', x, y)
    #     success2, solution2 = flow_linear_programming(s, y, x, t, g_di)
    #     if success2:
    #         possible_pairs = delete_not_possible_pairs(possible_pairs, solution2, s, x, y, t, g_di)
    #     if not success1 and not success2:
    #         ex_pairs[x] = y

    # ex_pairs = {
    #     x: y for x, y in possible_pairs
    #     if not flow_linear_programming(s, x, y, t, g_di)
    #        and not flow_linear_programming(s, y, x, t, g_di)
    # }
    # print("ex_pairs len: ", len(ex_pairs))
    # ep = list(ex_pairs.items())
    # counter = 0
    # if len(ep) > 0:
    #     print(len(ep))
    # for x, y in ep:

from main import *


FILENAME = 'test_results.txt'

CUTOFF = 200000
TIMEOUT = -1

runs_per_params = 10
heuristics = [
    ["bcc nodes", count_nodes_bcc],
    ["ex pairs using reg flow", ex_pairs_using_reg_flow],
    ["ex pairs using 3 flow", ex_pairs_using_pulp_flow],
]
weights = [0.5 + 0.1 * i for i in range(6)]
grid_sizes = [(10 * i, 10 * i) for i in range(1,7)]
block_ps = [0.1 * i for i in range(5,7)]

graphs = []
for bp in block_ps:
    for n, m in grid_sizes:
        graphs += [(bp,) + g for g in generate_grids(runs_per_params, n, m, bp)]


def write_to_file(h_name, graph_mat, expansions, runtime, hs, ls, grid_n, astar_w, block_p):
    with open('test_results.txt', 'a') as f:
        f.write(str((grid_n, astar_w, block_p, h_name, graph_mat, expansions, runtime, hs, ls)))
        f.write('\n')


print(len(graphs))
for w in weights:
    print('w == ', w)
    for bp, mat, graph, start, target in graphs:
        print(bp, len(mat), bp)


    #     try:
    #         ex_pairs.pop(x)
    #         counter += 1
    #     except Exception as e:
    #         pass
    #     try:
    #         ex_pairs.pop(y)
    #     except Exception as e:
    #         pass
    #     try:
    #         ex_pairs.pop(get_key(x, ex_pairs))
    #     except Exception as e:
    #         pass
    #     try:
    #         ex_pairs.pop(get_key(y, ex_pairs))
    #     except Exception as e:
    #         pass
    # print("new len: ", counter)
    # print(ep)
    # print(ep[0])
    # print(index_to_node[ep[0][0]], index_to_node[ep[0][1]])