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

index_to_node = {}


def update_index_to_node(itn):
    global index_to_node
    index_to_node = itn


def g(state):
    path = state[PATH]
    g_value = len(path)
    return g_value


def available_nodes_heuristic(state, G, target):
    left_nodes_num = len(state[AVAILABLE_NODES])
    return left_nodes_num


N = 0


def reachable_nodes_heuristic(state, G, target):
    node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=node)
    return len(reachables) if target in reachables else N


def bcc_thingy(state, G, target):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=current_node)
    reachables.add(current_node)
    reach_nested = nested.subgraph(reachables)
    bcc_comps = list(nx.biconnected_components(reach_nested))
    path = []
    if target in reachables:
        path = nx.shortest_path(reach_nested, source=current_node, target=target)
        if len(path) < 1:
            return -1, -1, -1, -1, -1, -1
    else:
        return -1, -1, -1, -1, -1, -1

    bcc_dict = {}
    for node in reachables:
        bcc_dict[node] = []
    comp_index = 0
    for comp in bcc_comps:
        for node in comp:
            # mapping nodes to biconnected comp
            bcc_dict[node] += [comp_index]
        comp_index += 1

    relevant_comps = []
    relevant_comps_index = []
    added_comp = -1
    # getting only relevant components
    for i in range(len(path) - 1):
        current_comp = -1
        for comp in bcc_dict[path[i]]:
            for comp2 in bcc_dict[path[i + 1]]:
                if comp == comp2:
                    current_comp = comp
        if current_comp == -1:
            raise ConnectionError()
        # print(f"node - {path[i]}\tcomp - {bcc_dict[path[i]]}\t\tcurrent comp - {current_comp}")
        if current_comp != added_comp:
            relevant_comps += [bcc_comps[current_comp]]
            relevant_comps_index += [current_comp]
            added_comp = current_comp

    return reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node


def count_nodes_bcc(state, G, target):
    _, _, relevant_comps, _, _, _ = bcc_thingy(state, G, target)
    if relevant_comps == -1:
        return -1  # if theres no path
    ret = 1
    for comp in relevant_comps:
        ret += len(comp) - 1
    return ret


def component_degree(comp, graph):
    graph = graph.subgraph(comp)
    return graph.number_of_edges()


# def shimony_pairs_bcc_aprox(state, G, target):
#     reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
#                                                                                                         G, target)
#     if relevant_comps == -1:
#         return len(G.nodes) ** 2  # no path
#     cut_node_dict = {}
#
#     n = len(relevant_comps)
#     nodes_num = len(reachables)
#     comp_degree_coeff = 1 / (nodes_num ** 2)
#     in_pairs = 0
#     nodes_per_comp = map(lambda comp: (comp_degree_coeff * component_degree(comp, reach_nested)) ** 2, relevant_comps)
#     in_pairs = sum(nodes_per_comp)
#     inter_pairs = 0
#     for i in range(n):
#         for j in range(i + 1, n):
#             # for every two nodes in different there's a path from start to target that visits them
#             inter_pairs += len(relevant_comps[i]) * len(relevant_comps[j])
#
#     return inter_pairs


def function(state, heuristic, G, target):
    # res = g(state) + heuristic(state, G, target)
    # return res
    return heuristic(state, G, target)


# --- SHIMONY PAIRS IMPLEMENTATION 1 ---
def longest_shortest_path(state, G, target):
    global N
    node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (node,)
    nested = G.subgraph(availables)
    N = len(G.nodes) if N < 0 else N
    try:
        path = nx.shortest_path(nested, source=node, target=target)
        return N - len(path)
    except:
        return N + 1


def find_disjoint_paths(graph, segment):
    x1 = segment[0]
    x2 = segment[1]
    return list(nx.all_simple_paths(graph, x1, x2))


def paths_disjoint(p1, p2):
    for x in p1:
        for y in p2:
            if x == y:
                return False
    return True


def can_combine_paths(m, paths, combined):
    if m > 2:
        return True
    ret = False

    for path in paths[m]:
        if paths_disjoint(path[1:], combined):
            ret = can_combine_paths(m + 1, paths, combined + path[1:])
        if ret:
            break
    return ret


