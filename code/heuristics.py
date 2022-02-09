import networkx as nx

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
from numpy import sort, math
from scipy.optimize import linprog
from pulp import *
from helper_functions import *

CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2
NUM_OF_PAIRS = 5
N = 0
index_to_node = {}


def update_index_to_node(itn):
    global index_to_node
    index_to_node = itn


def g(state):
    path = state[PATH]
    g_value = len(path) - 1
    return g_value


def function(state, heuristic, G, target):
    return heuristic(state, G, target)


def count_nodes_bcc(state, G, target):
    _, _, relevant_comps, _, _, _ = bcc_thingy(state, G, target)
    if relevant_comps == -1:
        return -1  # if theres no path
    ret = 1
    for comp in relevant_comps:
        ret += len(comp) - 1
    return ret


def is_legit_shimony_pair(s, x, y, t, g):
    segments = [[s, x], [x, y], [y, t]]
    paths = []
    for seg in segments:
        paths += [find_disjoint_paths(g, seg)]
    paths2 = [find_disjoint_paths(g, [s, y]), [p[::-1] for p in paths[1]],
              find_disjoint_paths(g, [x, t])]
    # print(paths)
    # print(paths2)
    return not can_combine_paths(0, paths, [s]) and not can_combine_paths(0, paths2, [s])


# def disjoint_shimony_pairs(graph, in_node, out_node):
#     global index_to_node
#     counter = 0  # first pair is in and out nodes
#     done = []
#     pairs = []
#     for x1 in graph.nodes:
#         if x1 == in_node or x1 == out_node or x1 in done:
#             continue
#         for x2 in graph.nodes:
#             if x2 == in_node or x2 == out_node or x1 in done or x2 in done or x1 == x2:
#                 continue
#             if is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
#                 # di_graph = get_vertex_disjoint_directed(graph)
#                 # print('3 flow found: ', not (
#                 #             flow_linear_programming(in_node, x1, x2, out_node, di_graph) or flow_linear_programming(
#                 #         in_node, x2, x1, out_node, di_graph)))
#                 # print('regular flow found: ', not (
#                 #             has_flow(in_node, x1, x2, out_node, di_graph) or has_flow(in_node, x2, x1, out_node,
#                 #                                                                       di_graph)))
#                 counter += 1
#                 done += [x1, x2]
#                 # print(index_to_node[x1], index_to_node[x2])
#                 pairs += [(x1, x2)]
#     print(pairs)
#     return counter


# def shimony_pairs_bcc(state, G, target):
#     reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
#                                                                                                         G, target)
#     if relevant_comps == -1:
#         return 0
#     cut_node_dict = {}
#     for node in reachables:
#         comps = bcc_dict[node]
#         # if node in more than 1 component, its a cut node
#         if len(comps) > 1:
#             for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
#                 cut_node_dict[(c1, c2)] = node
#                 cut_node_dict[(c2, c1)] = node
#
#     n = len(relevant_comps)
#     in_pairs = 0
#     ex_pairs = []
#     sum = 1
#     for i in range(n):
#         comp = relevant_comps[i]
#         # getting cut nodes
#         if i == 0:
#             in_node = current_node
#         else:
#             in_node = cut_node_dict[(relevant_comps_index[i - 1], relevant_comps_index[i])]
#         if i == n - 1:
#             out_node = target
#         else:
#             out_node = cut_node_dict[(relevant_comps_index[i], relevant_comps_index[i + 1])]
#         counter = disjoint_shimony_pairs(reach_nested.subgraph(comp), in_node, out_node)
#         in_pairs += counter
#         # ex_pairs += pairs
#         sum += len(comp) - 1 - counter
#     # print(state)
#     # # print(pairs)
#     # print(sum)
#     # print('\n\n\n\n\n\n')
#     return sum


