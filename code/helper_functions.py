import itertools
import math
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from numpy import sort
from scipy.optimize import linprog

from state import State


CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2
BCC_DICT = 3
NUM_OF_PAIRS = 5
N = 0
index_to_node = {}


def all_pairs(lst):
    res = set()
    for i in range(len(lst)):
        for j in range(len(lst)):
            res.add((lst[i], lst[j]))
    return res


def includes(big, small):
    return not [x for x in small if x not in big]


def diff(li1, li2):
    return list(set(li1) - set(li2))


def intersection(lst1, lst2):
    # Use of hybrid method
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3


def display_graph(path, g):
    graph = g.copy()
    pos = nx.kamada_kawai_layout(graph)
    if not path:
        nx.draw(graph, pos, with_labels=True)
    else:
        x1 = path[0]
        for i in range(1, len(path)):
            x2 = path[i]
            graph[x1][x2]['color'] = "red"
            x1 = x2
        colors = nx.get_edge_attributes(graph, 'color').values()
        nx.draw(graph, pos, with_labels=True, edge_color=colors)
    plt.show()


def display_grid(path, g):
    graph = g.copy()
    pos = nx.spring_layout(graph)
    if not path:
        nx.draw(graph, pos, with_labels=True)
    else:
        x1 = path[0]
        for i in range(1, len(path)):
            x2 = path[i]
            graph[x1][x2]['color'] = "red"
            x1 = x2
        colors = nx.get_edge_attributes(graph, 'color').values()
        nx.draw(graph, pos, with_labels=True, edge_color=colors)
        plt.show()


def print_mat(mat, dict):
    mat = [[(dict[(i, j)] if mat[i][j] else 0) for i in range(len(mat[0]))] for j in range(len(mat))]
    for arr in mat:
        print(arr)


def get_vertex_disjoint_directed(g):
    # d = list(g.nodes).index
    g_ret = nx.DiGraph()
    for node in g.nodes:
        node_str = str(node)
        g_ret.add_node(node_str + "in")
        g_ret.add_node(node_str + "out")
        g_ret.add_edge(node_str + "in", node_str + "out", capacity=1)
    for st, tt in g.edges:
        s, t = st, tt
        g_ret.add_edge(str(s) + "out", str(t) + "in", capacity=1)
        g_ret.add_edge(str(t) + "out", str(s) + "in", capacity=1)
    return g_ret


def get_key(val, dict):
    a = list(dict.keys())
    b = list(dict.values())
    try:
        return a[b.index(val)]
    except Exception as e:
        return -1

comp_colors = [
    # (240, 248, 255),
    # # (250, 235, 215),
    # # (238, 223, 204),
    # (255, 239, 219),
    # # (205, 192, 176),
    # # (139, 131, 120),
    # # (0, 255, 255),
    # # (127, 255, 212),
    # # (118, 238, 198),
    (102, 205, 170),
    (69, 139, 116),
    # (240, 255, 255),
    # # (224, 238, 238),
    # # (193, 205, 205),
    # # (131, 139, 139),
    # # (227, 207, 87),
    # # (245, 245, 220),
    # (255, 228, 196),
    (238, 213, 183),
    (205, 183, 158),
    (139, 125, 107),
    # (0, 0, 0),
    # (255, 235, 205),
    # (0, 0, 255),
    # (0, 0, 238),
    # (0, 0, 205),
    # (0, 0, 139),
    (138, 43, 226),
    (156, 102, 31),
    (165, 42, 42),
    # (255, 64, 64),
    # (238, 59, 59),
    # (205, 51, 51),
    (139, 35, 35),
    (222, 184, 135),
    (255, 211, 155),
    (238, 197, 145),
    (205, 170, 125),
    (139, 115, 85),
    (138, 54, 15),
    (138, 51, 36),
]


def random_combination(iterable, r, n):
    "Random selection from itertools.combinations(iterable, r)"
    return [iterable.__next__()] * min(n-1, r)


def get_clique(node, graph):
    g = graph.subgraph(list(graph.neighbors(node)))
    if not g.nodes:
        return [node]
    else:
        x = max(g.nodes, key=lambda x: g.degree[x])
        return [node] + get_clique(x, g)


def is_subclique(G, nodelist):
    if len(nodelist) == 1:
        return True
    H = G.subgraph(nodelist)
    n = len(nodelist)
    return H.size() == n * (n - 1) / 2


