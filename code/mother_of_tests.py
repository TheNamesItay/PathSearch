import csv

from read_csv import read_raw_csv
from main import *

SHOWCASE_CSV = 'test_showcases2.csv'
GRAPHS_FILENAME = 'saved_graphs.txt'
CSV_FILENAME = 'raw_results2.csv'
AVG_CSV = 'test_results2.csv'

CUTOFF = 200000
TIMEOUT = 1000

runs_per_params = 10
heuristics = [
    ["bcc incremental", count_nodes_bcc, True],
    ["bcc", count_nodes_bcc, False],
    # ["ex pairs using 3 flow", ex_pairs_using_pulp_flow],
    # ["ex pairs no filter", ex_pairs_with_no_prefiltering],
]
weights = [1]  # [0.7 + 0.1 * i for i in range(6)]
grid_sizes = [(15 * i, 15 * i) for i in range(1,2)]
block_ps = [0.1 * i for i in range(5, 6)]


def write_header_file(file_name, header):
    with open(file_name, 'a', encoding='UTF8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)


def write_to_file(file_name, graph_i, h_name, graph_mat, expansions, runtime, hs, ls, grid_n, astar_w, block_p):
    with open(file_name, 'a') as f:
        f.write(str((graph_i, grid_n, astar_w, block_p, h_name, graph_mat, expansions, runtime, hs, ls)))
        f.write('\n')


def write_to_csv_file(file_name, graph_i, h_name, expansions, runtime, grid_n, astar_w, block_p, generated_nodes):
    with open(file_name, 'a', encoding='UTF8') as csv_file:
        writer = csv.writer(csv_file)
        row = [str(x) for x in [graph_i, grid_n, block_p, astar_w, h_name, expansions, runtime, generated_nodes]]
        writer.writerow(row)


def save_graph_picture(folder_name, pic_name, mat, graph, start, target, itn):
    draw_grid(folder_name, pic_name, graph, mat, start, target, itn)


def save_heuristic_plot(folder_name, graph_i, hs_per_run):
    fig, ax = plt.subplots()
    for name, _, _ in heuristics:
        # print(name, hs_per_run[name][graph_i])
        ax.plot(range(len(hs_per_run[name][graph_i])), hs_per_run[name][graph_i], label=f"hs - {name}")
        # plt.plot(range(len(pl_per_run[name][graph_i])), pl_per_run[name][graph_i], label=f"pl - {name}")
    plt.title('graph ' + str(graph_i))
    plt.legend()
    # plt.show()
    save_results_to = './'

    fig.savefig(save_results_to + f'scatter_{str(graph_i)}.png')


#     my_file = f"."
#     fig.savefig(os.path.join(my_path, my_file))
#     plt.savefig)


def save_showcase(folder_name, showcase_name, graph, start, target, hs_per_run):
    save_heuristic_plot(folder_name, showcase_name, hs_per_run)
    # save_showcase_picture(folder_name, showcase_name, graph, start, target)


def test_heuristics(raw_csv_file_name, graphs_folder, scatter_folder):
    graphs = []
    for bp in block_ps:
        for n, m in grid_sizes:
            graphs += [(bp,) + g for g in generate_grids(runs_per_params, n, m, bp)]
    runs = len(graphs)
    names = [name for name, h, _ in heuristics]
    sum_runtimes = dict.fromkeys(names, 0)
    sum_expansions = dict.fromkeys(names, 0)
    sum_path_lengths = dict.fromkeys(names, 0)
    hs_per_run = {}
    ls_per_run = {}
    expansions_per_run = {}
    for name, _, _ in heuristics:
        hs_per_run[name] = [0] * runs
        ls_per_run[name] = [0] * runs
        expansions_per_run[name] = [0] * runs
    graph_i = 0

    for w in weights:
        print('w == ', w)
        for bp, mat, graph, start, target, itn in graphs:
            print(f"GRAPH {graph_i}:")
            for name, h, is_incremental in heuristics:
                path, expansions, runtime, hs, ls, ns, ng = run_weighted(h, graph, start, target, w, CUTOFF, TIMEOUT,
                                                                         is_incremental)
                sum_path_lengths[name] += len(path)
                sum_expansions[name] += expansions
                sum_runtimes[name] += runtime
                hs_per_run[name][graph_i] = hs
                ls_per_run[name][graph_i] = ls
                expansions_per_run[name][graph_i] = expansions
                # print(f"{name} {hs_per_run[name][graph_i]}")
                # print(
                #     f"\tNAME: {name}, \t\tPATH-LENGTH: {len(path)}, \t\tEXPANSIONS: {expansions} \t\tRUNTIME: {runtime}")
                write_to_file(GRAPHS_FILENAME, graph_i, name, mat, expansions, runtime, hs, ls, n, w, bp)
                write_to_csv_file(raw_csv_file_name, graph_i, name, expansions, runtime, n, w, bp, ng)
            save_heuristic_plot(scatter_folder, graph_i, hs_per_run)
            save_graph_picture(graphs_folder, graph_i, mat, graph, start, target, itn)
            # save_heuristic_scatters(scatter_folder, graph_i)
            graph_i += 1


def test_showcases(raw_csv_file_name, graphs_folder, scatter_folder):
    sizes = [2000 * i for i in range(1, 2)]
    graphs = [build_small_grid()] + [build_heuristic_showcase(x) for x in sizes]
    runs = len(graphs)
    names = [name for name, h, _ in heuristics]
    sum_runtimes = dict.fromkeys(names, 0)
    sum_expansions = dict.fromkeys(names, 0)
    sum_path_lengths = dict.fromkeys(names, 0)
    hs_per_run = {}
    ls_per_run = {}
    expansions_per_run = {}
    for name, _, _ in heuristics:
        hs_per_run[name] = dict()
        ls_per_run[name] = dict()
        expansions_per_run[name] = dict()
    for w in weights:
        print('w == ', w)
        for showcase_name, graph, start, target in graphs:
            print(f"GRAPH {showcase_name}:")
            for name, h, incremental in heuristics:
                path, expansions, runtime, hs, ls, ns, ng = run_weighted(h, graph, start, target, w, CUTOFF, TIMEOUT,
                                                                         incremental)
                sum_path_lengths[name] += len(path)
                sum_expansions[name] += expansions
                sum_runtimes[name] += runtime
                hs_per_run[name][showcase_name] = hs
                ls_per_run[name][showcase_name] = ls
                expansions_per_run[name][showcase_name] = expansions
                # print(f"{name} {hs_per_run[name][showcase_name]}")
                # print(
                #     f"\tNAME: {name}, \t\tPATH-LENGTH: {len(path)}, \t\tEXPANSIONS: {expansions} \t\tRUNTIME: {runtime}")
                write_to_file(GRAPHS_FILENAME, showcase_name, name, (graph.nodes, graph.edges), expansions, runtime, hs,
                              ls, -1, w, -1)
                write_to_csv_file(raw_csv_file_name, showcase_name, name, expansions, runtime, 0, w, -1, ng)
            save_showcase(graphs_folder, showcase_name, graph, start, target, hs_per_run)


def mother_of_tests(raw_csv_file_name, avg_csv, graphs_folder, scatter_folder, grids=False, showcases=False):
    header = ['Graph', 'Grid Size', 'Blocks', 'A* weight', 'Heuristic', 'Expansions', 'Runtime', 'Generated Nodes']
    avg_header = ['Grid Size', 'Blocks', 'A* weight', 'Heuristic', 'Expansions Avg', 'Runtime Avg',
                  'Generated Nodes Avg']
    write_header_file(raw_csv_file_name, header)
    if showcases:
        test_showcases(raw_csv_file_name, graphs_folder, scatter_folder)
    if grids:
        test_heuristics(raw_csv_file_name, graphs_folder, scatter_folder)
    if grids or showcases:
        write_header_file(avg_csv, avg_header)
        read_raw_csv(raw_csv_file_name, avg_csv)


mother_of_tests(CSV_FILENAME, AVG_CSV, 'graphs', 'scatters', grids=False, showcases=True)
