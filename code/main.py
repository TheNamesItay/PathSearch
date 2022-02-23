import matplotlib.pyplot as plt
import networkx as nx
import time as t
from multiprocessing import Process

from state import State
from graph_builder import *
from heuristics import *
# from astar import limited_AStar as astar
from astar import FAILURE
from lazy_a_star import max_weighted_a_star, max_a_star_ret_states

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2


def get_goal_func(target):
    def goal_check_path(state):  # graph is original graph of nodes!
        return state.current == target

    return goal_check_path


def run(heuristic, graph, start, target, cutoff, timeout):
    start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
    start_path = (start,)
    start_state = (start, start_path, start_available)
    h = (lambda x: heuristic(x, graph, target))
    # strong_h = (lambda x: ex_pairs(x, graph, target, ))
    end_state, data = max_weighted_a_star(graph,
                                          start_state,
                                          get_goal_func(target),
                                          h,
                                          g)
    expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len, nodes_chosen = data
    return end_state.path if end_state != -1 else [], expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len, nodes_chosen


def run_weighted(heuristic, graph, start, target, weight, cutoff, timeout, is_incremental):
    start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
    start_path = (start,)
#     bcc_dict = {}
    start_state = State(start, start_path, start_available)
    h = (lambda x: heuristic(x, graph, target, is_incremental))
    # stron = (lambda x: ex_pairs(x, graph, target))
    end_state, data = max_weighted_a_star(graph,
                                          start_state,
                                          get_goal_func(target),
                                          h,
                                          g,
                                          is_incremental,
                                          weight=weight,
                                         cutoff=cutoff,
                                          timeout=timeout
                                         )
    expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len, nodes_chosen, generated_nodes = data
    return end_state.path if end_state != -1 else [], expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len, nodes_chosen, generated_nodes
# def process_run(
#         name,
#         heuristic,
#         graph,
#         start,
#         target,
#         cutoff,
#         timeout,
#         sum_path_lengths,
#         sum_expansions,
#         sum_runtimes,
#         hs_per_run,
#         pl_per_run,
#         expansions_per_run,
#         graph_i
# ):
#     reset_bcc_values()
#     start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
#     start_path = (start,)
#     start_state = (start, start_path, start_available)
#     h = (lambda x: heuristic(x, graph, target))
#     # strong_h = (lambda x: ex_pairs(x, graph, target))
#     end_state, data = max_weighted_a_star(graph,
#                                           start_state,
#                                           get_goal_func(target),
#                                           h,
#                                           g)
#     expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len, nodes_chosen = data
#     path, expansions, runtime, hs, pl, ns = end_state[PATH], expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len, nodes_chosen
#     sum_path_lengths[name] += len(path)
#     sum_expansions[name] += expansions
#     sum_runtimes[name] += runtime
#     hs_per_run[name][graph_i] = hs
#     pl_per_run[name][graph_i] = pl
#     expansions_per_run[name][graph_i] = expansions
#     print(f"{name} {hs_per_run[name][graph_i]}")
#     print(f"\tNAME: {name}, \t\tPATH-LENGTH: {len(path)}, \t\tEXPANSIONS: {expansions} \t\tRUNTIME: {runtime}")