def is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
    segments = [[in_node, x1], [x1, x2], [x2, out_node]]
    paths = []
    for seg in segments:
        paths += [find_disjoint_paths(graph, seg)]
    paths2 = [find_disjoint_paths(graph, [in_node, x2]), [p[::-1] for p in paths[1]],
              find_disjoint_paths(graph, [x1, out_node])]
    # print(paths)
    # print(paths2)
    return not can_combine_paths(0, paths, [in_node]) and not can_combine_paths(0, paths2, [in_node])


def disjoint_shimony_pairs(graph, in_node, out_node):
    global index_to_node
    counter = 0  # first pair is in and out nodes
    done = []
    pairs = []
    for x1 in graph.nodes:
        if x1 == in_node or x1 == out_node or x1 in done:
            continue
        for x2 in graph.nodes:
            if x2 == in_node or x2 == out_node or x1 in done or x2 in done or x1 == x2:
                continue
            if is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
                # di_graph = get_vertex_disjoint_directed(graph)
                # print('3 flow found: ', not (
                #             flow_linear_programming(in_node, x1, x2, out_node, di_graph) or flow_linear_programming(
                #         in_node, x2, x1, out_node, di_graph)))
                # print('regular flow found: ', not (
                #             has_flow(in_node, x1, x2, out_node, di_graph) or has_flow(in_node, x2, x1, out_node,
                #                                                                       di_graph)))
                counter += 1
                done += [x1, x2]
                # print(index_to_node[x1], index_to_node[x2])
                pairs += [(x1, x2)]
    print(pairs)
    return counter


