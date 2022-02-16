from main import *
import csv

FILENAME = 'test_results.txt'
CSV_FILENAME = 'test_results.csv'

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
block_ps = [0.1 * i for i in range(4,7)]

graphs = [(-1,) + build_small_grid2()]
for bp in block_ps:
    for n, m in grid_sizes:
        graphs += [(bp,) + g for g in generate_grids(runs_per_params, n, m, bp)]

header = ['Grid Size', 'Blocks', 'A* weight', 'Heuristic', 'Expansions Avg', 'Runtime Avg']
with open(CSV_FILENAME, 'a', encoding='UTF8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)

def write_to_file(h_name, graph_mat, expansions, runtime, hs, ls, grid_n, astar_w, block_p):
    with open('test_results.txt', 'a') as f:
        f.write(str((grid_n, astar_w, block_p, h_name, graph_mat, expansions, runtime, hs, ls)))
        f.write('\n')

def write_to_csv_file(h_name, expansions, runtime, grid_n, astar_w, block_p):
    with open(CSV_FILENAME, 'a', encoding='UTF8') as csv_file:
        writer = csv.writer(csv_file)
        row = [str(x) for x in [grid_n, block_p, astar_w, h_name, expansions, runtime]]
        writer.writerow(row)



print(len(graphs))
for w in weights:
    print('w == ', w)
    for bp, mat, graph, start, target in graphs:
        for name, h in heuristics:
            path, expansions, runtime, hs, ls, ns = run_weighted(h, graph, start, target, w, CUTOFF, TIMEOUT)
            n = len(mat)
            write_to_file(name, mat, expansions, runtime, hs, ls, n, w, bp)
            write_to_csv_file(name, expansions, runtime, n, w, bp)
