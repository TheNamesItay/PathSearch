import networkx as nx

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
from numpy import sort
from scipy.optimize import linprog

from helper_functions import *

CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2
NUM_OF_PAIRS = 5


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
        if len(path) < 2:
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
    ret = 0
    for comp in relevant_comps:
        ret += len(comp)
    return ret


def component_degree(comp, graph):
    graph = graph.subgraph(comp)
    return graph.number_of_edges()


def shimony_pairs_bcc_aprox(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1:
        return len(G.nodes) ** 2  # no path
    cut_node_dict = {}

    n = len(relevant_comps)
    nodes_num = len(reachables)
    comp_degree_coeff = 1 / (nodes_num ** 2)
    in_pairs = 0
    nodes_per_comp = map(lambda comp: (comp_degree_coeff * component_degree(comp, reach_nested)) ** 2, relevant_comps)
    in_pairs = sum(nodes_per_comp)
    inter_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            # for every two nodes in different there's a path from start to target that visits them
            inter_pairs += len(relevant_comps[i]) * len(relevant_comps[j])

    return inter_pairs


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
    return list(nx.edge_disjoint_paths(graph, x1, x2))


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

    paths2 = [find_disjoint_paths(graph, [in_node, x2]), paths[1], find_disjoint_paths(graph, [x1, out_node])]

    return not can_combine_paths(0, paths, [in_node]) and not can_combine_paths(0, paths2, [in_node])


def shimony_pairs(graph, in_node, out_node):
    counter = 1  # first pair is in and out nodes
    done = []
    for x1 in graph.nodes:
        done += [x1]
        if x1 == in_node or x1 == out_node:
            continue
        for x2 in graph.nodes:
            if x2 == in_node or x2 == out_node or x2 in done:
                continue
            if is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
                print(x1, x2)
                counter += 1
    return counter


def shimony_pairs_bcc(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1:
        return len(G.nodes) ** 2  # no path
    cut_node_dict = {}
    for node in reachables:
        comps = bcc_dict[node]
        # if node in more than 1 component, its a cut node
        if len(comps) > 1:
            for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
                cut_node_dict[(c1, c2)] = node
                cut_node_dict[(c2, c1)] = node

    n = len(relevant_comps)
    if n < 3:
        return 0

    in_pairs = 0
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
        in_pairs += shimony_pairs(reach_nested.subgraph(comp), in_node, out_node)

    return in_pairs


# --- SHIMONY PAIRS IMPLEMENTATION 2 ---
def count_pairs_from_paths(graph, s, t):
    pairs = set()
    for path in nx.all_simple_paths(graph, source=s, target=t):
        p = len(path)
        for i in range(p):
            for j in range(i, p):
                pairs.add((path[i], path[j]))
    return len(graph.nodes) * (len(graph.nodes) - 1) - len(pairs)


def shimony_pairs_bcc2(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1:
        return len(G.nodes) ** 2  # no path
    cut_node_dict = {}
    for node in reachables:
        comps = bcc_dict[node]
        # if node in more than 1 component, its a cut node
        if len(comps) > 1:
            for c1, c2 in [(a, b) for idx, a in enumerate(comps) for b in comps[idx + 1:]]:
                cut_node_dict[(c1, c2)] = node
                cut_node_dict[(c2, c1)] = node

    n = len(relevant_comps)
    if n < 3:
        return 0

    in_pairs = 0
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
        in_pairs += count_pairs_from_paths(reach_nested.subgraph(comp), in_node, out_node)

    return in_pairs


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
    if n < 3:
        return 0

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
    print(nodes)
    for i in range(len(nodes)):
        node1 = nodes[i]
        # print(nodes)
        # print(node1)
        # # print(tuple(node1))
        # print(s)
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
    g.add_edge("flow_start", str(s) + "out", capacity=1)
    g.add_edge("flow_start", str(x) + "out", capacity=2)
    g.add_edge(str(t) + "in", "flow_end", capacity=1)
    g.add_edge(str(y) + "in", "flow_end", capacity=2)
    flow_value, flow_dict = nx.maximum_flow(g, "flow_start", "flow_end")
    g.remove_edge("flow_start", str(s) + "out")
    g.remove_edge("flow_start", str(x) + "out")
    g.remove_edge(str(t) + "in", "flow_end")
    g.remove_edge(str(y) + "in", "flow_end")
    return flow_value == 3


def flow_linear_programming(s, x, y, t, g):
    nv = len(g.nodes)
    edges = list(g.edges)
    ne = len(edges)
    # objective
    obj = [-1] * (3 * ne)
    # print(g.nodes)
    # print(f"s: {s}, t: {t}, x: {x}, y: {y}")

    #   edges constraints
    edges_lhs_ineq = [[1 if i in (j, j + ne, j + 2 * ne) else 0 for i in range(3 * ne)] for j in range(ne)]
    edges_rhs_ineq = [1] * ne

    #   vertices constraints
    vertices_lhs_eq_1 = [
        [1 if edges[i] in g.in_edges(node) else -1 if edges[i] in g.out_edges(node) else 0 for i in range(ne)] + [0] * (
                2 * ne) for node in g.nodes if
        node not in (str(s) + "in", str(s) + "out", str(x) + "in", str(x) + "out")]
    vertices_lhs_eq_2 = [
        [0] * ne + [1 if edges[i] in g.in_edges(node) else -1 if edges[i] in g.out_edges(node) else 0 for i in
                    range(ne)] + [0] * ne for node in g.nodes if
        node not in (str(x) + "in", str(x) + "out", str(y) + "in", str(y) + "out")]
    vertices_lhs_eq_3 = [
        [0] * (2 * ne) + [1 if edges[i] in g.in_edges(node) else -1 if edges[i] in g.out_edges(node) else 0 for i in
                          range(ne)] for node in g.nodes if
        node not in (str(y) + "in", str(y) + "out", str(t) + "in", str(t) + "out")]

    # s -> x constraint
    s_out_lhs_eq = [[1 if edges[i] in g.out_edges(str(s) + "out") else 0 for i in range(ne)] + [0] * (2 * ne)]
    x_in_lhs_eq = [[1 if edges[i] in g.in_edges(str(x) + "in") else 0 for i in range(ne)] + [0] * (2 * ne)]

    # x -> y constraint
    x_out_lhs_eq = [[0] * ne + [1 if edges[i] in g.out_edges(str(x) + "out") else 0 for i in range(ne)] + [0] * ne]
    y_in_lhs_eq = [[0] * ne + [1 if edges[i] in g.in_edges(str(y) + "in") else 0 for i in range(ne)] + [0] * ne]

    # y -> t constraint
    y_out_lhs_eq = [[0] * (2 * ne) + [1 if edges[i] in g.out_edges(str(y) + "out") else 0 for i in range(ne)]]
    t_in_lhs_eq = [[0] * (2 * ne) + [1 if edges[i] in g.in_edges(str(t) + "in") else 0 for i in range(ne)]]

    #  combined constraints
    vertices_lhs_eq = vertices_lhs_eq_1 \
                      + vertices_lhs_eq_2 \
                      + vertices_lhs_eq_3 \
                      + s_out_lhs_eq \
                      + x_in_lhs_eq \
                      + x_out_lhs_eq \
                      + y_in_lhs_eq \
                      + y_out_lhs_eq \
                      + t_in_lhs_eq
    # print(len(vertices_lhs_eq_1), len(vertices_lhs_eq_2), len(vertices_lhs_eq_3))

    vertices_rhs_eq = [0] * (3 * (nv - 4)) + [1] * 6
    # print(len(vertices_rhs_eq), len(vertices_lhs_eq))

    # bounds
    bnd = [(0, 1)] * (3 * ne)
    # print("nv", nv, "ne", ne, "len", len(vertices_lhs_eq), len(vertices_rhs_eq))

    opt = linprog(c=obj, A_ub=edges_lhs_ineq, b_ub=edges_rhs_ineq,
                  A_eq=vertices_lhs_eq, b_eq=vertices_rhs_eq, bounds=bnd,
                  method="revised simplex")
    # print(opt.success)
    return opt.success


def get_pairs_flow_and_dis_paths(graph, s, t, di_graph):
    good_pairs = set()
    for path in nx.node_disjoint_paths(graph, s, t):
        p = len(path)
        for i in range(p):
            for j in range(i, p):
                good_pairs.add((path[i], path[j]))
    g_di = di_graph.copy()
    # print(graph.nodes)
    # print("goooooood", good_pairs)
    possible_pairs = get_dis_pairs(s, t, graph.nodes, good_pairs)  ### NOT REALLY DISJOINT
    ex_pairs = {
        x: y for x, y in possible_pairs
        if not flow_linear_programming(s, x, y, t, g_di)
        and not flow_linear_programming(s, y, x, t, g_di)
    }
    print("ex_pairs len: ", len(ex_pairs))
    ep = list(ex_pairs.items())
    counter = 0
    if len(ep) > 0:
        print(len(ep))
    for x, y in ep:
        try:
            ex_pairs.pop(x)
            counter += 1
        except Exception as e:
            pass
        try:
            ex_pairs.pop(y)
        except Exception as e:
            pass
        try:
            ex_pairs.pop(get_key(x, ex_pairs))
        except Exception as e:
            pass
        try:
            ex_pairs.pop(get_key(y, ex_pairs))
        except Exception as e:
            pass
    print("new len: ", counter)
    return counter


def ex_pairs_using_flow(state, G, target):
    reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
                                                                                                        G, target)
    if relevant_comps == -1 or len(relevant_comps) == 0:
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

    ex_pairs = 0
    bcc_path_size = 0
    for i in range(n):
        comp = relevant_comps[i]
        bcc_path_size += len(comp)
        # getting cut nodes
        if i == 0:
            in_node = current_node
        else:
            in_node = cut_node_dict[(relevant_comps_index[i - 1], relevant_comps_index[i])]
        if i == n - 1:
            out_node = target
        else:
            out_node = cut_node_dict[(relevant_comps_index[i], relevant_comps_index[i + 1])]
        graph = reach_nested.subgraph(comp)
        di_graph = get_vertex_disjoint_directed(graph)
        to_add = get_pairs_flow_and_dis_paths(graph, in_node, out_node, di_graph)
        ex_pairs += to_add
        # if to_add > 0:
        #     print(to_add, len(comp), n)
    print('++++++++++++ ', bcc_path_size, ex_pairs)
    return bcc_path_size - ex_pairs