def has_flow(s, x, y, t, g):
    # print(list(g.nodes))
    g = get_vertex_disjoint_directed(g)
    g.add_edge("flow_start", str(s) + "out", capacity=1)
    g.add_edge("flow_start", str(x) + "out", capacity=2)
    g[str(s) + 'in'][str(s) + 'out']['capacity'] = 0
    g[str(x) + 'in'][str(x) + 'out']['capacity'] = 0
    g[str(y) + 'in'][str(y) + 'out']['capacity'] = 0
    g[str(t) + 'in'][str(t) + 'out']['capacity'] = 0
    g.add_edge(str(t) + "in", "flow_end", capacity=1)
    g.add_edge(str(y) + "in", "flow_end", capacity=2)
    flow_value, flow_dict = nx.maximum_flow(g, "flow_start", "flow_end")
    g.remove_edge("flow_start", str(s) + "out")
    g.remove_edge("flow_start", str(x) + "out")
    g.remove_edge(str(t) + "in", "flow_end")
    g.remove_edge(str(y) + "in", "flow_end")
    # if flow_value != 3:
    #     print(f"s: {index_to_node[s]} \tx: {index_to_node[x]} \ty: {index_to_node[y]} \tt: {index_to_node[t]} \tflow: {flow_value}")
    return flow_value == 3


def flow_linear_programming_pulp(s, x, y, t, g):
    g = get_vertex_disjoint_directed(g)
    edges = list(g.edges)
    nodes = list(g.nodes)
    # print('starting')

    prob = LpProblem("find_flow", LpMinimize)

    vars = flatten([[(e, f) for e in edges] for f in [1, 2, 3]])
    vars = LpVariable.dicts("es", vars, lowBound=0, upBound=1)

    # objective
    prob += lpSum([vars[(e, 1)] for e in g.out_edges(str(s) + 'out')]
                  + [vars[(e, 2)] for e in g.out_edges(str(x) + 'out')]
                  + [vars[(e, 3)] for e in g.out_edges(str(y) + 'out')]), "total flow we dont care"

    # max total flow is 1 for each edge
    for e in edges:
        prob += lpSum([vars[(e, f)] for f in [1, 2, 3]]) <= 1, f"{e} total flow"

    # in flow is 1 max
    for node in nodes:
        if node not in (str(s) + "in", str(x) + "in"):
            prob += lpSum(flatten([[vars[(e, f)] for e in g.in_edges(node)] for f in [1, 2, 3]])) <= 1, f"{node} max in"

    for node in nodes:
        if node not in (str(s) + "in", str(x) + "in"):
            prob += lpSum([vars[(e, 1)] for e in g.in_edges(node)] + [-1 * vars[(e, 1)] for e in
                                                                      g.out_edges(node)]) == 0, f"{node} in = out f1"

    for node in nodes:
        if node not in (str(x) + "in", str(y) + "in"):
            prob += lpSum([vars[(e, 2)] for e in g.in_edges(node)] + [-1 * vars[(e, 2)] for e in
                                                                      g.out_edges(node)]) == 0, f"{node} in = out f2"

    for node in nodes:
        if node not in (str(y) + "in", str(t) + "in"):
            prob += lpSum([vars[(e, 3)] for e in g.in_edges(node)] + [-1 * vars[(e, 3)] for e in
                                                                      g.out_edges(node)]) == 0, f"{node} in = out f3"

    # s -> x constraint
    prob += lpSum(vars[((str(s) + 'in', str(s) + 'out'), 1)]) == 1, f"S out 1flow"
    prob += lpSum([vars[(e, 1)] for e in g.in_edges(str(x) + 'in')]) == 1, f"X in 1flow"

    # x -> y constraint
    prob += lpSum(vars[((str(x) + 'in', str(x) + 'out'), 2)]) == 1, f"X out 2flow"
    prob += lpSum([vars[(e, 2)] for e in g.in_edges(str(y) + 'in')]) == 1, f"Y in 2flow"
    #
    # # y -> t constraint
    prob += lpSum(vars[((str(y) + 'in', str(y) + 'out'), 3)]) == 1, f"Y out 3flow"
    prob += lpSum([vars[(e, 3)] for e in g.in_edges(str(t) + 'in')]) == 1, f"T in 3flow"

    prob += lpSum([vars[(e, 1)] for e in g.in_edges(str(s) + 'in')]) == 0, f"S in flow 1"
    prob += lpSum([vars[(e, 2)] for e in g.in_edges(str(x) + 'in')]) == 0, f"X in flow 2"
    prob += lpSum([vars[(e, 3)] for e in g.in_edges(str(y) + 'in')]) == 0, f"Y in flow 3"

    # print("+++++++")
    # print(prob)

    # print('solving')
    prob.solve(PULP_CBC_CMD(msg=False))

    # print("status", prob.status, "Total flow =", value(prob.objective))
    # if prob.status != -1:
    #     print(prob.status == 1)
    #     for v in prob.variables():
    #         print(v.name, "=", v.varValue)
    return prob.status == 1