def shimony_pairs_bcc(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1:
        return 0
    cut_node_dict = {}
    for node in reachables:
        comps = bcc_dict[node]
        # if node in more than 1 component, its a cut node
        if len(comps) > 1:
            for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
                cut_node_dict[(c1, c2)] = node
                cut_node_dict[(c2, c1)] = node

    n = len(relevant_comps)
    in_pairs = 0
    ex_pairs = []
    sum = 1
    for i in range(n):
        comp = relevant_comps[i]
        # getting cut nodes
        if i == 0:
            in_node = current_node
        else:
            in_node = cut_node_dict[(relevant_comps_index[i - 1], relevant_comps_index[i])]
        if i == n - 1:
            out_node = target
        else:
            out_node = cut_node_dict[(relevant_comps_index[i], relevant_comps_index[i + 1])]
        counter = disjoint_shimony_pairs(reach_nested.subgraph(comp), in_node, out_node)
        in_pairs += counter
        # ex_pairs += pairs
        sum += len(comp) - 1 - counter
    # print(state)
    # # print(pairs)
    # print(sum)
    # print('\n\n\n\n\n\n')
    return sum


# --- SHIMONY PAIRS IMPLEMENTATION 2 ---
def count_pairs_from_paths(graph, s, t):
    pairs = set()
    for path in nx.all_simple_paths(graph, source=s, target=t):
        p = len(path)
        for i in range(p):
            for j in range(i, p):
                pairs.add((path[i], path[j]))
    return len(graph.nodes) * (len(graph.nodes) - 1) - len(pairs)


# def shimony_pairs_bcc2(state, G, target):
#     reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
#                                                                                                         G, target)
#     if relevant_comps == -1:
#         return len(G.nodes) ** 2  # no path
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
#     if n < 3:
#         return 0
#
#     in_pairs = 0
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
#         in_pairs += count_pairs_from_paths(reach_nested.subgraph(comp), in_node, out_node)
#
#     return in_pairs


def count_easy_shimony_nodes(G, in_node, out_node):
    g = G.copy()
    g.remove_node(in_node)
    g.remove_node(out_node)
    comps = list(nx.connected_components(G))
    # if len(comps) > 1:
    # print("hiiiiiiiiiiiiiiiiiiiiiiii")
    return len(max(comps, key=len))


def easy_ex_nodes(state, G, target):
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

    good_nodes = 0
    for i in range(n):
        comp = relevant_comps[i]
        # getting cut nodes
        if i == 0:
            in_node = current_node
        else:
            in_node = cut_node_dict[(relevant_comps_index[i - 1], relevant_comps_index[i])]
        if i == n - 1:
            out_node = target
        else:
            out_node = cut_node_dict[(relevant_comps_index[i], relevant_comps_index[i + 1])]
        good_nodes += count_easy_shimony_nodes(reach_nested.subgraph(comp), in_node, out_node)

    return good_nodes


def longest_edge_disjoint_path(state, G, target):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    try:
        return len(max(list(nx.edge_disjoint_paths(nested, current_node, target)), key=len))
    except Exception as e:
        return 0


def longest_node_disjoint_path(state, G, target):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    try:
        return len(max(list(nx.disjoint_paths(nested, current_node, target)), key=len))
    except Exception as e:
        return 0


def get_dis_pairs(s, t, nodes, good_pairs):
    possible_pairs = []
    nodes = sort(nodes)
    # nodes = [tuple(node) for node in nodes]
    # print(nodes)
    for i in range(len(nodes)):
        node1 = nodes[i]
        # print(node1, s, t)
        if node1 == s or node1 == t:
            continue
        for j in range(i + 1, len(nodes)):
            node2 = nodes[j]
            if node2 == s or node2 == t:
                continue
            if (node1, node2) in good_pairs:
                continue
            possible_pairs += [(node1, node2)]
    return possible_pairs


def has_flow(s, x, y, t, g):
    # print(list(g.nodes))
    g = get_vertex_disjoint_directed(g)
    g.add_edge("flow_start", str(s) + "out", capacity=1)
    g.add_edge("flow_start", str(x) + "out", capacity=2)
    g[str(s)+'in'][str(s)+'out']['capacity'] = 0
    g[str(x)+'in'][str(x)+'out']['capacity'] = 0
    g[str(y)+'in'][str(y)+'out']['capacity'] = 0
    g[str(t)+'in'][str(t)+'out']['capacity'] = 0
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


def flatten(lst):
    res = []
    for x in lst:
        res += x
    return res


def flow_linear_programming_pulp(s, x, y, t, g):
    g = get_vertex_disjoint_directed(g)
    edges = list(g.edges)
    nodes = list(g.nodes)
    # print('starting')


    prob = LpProblem("find_flow", LpMinimize)

    vars = flatten([[(e, f) for e in edges] for f in [1,2,3]])
    vars = LpVariable.dicts("es", vars, lowBound=0, upBound=1)

    # objective
    prob += lpSum([vars[(e, 1)] for e in g.out_edges(str(s) + 'out')]
                  + [vars[(e, 2)] for e in g.out_edges(str(x) + 'out')]
                  + [vars[(e, 3)] for e in g.out_edges(str(y) + 'out')]), "total flow we dont care"

    # max total flow is 1 for each edge
    for e in edges:
        prob += lpSum([vars[(e, f)] for f in [1,2,3]]) <= 1, f"{e} total flow"

    # in flow is 1 max
    for node in nodes:
        if node not in (str(s) + "in", str(x) + "in"):
            prob += lpSum(flatten([[vars[(e, f)] for e in g.in_edges(node)] for f in [1, 2, 3]])) <= 1, f"{node} max in"

    for node in nodes:
        if node not in (str(s) + "in", str(x) + "in"):
            prob += lpSum([vars[(e, 1)] for e in g.in_edges(node)] + [-1 * vars[(e, 1)] for e in g.out_edges(node)]) == 0, f"{node} in = out f1"

    for node in nodes:
        if node not in (str(x) + "in", str(y) + "in"):
            prob += lpSum([vars[(e, 2)] for e in g.in_edges(node)] + [-1 * vars[(e, 2)] for e in g.out_edges(node)]) == 0, f"{node} in = out f2"

    for node in nodes:
        if node not in (str(y) + "in", str(t) + "in"):
            prob += lpSum([vars[(e, 3)] for e in g.in_edges(node)] + [-1 * vars[(e, 3)] for e in g.out_edges(node)]) == 0, f"{node} in = out f3"

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


def flow_linear_programming(s, x, y, t, g):
    g = get_vertex_disjoint_directed(g)
    nv = len(g.nodes)
    edges = list(g.edges)
    ne = len(edges)
    # objective
    obj = [1] * (3 * ne)
    # obj = [1 if edges[i] in g.in_edges(str(x) + "in") else 0 for i in range(ne)] + [1 if edges[i] in g.in_edges(str(y) + "in") else 0 for i in range(ne)] + [1 if edges[i] in g.in_edges(str(t) + "in") else 0 for i in range(ne)]
    # print(g.nodes)
    # print(f"s: {s}, t: {t}, x: {x}, y: {y}")

    #   edges constraints
    edges_lhs_ineq = [[1 if i in (j, j + ne, j + 2 * ne) else 0 for i in range(3 * ne)] for j in range(ne)]
    # edges_rhs_ineq = [1] * ne

    vertices_lhs_ineq_1 = [
        [1 if edges[i] in g.in_edges(node) else 0 for i in range(ne)] * 3 for node in g.nodes
        if node not in (str(s) + "in", str(x) + "in")]
    # vertices_lhs_ineq_2 = [
    #     [0] * ne + [1 if edges[i] in g.in_edges(node) else 0 for i in range(ne)] + [0] * ne for node in g.nodes
    #     if node not in (str(x) + "in", str(y) + "in")]
    # vertices_lhs_ineq_3 = [
    #     [0] * (2 * ne) + [1 if edges[i] in g.in_edges(node) else 0 for i in range(ne)] for node in g.nodes
    #     if node not in (str(y) + "in", str(t) + "in")]

    lhs_ineq = edges_lhs_ineq + vertices_lhs_ineq_1
    rhs_ineq = [1] * (ne + nv - 2)



    # print(f"=-=-=-=-=-=-=-=- edges[0]: {edges[1]}, g.in_edges(): {g.in_edges(str(s)+'in')}")
    #   vertices constraints
    vertices_lhs_eq_1 = [
        [1 if edges[i] in g.in_edges(node) else -1 if edges[i] in g.out_edges(node) else 0 for i in range(ne)] + [0] * (
                2 * ne) for node in g.nodes if
        node not in (str(s) + "in", str(x) + "in")]
    vertices_lhs_eq_2 = [
        [0] * ne + [1 if edges[i] in g.in_edges(node) else -1 if edges[i] in g.out_edges(node) else 0 for i in
                    range(ne)] + [0] * ne for node in g.nodes if
        node not in (str(x) + "in", str(y) + "in")]
    vertices_lhs_eq_3 = [
        [0] * (2 * ne) + [1 if edges[i] in g.in_edges(node) else -1 if edges[i] in g.out_edges(node) else 0 for i in
                          range(ne)] for node in g.nodes if
        node not in (str(y) + "in", str(t) + "in")]

    # s -> x constraint
    s_out_lhs_eq = [[1 if edges[i] == (str(s)+'in', str(s)+'out') else 0 for i in range(ne)] + [0] * (2 * ne)]
    x_in_lhs_eq = [[1 if edges[i] in g.in_edges(str(x) + "in") else 0 for i in range(ne)] + [0] * (2 * ne)]

    # x -> y constraint
    x_out_lhs_eq = [[0] * ne + [1 if edges[i] == (str(x)+'in', str(x)+'out') else 0 for i in range(ne)] + [0] * ne]
    y_in_lhs_eq = [[0] * ne + [1 if edges[i] in g.in_edges(str(y) + "in") else 0 for i in range(ne)] + [0] * ne]

    # y -> t constraint
    y_out_lhs_eq = [[0] * (2 * ne) + [1 if edges[i] == (str(y)+'in', str(y)+'out') else 0 for i in range(ne)]]
    t_in_lhs_eq = [[0] * (2 * ne) + [1 if edges[i] in g.in_edges(str(t) + "in") else 0 for i in range(ne)]]

    s_in = [[1 if edges[i] in g.in_edges(str(s)+'in') else 0 for i in range(ne)] + [0] * (2 * ne)]
    x_in = [[0] * ne + [1 if edges[i] in g.in_edges(str(x) + 'in') else 0 for i in range(ne)] + [0] * ne]
    y_in = [[0] * (2 * ne) + [1 if edges[i] in g.in_edges(str(y) + 'in') else 0 for i in range(ne)]]


    #  combined constraints
    vertices_lhs_eq = vertices_lhs_eq_1 \
                      + vertices_lhs_eq_2 \
                      + vertices_lhs_eq_3 \
                      + s_out_lhs_eq \
                      + x_in_lhs_eq \
                      + x_out_lhs_eq \
                      + y_in_lhs_eq \
                      + y_out_lhs_eq \
                      + t_in_lhs_eq \
                      + s_in + x_in + y_in
    # print(len(vertices_lhs_eq_1), len(vertices_lhs_eq_2), len(vertices_lhs_eq_3))

    vertices_rhs_eq = [0] * (3 * (nv - 2)) + [1] * 6 + [0] * 3
    # print(len(vertices_rhs_eq), len(vertices_lhs_eq))

    # bounds
    bnd = [(0, 1)] * (3 * ne)
    # print("nv", nv, "ne", ne, "len", len(vertices_lhs_eq), len(vertices_rhs_eq))

    opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq,
                  A_eq=vertices_lhs_eq, b_eq=vertices_rhs_eq, bounds=bnd,
                  method="revised simplex")
    # print(opt.success)
    return opt.success


