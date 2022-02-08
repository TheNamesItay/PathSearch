

def available_nodes_heuristic(state, G, target):
    left_nodes_num = len(state[AVAILABLE_NODES])
    return left_nodes_num



def reachable_nodes_heuristic(state, G, target):
    node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=node)
    return len(reachables) if target in reachables else N


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

# def easy_ex_nodes(state, G, target):
#     reachables, bcc_dict, relevant_comps, relevant_comps_index, reach_nested, current_node = bcc_thingy(state,
#                                                                                                         G, target)
#     if relevant_comps == -1:
#         return -1  # no path
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
#
#     good_nodes = 0
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
#         good_nodes += count_easy_shimony_nodes(reach_nested.subgraph(comp), in_node, out_node)
#
#     return good_nodes


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
