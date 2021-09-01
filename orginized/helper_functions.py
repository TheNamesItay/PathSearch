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


def generate_grid(height, width, block_p):
    path = []
    grid = [[(1 if random.uniform(0, 1) > block_p else 0) for i in range(width)] for j in range(height)]
    graph = nx.Graph()
    node_index = 0
    index_to_node = {}

    # set up edges
    for i in range(height):
        for j in range(width):
            if not grid[i][j]:
                continue
            graph.add_node(node_index)
            index_to_node[(i, j)] = node_index
            if i > 0 and grid[i - 1][j]:
                graph.add_edge(node_index, index_to_node[(i - 1, j)])
            if j > 0 and grid[i][j - 1]:
                graph.add_edge(node_index, index_to_node[(i, j - 1)])
            node_index += 1

    # choose for path
    while True:
        indexes = range(node_index)
        start = random.choice(indexes)
        target = random.choice(indexes)
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
    print_mat(grid, index_to_node)
    return graph, start, target


def generate_grids(num_of_runs, height, width, block_p):
    return [generate_grid(height, width, block_p) for i in range(num_of_runs)]
