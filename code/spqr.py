from random import random

import networkx as nx

from helper_functions import flatten, diff


def nodes_of_sn(current_sn, parent_sn, tree):
    nodes = list(current_sn[1].networkx_graph().nodes)
    for neighbor in tree.neighbors(current_sn):
        if neighbor == parent_sn:
            continue
        nodes += nodes_of_sn(neighbor, current_sn, tree)
    return nodes


def pairs_p(current_sn, tree, g, s, t):
    sub_nodes = [diff(nodes_of_sn(neighbor_sn, current_sn, tree), current_sn[1].networkx_graph().nodes) for neighbor_sn in tree.networkx_graph().neighbors(current_sn)]
    sub_nodes = [nodes for nodes in sub_nodes if ((s not in nodes or s in current_sn[1].networkx_graph().nodes) and (t not in nodes or t in current_sn[1].networkx_graph().nodes))]
    pairs = []
    for i in range(len(sub_nodes)):
        for j in range(i+1, len(sub_nodes)):
            pairs += flatten([[(n1, n2) if n1 < n2 else (n2, n1) for n1 in sub_nodes[i]] for n2 in sub_nodes[j]])
    return pairs


from itertools import combinations


def get_all_spqr_pairs_new(tree, component, in_node, out_node):
    pairs = []
    for c in tree:
        pairs += pairs_spqr_new(c, tree, component, in_node, out_node)
    pairs = set(pairs)
    #     print(pairs)
    return pairs


def pairs_spqr_new(current_sn, tree, g, s, t):
    if current_sn[0] == 'R':
        pairs = pairs_r(current_sn, tree, g, s, t)
        return pairs
    if current_sn[0] == 'P':
        return pairs_p(current_sn, tree, g, s, t)
    return []


def pairs_r(current_sn, tree, g, s, t):
    # print(f's,t - {(s,t)}')
    super_n_nodes = [nodes_of_sn(neighbor_sn, current_sn, tree) for neighbor_sn in
                     tree.networkx_graph().neighbors(current_sn)]
    super_edges = [tuple(set(intersection(nodes, current_sn[1].networkx_graph().nodes))) for nodes in super_n_nodes]
    super_edges = dict([((min(e), max(e)), diff(nodes, e)) for e, nodes in zip(super_edges, super_n_nodes)])
    super_edges.pop((s, t), None)
    super_edges.pop((t, s), None)
    # print(super_edges)

    sp_nodes = list(current_sn[1].networkx_graph().nodes)
    local_g = g.subgraph(sp_nodes).copy()

    local_g.add_edges_from([e for e in super_edges.keys() if e not in local_g.edges])

    try:
        # s_,t_ = [e for e in local_g.edges if (((s in e) or (e in super_edges.keys() and s in super_edges[e])) and ((t in e) or (e in super_edges.keys() and t in super_edges[e])))][0]
        potential_es = [e for e, ns in super_edges.items() if ((s in e or s in ns) and (t in e or t in ns))] + [e for e
                                                                                                                in
                                                                                                                local_g.edges
                                                                                                                if (
                                                                                                                            s in e and t in e)]
        s_, t_ = potential_es[0]
    except Exception as e:
        print(f's,t - {(s, t)}')
        print(super_edges)
        print(potential_es)
        raise e

    if s not in (s_, t_) or t not in (s_, t_):
        super_edges.pop((s_, t_), None)
        s, t = s_, t_

    # print(f'{(s,t)}, {list(local_g.edges)}')

    # out of s pairs:
    s_edges_nodes = [super_edges[e] for e in super_edges.keys() if s in e]
    s_edge_pairs = []
    for i in range(len(s_edges_nodes)):
        for j in range(i + 1, len(s_edges_nodes)):
            s_edge_pairs += flatten(
                [[(n1, n2) if n1 < n2 else (n2, n1) for n1 in s_edges_nodes[i]] for n2 in s_edges_nodes[j]])

    # out of t pairs:
    t_edges_nodes = [super_edges[e] for e in super_edges.keys() if t in e]
    #     print(t_edges_nodes)
    t_edge_pairs = []
    for i in range(len(t_edges_nodes)):
        for j in range(i + 1, len(t_edges_nodes)):
            t_edge_pairs += flatten(
                [[(n1, n2) if n1 < n2 else (n2, n1) for n1 in t_edges_nodes[i]] for n2 in t_edges_nodes[j]])

    # print(111)
    # edge cut pairs:
    #     print(s,t)
    #     print(super_edges.keys())
    if (s, t) not in super_edges.keys() and (t, s) not in super_edges.keys():
        local_g.remove_edge(s, t)
    cut_pairs = []
    #     print(get_relevant_cuts(local_g, super_edges.keys()))
    for p1, p2 in get_relevant_cuts(local_g, s, t, super_edges.keys()):
        if p1 not in super_edges:
            qw, er = p1
            print((er, qw) in super_edges)
        if p2 not in super_edges:
            qw, er = p2
            print((er, qw) in super_edges)
        #         print(f'1 - {super_edges[p1]}    2 - {super_edges[p2]}')
        cut_pairs += flatten([[(n1, n2) if n1 < n2 else (n2, n1) for n1 in super_edges[p1]] for n2 in super_edges[p2]])
    #     # print(222)
    # draw_grid('', 'r', g, [[0]*20]*20, s, t, itn, path=local_g.nodes)
    # print('in , out - ', s, t)
    # print('edges -', list(local_g.edges))
    # print('cuts -', get_relevant_cuts(local_g, local_g.edges))
    # print('ve')
    # for k,v in super_edges.items():
    #     print(k, '\t', v)
    return list(set(s_edge_pairs + t_edge_pairs + cut_pairs))


