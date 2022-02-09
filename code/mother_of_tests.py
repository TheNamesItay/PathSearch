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
        for name, h in heuristics:
            path, expansions, runtime, hs, ls, ns = run_weighted(h, graph, start, target, w, CUTOFF, TIMEOUT)
            write_to_file(name, mat, expansions, runtime, hs, ls, len(mat), w, bp)
