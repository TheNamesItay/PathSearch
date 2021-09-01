import time as t
from helper_functions import *

#   return values:
FAILURE = -1

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2

expansion_counter = 0


def expand_with_constraints(state, expanded, G):
    global expansion_counter
    ret = []
    current_v = state[CURRENT_NODE]
    neighbors = G.neighbors(current_v)
    availables = state[AVAILABLE_NODES]
    path = state[PATH]
    expansion_counter += 1
    for v in intersection(neighbors, availables):
        new_path = path + (v,)
        new_availables = tuple(diff(availables, G.nodes[current_v]["constraint_nodes"]))
        new_state = (v, new_path, new_availables)
        if new_state not in expanded:
            ret.append(new_state)
    return ret


def expand_snake(state, expanded, G):
    global expansion_counter
    ret = []
    current_v = state[CURRENT_NODE]
    neighbors = G.neighbors(current_v)
    availables = state[AVAILABLE_NODES]
    path = state[PATH]
    expansion_counter += 1
    new_availables = tuple(diff(availables, [current_v] + neighbors))
    for v in intersection(neighbors, availables):
        new_path = path + (v,)
        new_state = (v, new_path, new_availables + (v,))
        if new_state not in expanded:
            ret.append(new_state)
    return ret


def checkIfWorthOpen(closed, node, heuristic):
    return node not in closed


def limited_AStar(G, start_state, f, goal_check, expand=expand_with_constraints, cutoff=-1, timeout=-1):
    start_time = t.time()
    expansion = 0
    OPEN = [start_state]
    CLOSED = []
    expanded = []
    nodes_extracted_heuristic_values = []
    best_state = start_state
    while True:
        if expansion % 100 == 0:
            print(expansion, end=' ')
        if not OPEN:
            end_time = t.time() - start_time
            return best_state, expansion, end_time, nodes_extracted_heuristic_values
        OPEN = sorted(OPEN, key=f)
        node = OPEN.pop(0)
        if len(node[PATH]) > len(best_state[PATH]):
            best_state = node
        if (t.time() - start_time > timeout > 0) or (0 < cutoff == expansion) or goal_check(node, G):
            end_time = t.time() - start_time
            return best_state, expansion, end_time, nodes_extracted_heuristic_values
        if checkIfWorthOpen(CLOSED, node, f):
            nodes_extracted_heuristic_values += [f(node)]
            CLOSED.append(node)
            nodes = expand(node, expanded, G)
            expanded += nodes
            OPEN += nodes
            expansion += 1