def test_heuristics(heuristic_name_func_pairs, cutoff, timeout, generate_func):
    graphs = generate_func()
    runs = len(graphs)
    names = [name for name, h in heuristic_name_func_pairs]
    sum_runtimes = dict.fromkeys(names, 0)
    sum_expansions = dict.fromkeys(names, 0)
    sum_path_lengths = dict.fromkeys(names, 0)
    hs_per_run = {}
    pl_per_run = {}
    expansions_per_run = {}
    for name, _ in heuristic_name_func_pairs:
        hs_per_run[name] = [0] * runs
        pl_per_run[name] = [0] * runs
        expansions_per_run[name] = [0] * runs
    graph_i = 0
    for graph, start, target in graphs:
        print(f"GRAPH {graph_i}:")
        for name, h in heuristic_name_func_pairs:
            path, expansions, runtime, hs, pl, ns, ng = run_weighted(h, graph, start, target, 1, cutoff, timeout)
            sum_path_lengths[name] += len(path)
            sum_expansions[name] += expansions
            sum_runtimes[name] += runtime
            hs_per_run[name][graph_i] = hs
            pl_per_run[name][graph_i] = pl
            expansions_per_run[name][graph_i] = expansions
            print(f"{name} {hs_per_run[name][graph_i]}")
            print(f"\tNAME: {name}, \t\tPATH-LENGTH: {len(path)}, \t\tEXPANSIONS: {expansions} \t\tRUNTIME: {runtime}")

        display_hs(graph_i, heuristic_name_func_pairs, hs_per_run, pl_per_run)
        graph_i += 1

    print()
    print("RESULTS:")
    res = []
    for name, h in heuristic_name_func_pairs:
        avg_length = sum_path_lengths[name] / runs
        avg_expansions = sum_expansions[name] / runs
        avg_runtime = sum_runtimes[name] / runs
        print(f"\tNAME: {name}, "
              f"\t\tPATH-LENGTH: {avg_length}, \t\tEXPANSIONS: {avg_expansions} \t\tRUNTIME: {avg_runtime}")
        res += [(name, avg_length, avg_expansions, avg_runtime)]

    if len(heuristic_name_func_pairs) == 2:
        name1, name2 = heuristic_name_func_pairs[0][0], heuristic_name_func_pairs[1][0]
        ratio_sum = 0
        for i in range(runs):
            ratio_sum = expansions_per_run[name1][i] / expansions_per_run[name2][i]
        ratio = ratio_sum / runs
        print(f"EXPANSION RATIO: {name1} / {name2} = {ratio}")


# def test_heuristics_2(cutoff, generate_func):
#     graphs = generate_func()
#     hs = []
#     for graph, start, target in graphs:
#         start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
#         start_path = (start,)
#         start_state = (start, start_path, start_available)
#         g = (lambda x: len(x[PATH]))
#         def f(x):
#             a, b = ex_pairs_test(x, graph, target)
#             return (a + g(x)), (b + g(x))
#         h_i = max_a_star_ret_states(graph, start_state, get_goal_func(target), cutoff, f)
#         print(len(h_i))
#         hs += h_i
#     print('len', len(hs))
#     h1 = [a for a,b in hs]
#     h2 = [b for a,b in hs]
#     plt.scatter(h1, h2)
#     plt.plot([0, max(h2)], [0, max(h2)], '--')
#     plt.xlabel("regular flow ex pairs")
#     plt.ylabel("bcc")
#     plt.show()


def display_hs(graph_i, heuristic_name_func_pairs, hs_per_run, pl_per_run):
    fig, ax = plt.subplots()
    for name, _ in heuristic_name_func_pairs:
        print(name, hs_per_run[name][graph_i])
        plt.plot(range(len(hs_per_run[name][graph_i])), hs_per_run[name][graph_i], label=f"hs - {name}")
        # plt.plot(range(len(pl_per_run[name][graph_i])), pl_per_run[name][graph_i], label=f"pl - {name}")
    plt.title('graph ' + str(graph_i))
    plt.legend()
    plt.show()
    plt.savefig('fig.png')


def grid_setup(runs, height, width, block_p):
    return lambda: generate_grids(runs, height, width, block_p)


heuristics = [
    # ["reachables", reachable_nodes_heuristic],
    # ["availables", available_nodes_heuristic],
    # ["shimony pairs heuristics approx", shimony_pairs_bcc_aprox],
    # ["easy nodes", easy_ex_nodes],
    # ["brute force ex pairs", ex_pairs_using_brute_force],
    ["bcc nodes", count_nodes_bcc],
    # ["test bcc nodes", count_nodes_bcc_testy],
    ["ex pairs not incremental", ex_pairs_using_reg_flow],
    ["ex pairs using reg flow", ex_pairs_using_reg_flow],
    # ["ex pairs using 3 flow", ex_pairs_using_pulp_flow],
    # ["ex pairs using LP", ex_pairs_using_3_flow],

]

# s = {3, 2, 1}
# graph = reach_nested.subgraph(comp)
# print(type(s))
# s = sorted(s)
# print(s, type(s))
# t = tuple(s)
# print(t)

# test_heuristics(heuristics, cutoff=-1, timeout=-1, generate_func=build_small_grid)
# test_heuristics(cutoff=100, generate_func=build_small_grid)
# test_heuristics(heuristics, cutoff=-1, timeout=-1, generate_func=regular_graph_setup(runs=10, num_of_nodes=50, prob_of_edge=0.1))
# test_heuristics(heuristics, cutoff=-1, timeout=-1, generate_func=grid_setup(runs=10, height=20, width=20, block_p=0.5))