def get_pairs_flow_and_dis_paths(graph, s, t, flow_alg):
    # print(f"s:{s}, t:{t}")
    good_pairs = set()
    for path in nx.node_disjoint_paths(graph, s, t):
        p = len(path)
        for i in range(p):
            for j in range(i, p):
                good_pairs.add((path[i], path[j]))
    # print(len(list(graph.nodes)))
    possible_pairs = get_dis_pairs(s, t, graph.nodes, good_pairs)  ### NOT REALLY DISJOINT
    # print(len(possible_pairs))
    pairs = [(x1,x2) for x1,x2 in possible_pairs if
             (not flow_alg(s, x1, x2, t, graph)
                and not flow_alg(s, x2, x1, t, graph))]
    # print('pairs', len(pairs))
    res = max_disj_set_upper_bound(graph.nodes, pairs)
    # print('ret', res)
    return res

def delete_not_possible_pairs(possible_pairs, solution, s, x, y, t, g):
    print('start deleteing pairs')
    if all([f==1. or f==0. for f in solution]):
        ne = len(g.edges)
        # flow1, flow2, flow3 = solution[:ne], solution[ne:2*ne], solution[2*ne:]
        path = find_path(solution, s, t, g)
        # print(f"s: {s}, x: {x}, y: {y}, t: {t}")
        # print(f"path contains x and y: {str(x)+'in' in path and str(y)+'in' in path}")
        # print(path)
        path = {x.replace('in', '').replace('out', '') for x in path}
        # print(path)
        # print(possible_pairs)
        for x,y in possible_pairs:
            if str(x) in path and str(y) in path:
                possible_pairs.remove((x,y))
    # print(possible_pairs)
    return possible_pairs

