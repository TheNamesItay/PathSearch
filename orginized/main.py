import networkx as nx
import time as t
from heuristics import *
from helper_functions import *
from astar import limited_AStar as astar
from astar import FAILURE


# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2


def goal_check_path(state, graph):  # graph is original graph of nodes!
    left = len(state[PATH])
    return left == len(graph.nodes)


def run(heuristic, graph, start, target, cutoff, timeout):
    start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
    start_path = (start,)
    start_state = (start, start_path, start_available)
    f = (lambda x: function(x, heuristic, graph, target))
    end_state, expansions, runtime = astar(graph, start_state, f, goal_check_path, cutoff=cutoff, timeout=timeout)
    return end_state[PATH], expansions, runtime


def test_heuristics(heuristic_name_func_pairs, runs, num_of_nodes, prob_of_edge, cutoff, timeout):
    graphs = generate_graphs(runs, num_of_nodes, prob_of_edge)
    names = [name for name, h in heuristic_name_func_pairs]
    sum_runtimes = dict.fromkeys(names, 0)
    sum_expansions = dict.fromkeys(names, 0)
    sum_path_lengths = dict.fromkeys(names, 0)
    graph_i = 0
    for graph, start, target in graphs:
        print()
        print(f"GRAPH {graph_i}:")
        graph_i += 1
        for name, h in heuristic_name_func_pairs:
            path, expansions, runtime = run(h, graph, start, target, cutoff, timeout)
            sum_path_lengths[name] += len(path)
            sum_expansions[name] += expansions
            sum_runtimes[name] += runtime
            print(f"\tNAME: {name}, \t\tPATH-LENGTH: {len(path)}, \t\tEXPANSIONS: {expansions} \t\tRUNTIME: {runtime}")
    print()
    print("RESULTS:")
    for name, h in heuristic_name_func_pairs:
        avg_length = sum_path_lengths[name] / runs
        avg_expansions = sum_expansions[name] / runs
        avg_runtime = sum_runtimes[name] / runs
        print(f"\tNAME: {name}, "
              f"\t\tPATH-LENGTH: {avg_length}, \t\tEXPANSIONS: {avg_expansions} \t\tRUNTIME: {avg_runtime}")


heuristics = [
    # ["reachables", reachable_nodes_heuristic],
    # ["bcc nodes", count_nodes_bcc],
    # ["shimony pairs heuristics approx", shimony_pairs_bcc_aprox],
    ["shimony pairs heuristics", shimony_pairs_bcc]
]
test_heuristics(heuristics, 5, 60, 0.3, 30, 500)
