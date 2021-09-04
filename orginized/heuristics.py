import networkx as nx

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2


def g(state):
    path = state[PATH]
    g_value = len(path)
    return g_value


def available_nodes_heuristic(state, G, target):
    left_nodes_num = len(state[AVAILABLE_NODES])
    return left_nodes_num


def reachable_nodes_heuristic(state, G, target):
    node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=node)
    return len(reachables) if target in reachables else N


N = 10000


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


def is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
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

    segments = [[in_node, x1], [x1, x2], [x2, out_node]]
    paths = []
    for seg in segments:
        paths += [find_disjoint_paths(graph, seg)]

    return can_combine_paths(0, paths, [in_node])


def shimony_pairs(graph, in_node, out_node):
    counter = 1  # first pair is in and out nodes

    for x1 in graph.nodes:
        if x1 == in_node or x1 == out_node:
            continue
        for x2 in graph.nodes:
            if x2 == in_node or x2 == out_node or x2 == x1:
                continue
            if is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
                counter += 1
    return counter


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


def bcc_thingy2(state, G, target):
    current_node = state[CURRENT_NODE]
    availables = state[AVAILABLE_NODES] + (current_node,)
    nested = G.subgraph(availables)
    reachables = nx.descendants(nested, source=current_node)
    reachables.add(current_node)
    reach_nested = nested.subgraph(availables)
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
        return len(G.nodes) + 1  # if theres no path
    ret = 0
    for comp in relevant_comps:
        ret += len(comp)
    return ret


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

    inter_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            # for every two nodes in different there's a path from start to target that visits them
            inter_pairs += len(relevant_comps[i]) * len(relevant_comps[j])

    return inter_pairs + in_pairs


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
