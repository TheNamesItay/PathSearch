from main import *


FILENAME = 'test_results.txt'

RUNS = 20
CUTOFF = 200000

heuristics = [
    ["bcc nodes", count_nodes_bcc],
    ["ex pairs using reg flow", ex_pairs_using_reg_flow],
    ["ex pairs using 3 flow", ex_pairs_using_pulp_flow],
]
weights = [0.5 + 0.1 * i for i in range(6)]
grid_sizes = [(10 * i, 10 * i) for i in range(1,7)]
block_ps = [0.1 * i for i in range(1,7)]
extra_graphs = [build_small_grid2(), build_heuristic_showcase(10)]


def write_to_file(h_name, graph_mat, expansions, runtime, hs, ls, grid_n, astar_w, block_p, index_to_node):
    with open('test_results.txt', 'a') as f:
        f.write(str((grid_n, astar_w, block_p, h_name, graph_mat, expansions, runtime, hs, ls, index_to_node)))
        f.write('\n')


mat, graph, start, target, index_to_node, node_to_index = buil