def get_max_nodes(component, in_node, out_node, algorithm):
    # print(f"s:{s}, t:{t}")
    good_pairs = set()
    for path in nx.node_disjoint_paths(component, in_node, out_node):
        p = len(path)
        for i in range(p):
            for j in range(i, p):
                good_pairs.add((path[i], path[j]))
    # print(len(list(graph.nodes)))
    possible_pairs = get_dis_pairs(in_node, out_node, component.nodes, good_pairs)  ### NOT REALLY DISJOINT
    # print(len(possible_pairs))
    pairs = [(x1, x2) for x1, x2 in possible_pairs if
             (not algorithm(in_node, x1, x2, out_node, component)
              and not algorithm(in_node, x2, x1, out_node, component))]
    # print('pairs', [(index_to_node[x], index_to_node[y]) for x,y in pairs])
    res = max_disj_set_upper_bound(component.nodes, pairs)
    # print('ret', res)
    return res


def ex_pairs_using_reg_flow(state, G, target):
    return ex_pairs(state, G, target, has_flow)


def ex_pairs_using_pulp_flow(state, G, target):
    return ex_pairs(state, G, target, flow_linear_programming_pulp)


def ex_pairs_using_brute_force(state, G, target):
    return ex_pairs(state, G, target, is_legit_shimony_pair)


def count_nodes_bcc_testy(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1:
        return -1  # no path
    cut_node_dict = {}
    for node in reachables:
        comps = bcc_dict[node]
        # if node in more than 1 component, its a cut node
        if len(comps) > 1:
            for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
                cut_node_dict[(c1, c2)] = node
                cut_node_dict[(c2, c1)] = node

    n = len(relevant_comps)

    relevant_nodes = 1
    bcc_path_size = 1
    for i in range(n):
        # print('i: ', i)
        comp = relevant_comps[i]
        bcc_path_size += len(comp) - 1
        # getting cut nodes
        if i == 0:
            in_node = current_node
        else:
            in_node = cut_node_dict[(relevant_comps_index[i - 1], relevant_comps_index[i])]
        if i == n - 1:
            out_node = target
        else:
            out_node = cut_node_dict[(relevant_comps_index[i], relevant_comps_index[i + 1])]
        # print('here1')
        graph = reach_nested.subgraph(comp)
        # print('++++comp', [index_to_node[x] for x in comp])
        to_add = len(list(graph.nodes))
        # print('here3', to_add)
        relevant_nodes += to_add - 1
        # print(bcc_path_size - ex_nodes)
        # if to_add > 0:
        #     print(to_add, len(comp), n)
    # print('####################### ', bcc_path_size, relevant_nodes)
    return relevant_nodes


def ex_pairs(state, G, target, algorithm):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1:
        return -1  # no path
    cut_node_dict = {}
    for node in reachables:
        comps = bcc_dict[node]
        # if node in more than 1 component, its a cut node
        if len(comps) > 1:
            for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
                cut_node_dict[(c1, c2)] = node
                cut_node_dict[(c2, c1)] = node

    n = len(relevant_comps)

    relevant_nodes = 1
    bcc_path_size = 1
    for i in range(n):
        # print('i: ', i)
        comp = relevant_comps[i]
        bcc_path_size += len(comp) - 1
        # getting cut nodes
        if i == 0:
            in_node = current_node
        else:
            in_node = cut_node_dict[(relevant_comps_index[i - 1], relevant_comps_index[i])]
        if i == n - 1:
            out_node = target
        else:
            out_node = cut_node_dict[(relevant_comps_index[i], relevant_comps_index[i + 1])]
        # print('here1')
        graph = reach_nested.subgraph(comp)
        # print('++++comp', [index_to_node[x] for x in comp])
        to_add = get_max_nodes(graph, in_node, out_node, algorithm)
        # print('here3', to_add)
        relevant_nodes += to_add - 1
        # print(bcc_path_size - ex_nodes)
        # if to_add > 0:
        #     print(to_add, len(comp), n)
    # print('####################### ', bcc_path_size, relevant_nodes)
    return relevant_nodes