def get_clique_bf(node, graph):
    # print("NODE: ", node)
    res = [node]
    nodes = list(graph.neighbors(node)) + [node]
    l = len(nodes)
    for i in range(len(nodes)):
        for subset in itertools.combinations(nodes, l - i):
            # print(l-i,subset)
            if is_subclique(graph, subset):
                # print("RES: ", subset, graph.degree[node], len(subset))
                return subset


def max_disj_set_upper_bound(nodes, pairs):
    g = nx.Graph()
    for x in nodes:
        g.add_node(x)
    for s, t in pairs:
        g.add_edge(s, t)
    degrees = g.degree
    counter = 0
    # print("nodes", len(list(g.nodes)))
    # print("pairs", pairs)
    while g.nodes:
        x = max(g.nodes, key=lambda x: degrees[x])
        c = get_clique(x, g)
        # print(len(c))
        for n in c:
            g.remove_node(n)
        counter += 1
    # print('counter', counter)
    # print('----------------------------------')
    return counter


def max_bad_set_upper_bound(nodes, pairs):
    g = nx.Graph()
    for x in nodes:
        g.add_node(x)
    for s, t in pairs:
        g.add_edge(s, t)
    degrees = g.degree
    counter = 0
    # print("nodes", list(g.nodes))
    # print("pairs", pairs)
    while g.nodes:
        x = max(g.nodes, key=lambda x: degrees[x])
        if degrees[x] == 0:
            break
        # c = get_clique(x, g)
        c = [x, list(g.neighbors(x))[0]] if list(g.neighbors(x)) else [x]
        for n in c:
            g.remove_node(n)
        counter += 1
    # print('counter', counter)
    # print('----------------------------------')
    return counter


def bcc_thingy(state, G, target):
    current_node = state.current
    availables = state.available_nodes + (current_node,)
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


def component_degree(comp, graph):
    graph = graph.subgraph(comp)
    return graph.number_of_edges()


def flatten(lst):
    res = []
    for x in lst:
        res += x
    return res

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

        for edge in g.out_edges(cur_v):
            # print(flow[edges.index(edge)])
            if flow[edges.index(edge)] == 1. or flow[edges.index(edge) + ne] == 1. or flow[edges.index(edge) + (2 * ne)] == 1.:
                cur_v = edge[1]
                path += [cur_v]
                break
    return path


def triconnected_components(component):
    "Return the triconnected components of the graph."
    print('start')
    comp_nodes = list(component.nodes)
    components = []
    if len(component) < 3:
        return [comp_nodes]
    try:
        cuts = next(nx.all_node_cuts(
            component,
            k=2))
        if len(cuts) > 2:
            return [comp_nodes]
        assert len(cuts) == 2
        comp_min_cuts = component.copy()
        comp_min_cuts.remove_nodes_from(cuts)
        subcomponents = list(nx.connected_components(comp_min_cuts))
        if len(subcomponents) == 1:
            return [comp_nodes]
        components += subcomponents
        components.append(cuts)
    except StopIteration:
        return [comp_nodes]
    return components

def draw_grid(folder_name, pic_name, graph, mat, start, target, index_to_node):
    start_available = tuple(diff(list(graph.nodes), graph.nodes[start]["constraint_nodes"]))
    start_path = (start,)
    state = State(start, start_path, start_available)
    t = index_to_node[target]
    _, _, comps, _, _, _ = bcc_thingy(state, graph, target)
    current_node = index_to_node[state.current]
    path = [index_to_node[x] for x in state.path]
    height = len(mat)
    width = len(mat[0])
    data = [[(0, 0, 0) if mat[j][i] else (255, 255, 255) for j in range(len(mat[0]))] for i in range(len(mat))]
    if comps:
        for i in range(len(comps)):
            color = comp_colors[i % len(comp_colors)]
            comp = comps[i]
            for c in comp:
                node = index_to_node[c]
                data[node[1]][node[0]] = color
        for v in path:
            data[v[1]][v[0]] = (50, 50, 150)
    data[current_node[1]][current_node[0]] = (255, 0, 255)
    data[t[1]][t[0]] = (0, 255, 0)

    fig, ax = plt.subplots()
    ax.imshow(data, )

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.5)
    ax.set_xticks(np.arange(-.5, width, 1))
    ax.set_yticks(np.arange(-.5, height, 1))
    plt.title('graph ' + str(pic_name))
    save_results_to = "D:\sage\SageMath 9.3\dump"
    fig.savefig(save_results_to + f'graph_{str(pic_name)}.png')
