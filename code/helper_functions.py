import random

import matplotlib.pyplot as plt
import networkx as nx


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


def get_random_graph(num_of_nodes, prob_of_edge):
    path = []
    new_graph = nx.fast_gnp_random_graph(num_of_nodes, prob_of_edge)
    print(new_graph.nodes)
    while True:
        indexes = range(num_of_nodes)
        start = random.choice(indexes)
        target = random.choice(indexes)
        if start == target:
            print(start, target)
            continue
        try:
            path = nx.shortest_path(new_graph, source=start, target=target)
            break
        except:
            continue
    print(path)
    for node in new_graph.nodes:
        new_graph.nodes[node]["constraint_nodes"] = [node]
    return new_graph, start, target


def generate_graphs(num_of_runs, num_of_nodes, prob_of_edge):
    return [get_random_graph(num_of_nodes, prob_of_edge) for i in range(num_of_runs)]


def print_mat(mat, dict):
    mat = [[(dict[(i, j)] if mat[i][j] else 0) for i in range(len(mat[0]))] for j in range(len(mat))]
    for arr in mat:
        print(arr)


def generate_random_grid(height, width, block_p):
    grid = [[(0 if random.uniform(0, 1) > block_p else 1) for i in range(width)] for j in range(height)]
    return generate_grid(grid)


def generate_grid(grid):
    height = len(grid)
    width = len(grid[0])
    path = []
    graph = nx.Graph()
    index_to_node = {}

    # set up edges
    for i in range(height):
        for j in range(width):
            if grid[i][j]:
                continue
            node = (i, j)
            graph.add_node(node)
            index_to_node[(i, j)] = node
            if i > 0 and not grid[i - 1][j]:
                graph.add_edge(node, (i - 1, j))
            if j > 0 and not grid[i][j - 1]:
                graph.add_edge(node, (i, j - 1))

    # choose for path
    while True:
        indexes = range(len(graph.nodes))
        print(indexes)
        start = list(graph.nodes)[random.choice(indexes)]
        target = list(graph.nodes)[random.choice(indexes)]
        if start == target:
            print(start, target)
            continue
        try:
            path = nx.shortest_path(graph, source=start, target=target)
            break
        except:
            continue
    print(path)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]
    # print_mat(grid, index_to_node)
    return graph, start, target


def generate_grids(num_of_runs, height, width, block_p):
    return [generate_random_grid(height, width, block_p) for i in range(num_of_runs)]


def get_directed_graph(g):
    g_new = nx.DiGraph()
    d = list(g.nodes).index
    for node in g.nodes:
        g_new.add_node(node)
    for (st, tt) in g.edges:
        s = d(st)
        t = d(tt)
        print('s-', s, ' t-', t)
        node1 = s + t + "'"
        node2 = s + t + "''"
        g.add_node(node1)
        g.add_node(node2)
        g.add_edge(s, node1)
        g.add_edge(t, node1)
        g.add_edge(node2, s)
        g.add_edge(node2, s)
        g.add_node(node1, node2)
    return g_new


def get_vertex_disjoint_directed(g):
    # d = list(g.nodes).index
    g_ret = nx.DiGraph()
    for node in g.nodes:
        node_str = str(node)
        g_ret.add_node(node_str + "in")
        g_ret.add_node(node_str + "out")
        g_ret.add_edge(node_str + "in", node_str + "out", capacity=5)
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


def just_grid(grid):
    height = len(grid)
    width = len(grid[0])
    path = []
    graph = nx.Graph()
    index_to_node = {}
    node_to_index = {}
    index = 0

    # set up edges
    for i in range(height):
        for j in range(width):
            if grid[i][j]:
                continue
            node = (i, j)
            index_to_node[index] = node
            graph.add_node(index)
            node_to_index[(i, j)] = index
            if i > 0 and not grid[i - 1][j]:
                graph.add_edge(index, node_to_index[(i - 1, j)])
            if j > 0 and not grid[i][j - 1]:
                graph.add_edge(index, node_to_index[(i, j - 1)])
            index += 1

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]

    return graph, index_to_node, node_to_index


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
    # # (102, 205, 170),
    # # (69, 139, 116),
    # # (240, 255, 255),
    # # (224, 238, 238),
    # # (193, 205, 205),
    # # (131, 139, 139),
    # # (227, 207, 87),
    # # (245, 245, 220),
    # (255, 228, 196),
    # (238, 213, 183),
    # (205, 183, 158),
    # (139, 125, 107),
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