def find_path(flow, s, t, g):
    # print('finding path', s, t)
    edges = list(g.edges)
    ne = len(edges)
    cur_v = str(s)+'in'
    path = [cur_v]
    i=0
    while not cur_v == str(t)+'in':
        # print(f'cur_v: {cur_v}')
        # print(g.out_edges(cur_v))
        # print([flow[edges.index(edge)] for edge in g.out_edges(cur_v)])
        # print([flow[edges.index(edge) + ne] for edge in g.out_edges(cur_v)])
        # print([flow[edges.index(edge) + 2*ne] for edge in g.out_edges(cur_v)])

        for edge in g.out_edges(cur_v):
            # print(flow[edges.index(edge)])
            if flow[edges.index(edge)] == 1. or flow[edges.index(edge) + ne] == 1. or flow[edges.index(edge) + (2 * ne)] == 1.:
                cur_v = edge[1]
                path += [cur_v]
                break
    return path


def ex_pairs_using_3_flow(state, G, target):
    return ex_pairs_using_flow(state, G, target, flow_linear_programming)


def ex_pairs_using_reg_flow(state, G, target):
    return ex_pairs_using_flow(state, G, target, has_flow)


def ex_pairs_using_pulp_flow(state, G, target):
    return ex_pairs_using_flow(state, G, target, flow_linear_programming_pulp)


