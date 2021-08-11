import networkx as nx
import time as t
import matplotlib.pyplot as plt

DEFAULT_WEIGHT = 1
G = nx.Graph()
PROBLEM_GRAPH = nx.Graph()

TIMEOUT = 300
CUTOFF = 3000
FAILURE = -1
EXPANSION_TIME = 1

START_NODE = -1

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2

counter = 0


def diff(li1, li2):
    return list(set(li1) - set(li2))


def intersection(lst1, lst2):
    # Use of hybrid method
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3


def expand(state):
    global counter
    global PROBLEM_GRAPH
    ret = []
    current_v = state[CURRENT_NODE]
    neighbors = G.neighbors(current_v)
    availables = state[AVAILABLE_NODES]
    path = state[PATH]
    # if counter % 100 == 0:
    #     print(counter, end=" ")
    counter += 1
    for v in intersection(neighbors, availables):
        new_path = path + (v,)
        new_availables = tuple(diff(availables, G.nodes[current_v]["constraint_nodes"]))
        new_state = (v, new_path, new_availables)
        if new_state not in list(PROBLEM_GRAPH.nodes):
            PROBLEM_GRAPH.add_node(new_state, parent=state, g=-1)
            ret.append(new_state)
        PROBLEM_GRAPH.add_edge(new_state, state)
    return ret


def checkIfWorthOpen(closed, node, heuristic):
    return node not in closed


def limited_AStar(start_state, f, goal_check):
    start_time = t.time()
    expansions = 0
    OPEN = [start_state]
    CLOSED = []
    node = FAILURE
    while True:
        if not OPEN:
            end_time = t.time() - start_time
            return node, expansions, end_time
        OPEN = sorted(OPEN, key=f)
        node = OPEN.pop(0)
        if (t.time() - start_time > TIMEOUT) or (0 < CUTOFF == expansions) or goal_check(node):
            end_time = t.time() - start_time
            return node, expansions, end_time
        if checkIfWorthOpen(CLOSED, node, f):
            CLOSED.append(node)
            nodes = expand(node)
            OPEN += nodes
            expansions += 1


# def g(state):
#     parent = PROBLEM_GRAPH.nodes[state]["parent"]
#     if parent == 0:
#         PROBLEM_GRAPH.nodes[state]["g"] = 0
#         return 0
#     g_parent = PROBLEM_GRAPH.nodes[state]["parent"]["g"]
#     if g_parent == -1:
#         g_parent = g(parent)
#     g_value = 1 + g_parent
#     PROBLEM_GRAPH.nodes[state]["g"] = g_value
#     return g_value


def g(state):
    path = state[PATH]
    g_value = len(path)
    return g_value


def available_nodes_heuristic(state):
    left_nodes_num = len(state[AVAILABLE_NODES])
    return left_nodes_num


def reachable_nodes_heuristic(state):
    node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=node)
    return len(reachables)


def largest_connected_group(state):
    node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=node)
    nested = G.subgraph(reachables)
    connected_cs = list(nx.connected_components(nested))
    largest_connected = max(connected_cs, key=len) if connected_cs else []
    return len(largest_connected)


def component_degree(comp):
    graph = G.subgraph(comp)
    return graph.number_of_edges()


def largest_connected_group_degree(state):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=current_node)
    nested = G.subgraph(reachables)
    connected_cs = list(nx.connected_components(nested))
    largest_connected = max(connected_cs, key=component_degree) if connected_cs else []
    return len(largest_connected)


def bcc_heuristic(state):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    cut_points = nested.articulation_points()


def bcc_heuristic(state):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    

def function(state, heuristic):
    res = g(state) + heuristic(state)
    return res


def goal_check_path(state):
    left = len(state[PATH])
    return left == len(G.nodes)


def weird_path_search(heuristic):
    start_available = tuple(diff(list(G.nodes), G.nodes[START_NODE]["constraint_nodes"]))
    start_path = (START_NODE,)
    start_node = START_NODE
    start_state = (start_node, start_path, start_available)
    f = (lambda x: function(x, heuristic))
    PROBLEM_GRAPH.add_node(start_state, parent=0)
    (res, expansions, time) = limited_AStar(start_state, f, goal_check_path)
    return res[PATH] if res != FAILURE else res


def parseVertex(row):
    global START_NODE
    parts = row.split()
    v_str = parts[0][2:]
    v = int(v_str)
    constraint_nodes = []
    if len(parts) > 1 and parts[1][0] == 'C':
        for node in parts[1][1:].split(','):
            constraint_nodes += [int(node)]
    G.add_node(v, constraint_nodes=constraint_nodes)
    if START_NODE == -1 or START_NODE > v:
        START_NODE = v


def parseEdge(row):
    parts = row.split()
    v1 = int(parts[1])
    v2 = int(parts[2])
    w = DEFAULT_WEIGHT
    G.add_edge(v1, v2, weight=w, color="blue")


def display_g(path):
    graph = G.copy()
    x1 = path[0]
    for i in range(1, len(path)):
        x2 = path[i]
        graph[x1][x2]['color'] = "red"
        x1 = x2
    colors = nx.get_edge_attributes(graph, 'color').values()
    pos = nx.kamada_kawai_layout(graph)
    nx.draw(graph, pos, edge_color=colors)
    plt.show()


def run():
    with open('setup.txt', 'r') as fp:
        for line in fp:
            if len(line) == 1:
                continue
            if line[1] == 'E':
                parseEdge(line)
            if line[1] == 'V':
                parseVertex(line)
        path = weird_path_search(largest_connected_group)
        display_g(path)
        return path


def get_random_graph(num_of_nodes, prob_of_edge):
    new_graph = nx.fast_gnp_random_graph(num_of_nodes, prob_of_edge)
    for node in new_graph.nodes:
        new_graph.nodes[node]["constraint_nodes"] = [node]
    return new_graph


def test_heuristics(heuristic_name_func_pairs, runs, num_of_nodes, prob_of_edge, cutoff):
    global CUTOFF
    global G
    global START_NODE
    global PROBLEM_GRAPH
    CUTOFF = cutoff
    total_runtime = [0] * len(heuristic_name_func_pairs)
    total_path_length = [0] * len(heuristic_name_func_pairs)
    for run_index in range(runs):
        test_graph = get_random_graph(num_of_nodes, prob_of_edge)
        print(f"**** RUN NUMBER {run_index}")
        h_index = 0
        for name, h in heuristic_name_func_pairs:
            start_time = t.time()
            G = test_graph.copy()
            START_NODE = 0
            PROBLEM_GRAPH = nx.Graph()
            path = weird_path_search(h)
            end_time = t.time()
            print(f"heuristic: {name}, \tpath length: {len(path)}, \truntime: {end_time-start_time}")
            total_runtime[h_index] += end_time-start_time
            total_path_length[h_index] += len(path)
            h_index += 1
        print()
    print("*** RESULTS:")
    for h_index in range(len(heuristic_name_func_pairs)):
        name = heuristic_name_func_pairs[h_index][0]
        mean_runtime = total_runtime[h_index] / runs
        mean_path_length = total_path_length[h_index] / runs
        print(f"heuristic: {name}, \tmean path length: {mean_path_length}, \tmean runtime: {mean_runtime}")


heuristics = [
                ["reachables", reachable_nodes_heuristic],
                ["availables", available_nodes_heuristic],
                ["connected_degree", largest_connected_group_degree],
                ["largest_connected", largest_connected_group]
            ]
test_heuristics(heuristics, 10, 10, 0.5, 700)