def get_neighbors_pairs(component, node):
    node_neighbors = list(component.neighbors(node))
    #     print(in_node_neighbors)
    pairs = set(combinations(node_neighbors, 2))
    #     print(pairs)
    return pairs


def get_max_nodes_spqr_new(component, in_node, out_node, x_filter=False, y_filter=False, in_neighbors=False,
                           out_neighbors=False):
    # print(f"s:{s}, t:{t}")
    component = component.copy()
    if not component.has_edge(in_node, out_node):
        #         print(11)
        component.add_edge(in_node, out_node)
    comp_sage = Graph(component)
    tree = spqr_tree(comp_sage)
    #     for x in tree:
    #         print(x)
    #     print('--------------------------------')
    pairs = get_all_spqr_pairs_new(tree, component, in_node, out_node)
    if in_neighbors:
        pairs.update(get_neighbors_pairs(component, in_node))
    if out_neighbors:
        pairs.update(get_neighbors_pairs(component, out_node))
    res = max_disj_set_upper_bound(component.nodes, pairs, x_filter, y_filter, component)
    # print('ret', res)
    return res


def get_max_nodes_recursive_snake(component, in_node, out_node, y_filter=False, neighbors=False):
    counter = 0
    nodes = get_max_nodes_spqr_recursive(component, in_node, out_node)
    og_g = component.subgraph(nodes).copy()
    if neighbors:
        in_neighbors = diff(list(component.neighbors(in_node)), nodes)
        out_neighbors = diff(list(component.neighbors(out_node)), nodes)
        if not in_neighbors:
            counter += 1
        if not out_neighbors:
            counter += 1
        nodes = [x for x in nodes if x not in in_neighbors and x not in out_neighbors]

    if y_filter:
        while og_g.nodes:
            x = max(og_g.nodes, key=lambda x: og_g.degree[x])
            if og_g.degree[x] < 3:
                break
            # print('---------')
            y = []
            for n in [x] + list(random.sample(list(og_g.neighbors(x)), 3)):
                y += [n]
                nodes.remove(n)
                og_g.remove_node(n)
            #                 print([f for f in y])
            counter += 3
    return len(nodes) + counter


# get all edge cuts

# graph with out (s, t) edge
def get_relevant_cuts(graph, s, t, possible_edges):
    cut_edges = [(e1, e2) for e1, e2 in itertools.combinations(possible_edges, 2) if is_edge_cut((e1, e2), graph, s, t)]
    return cut_edges


def is_edge_cut(edges, graph, s, t):
    g = graph.copy()
    for u, v in edges:
        g.remove_edge(u, v)
    return not nx.is_connected(graph)
#     try:
#         nx.shortest_path(G, s, t)
#         return False
#     except Exception as e:
#         return True