def ex_pairs_using_flow(state, G, target, flow_alg):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1 or len(relevant_comps) == 0:
        return -1 # no path
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
        to_add = get_pairs_flow_and_dis_paths(graph, in_node, out_node, flow_alg)
        # print('here3', to_add)
        relevant_nodes += to_add - 1
        # print(bcc_path_size - ex_nodes)
        # if to_add > 0:
        #     print(to_add, len(comp), n)
    # print('####################### ', bcc_path_size, relevant_nodes)
    return relevant_nodes


def ex_pairs_using_flow_test(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1 or len(relevant_comps) == 0:
        return -1, -1 # no path
    cut_node_dict = {}
    for node in reachables:
        comps = bcc_dict[node]
        # if node in more than 1 component, its a cut node
        if len(comps) > 1:
            for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
                cut_node_dict[(c1, c2)] = node
                cut_node_dict[(c2, c1)] = node

    n = len(relevant_comps)

    res_lp, res_reg, res_pulp = 1, 1, 1
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
        # di_graph = get_vertex_disjoint_directed(graph)
        res_lp_add, res_reg_add, res_pulp_add = get_pairs_flow_and_dis_paths_test(graph, in_node, out_node)
        # print('here3', to_add)
        res_lp += res_lp_add
        res_reg += res_reg_add
        res_pulp += res_pulp_add
        # print(bcc_path_size - ex_nodes)
        # if to_add > 0:
        #     print(to_add, len(comp), n)
    # print('++++++++++++ ', bcc_path_size, ex_pairs)
    return res_lp, res_reg, res_pulp


def get_pairs_flow_and_dis_paths_test(graph, s, t):
    # print(f"s:{s}, t:{t}")
    good_pairs = set()
    for path in nx.node_disjoint_paths(graph, s, t):
        p = len(path)
        for i in range(p):
            for j in range(i, p):
                good_pairs.add((path[i], path[j]))
    # print(len(list(graph.nodes)))
    possible_pairs = get_dis_pairs(s, t, graph.nodes, good_pairs)  ### NOT REALLY DISJOINT
    # print(len(possible_pairs))

    pairs_lp = [(x1,x2) for x1,x2 in possible_pairs if
             ((not flow_linear_programming(s, x1, x2, t, graph))
                and (not flow_linear_programming(s, x2, x1, t, graph)))]
    pairs_pulp = [(x1, x2) for x1, x2 in possible_pairs if
                 ((not flow_linear_programming_pulp(s, x1, x2, t, graph))
                  and (not flow_linear_programming_pulp(s, x2, x1, t, graph)))]
    pairs_reg = [(x1, x2) for x1, x2 in possible_pairs if
             ((not has_flow(s, x1, x2, t, graph))
              and (not has_flow(s, x2, x1, t, graph)))]
    print('---------------------------------')
    print('nodes: ', [index_to_node[x] for x in graph.nodes])
    print('len lp', len(pairs_lp))
    print('len reg', len(pairs_reg))
    print('pulp len', len(pairs_pulp))
    print('in LP but not reg: ', [(index_to_node[x[0]], index_to_node[x[1]]) for x in pairs_lp if x not in pairs_reg])
    print('in REG but not lp: ', [(index_to_node[x[0]], index_to_node[x[1]]) for x in pairs_reg if x not in pairs_lp])
    print('++++')
    print('in LP but not pulp: ', [(index_to_node[x[0]], index_to_node[x[1]]) for x in pairs_lp if x not in pairs_pulp])
    print('in pulp but not lp: ', [(index_to_node[x[0]], index_to_node[x[1]]) for x in pairs_pulp if x not in pairs_lp])
    res_reg = max_disj_set_upper_bound(graph.nodes, pairs_reg)
    res_pulp = max_disj_set_upper_bound(graph.nodes, pairs_pulp)
    res_lp = max_disj_set_upper_bound(graph.nodes, pairs_lp)
    print("res REG", res_reg)
    print("res LP", res_lp)
    print("res PULP", res_pulp)
    if res_lp != res_reg or res_lp != res_pulp:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print('---------------------------------')
    # print('ret', res)
    return res_lp, res_reg, res_pulp