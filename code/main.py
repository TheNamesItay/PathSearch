import networkx as nx
import time as t

from graph_builder import build_room_graph, generate_grids, build_small_grid, build_small_grid_test, build_heuristic_showcase
from heuristics import *
# from astar import limited_AStar as astar
from astar import FAILURE
from lazy_a_star import max_weighted_a_star, max_weighted_lazy_a_star, max_a_star_ret_states

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2


def get_goal_func(target):
    def goal_check_path(state):  # graph is original graph of nodes!
        return state[CURRENT_NODE] == target

    return goal_check_path


def run(heuristic, graph, start, target, cutoff, timeout):
    start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
    start_path = (start,)
    start_state = (start, start_path, start_available)
    h = (lambda x: heuristic(x, graph, target))
    strong_h = (lambda x: ex_pairs(x, graph, target))
    g = (lambda x: len(x[PATH]))
    end_state, data = max_weighted_a_star(graph,
                                          start_state,
                                          get_goal_func(target),
                                          h,
                                          g)
    expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len = data
    return end_state[PATH], expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len


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
        print()
        print(f"GRAPH {graph_i}:")
        for name, h in heuristic_name_func_pairs:
            path, expansions, runtime, hs, pl = run(h, graph, start, target, cutoff, timeout)
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
    for name, h in heuristic_name_func_pairs:
        avg_length = sum_path_lengths[name] / runs
        avg_expansions = sum_expansions[name] / runs
        avg_runtime = sum_runtimes[name] / runs
        print(f"\tNAME: {name}, "
              f"\t\tPATH-LENGTH: {avg_length}, \t\tEXPANSIONS: {avg_expansions} \t\tRUNTIME: {avg_runtime}")
    print()
    if len(heuristic_name_func_pairs) == 2:
        name1, name2 = heuristic_name_func_pairs[0][0], heuristic_name_func_pairs[1][0]
        ratio_sum = 0
        for i in range(runs):
            ratio_sum = expansions_per_run[name1][i] / expansions_per_run[name2][i]
        ratio = ratio_sum / runs
        print(f"EXPANSION RATIO: {name1} / {name2} = {ratio}")


def test_heuristics_2(cutoff, generate_func):
    graphs = generate_func()
    hs = []
    for graph, start, target in graphs:
        start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
        start_path = (start,)
        start_state = (start, start_path, start_available)
        g = (lambda x: len(x[PATH]))
        def f(x):
            a, b = ex_pairs_test(x, graph, target)
            return (a + g(x)), (b + g(x))
        h_i = max_a_star_ret_states(graph, start_state, get_goal_func(target), cutoff, f)
        print(len(h_i))
        hs += h_i
    print('len', len(hs))
    h1 = [a for a,b in hs]
    h2 = [b for a,b in hs]
    plt.scatter(h1, h2)
    plt.plot([0, max(h2)], [0, max(h2)], '--')
    plt.xlabel("regular flow ex pairs")
    plt.ylabel("bcc")
    plt.show()


def display_hs(graph_i, heuristic_name_func_pairs, hs_per_run, pl_per_run):
    fig, ax = plt.subplots()
    for name, _ in heuristic_name_func_pairs:
        print(name, hs_per_run[name][graph_i])
        plt.plot(range(len(hs_per_run[name][graph_i])), hs_per_run[name][graph_i], label=f"hs - {name}")
        # plt.plot(range(len(pl_per_run[name][graph_i])), pl_per_run[name][graph_i], label=f"pl - {name}")
    plt.title('graph ' + str(graph_i))
    plt.legend()
    plt.show()


def regular_graph_setup(runs, num_of_nodes, prob_of_edge):
    return lambda: generate_graphs(runs, num_of_nodes, prob_of_edge)


def grid_setup(runs, height, width, block_p):
    return lambda: generate_grids(runs, height, width, block_p)


heuristics = [
    # ["reachables", reachable_nodes_heuristic],
    # ["availables", available_nodes_heuristic],
    # ["shimony pairs heuristics approx", shimony_pairs_bcc_aprox],
    # ["easy nodes", easy_ex_nodes],
    # ["brute force ex pairs", ex_pairs_using_brute_force],
    ["bcc nodes", count_nodes_bcc],
    ["ex pairs using reg flow", ex_pairs_using_reg_flow],
    ["ex pairs using 3 flow", ex_pairs_using_pulp_flow],
    # ["ex pairs using LP", ex_pairs_using_3_flow],

]
x = build_small_grid()
graph, start, target = x[0]
start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
start_path = (start,)
start_state = (start, start_path, start_available)

# print_graph(graph)

# plt.show()

# print(index_to_node[3], index_to_node[13])
# print(index_to_node[4], index_to_node[13])
# print(index_to_node[9], index_to_node[13])
# #
# print(index_to_node[2], index_to_node[13])
# print(index_to_node[3], index_to_node[23])
#
print(f"reg flow value: {ex_pairs_using_reg_flow(start_state, graph, target)}")
print(f"LP value: {ex_pairs_using_pulp_flow(start_state, graph, target)}")
print(f"BCC value: {count_nodes_bcc(start_state, graph, target)}")
# print(index_to_node[19], index_to_node[23])

test_heuristics(heuristics, cutoff=-1, timeout=-1, generate_func=build_small_grid)
# test_heuristics(cutoff=100, generate_func=build_small_grid)
# test_heuristics(heuristics, cutoff=-1, timeout=-1, generate_func=regular_graph_setup(runs=10, num_of_nodes=50, prob_of_edge=0.1))
