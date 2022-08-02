import matplotlib.pyplot as plt
import networkx as nx
from helper_functions import *

from heuristics import update_index_to_node

index_to_node = {}


def build_room_graph():
    graph = nx.Graph()
    node_index = 0
    index_to_node = {}
    # set up edges
    for i in range(9):
        for j in range(14):
            graph.add_node(node_index)
            index_to_node[(i, j)] = node_index
            if i > 0:
                graph.add_edge(node_index, index_to_node[(i - 1, j)])
            if j > 0:
                graph.add_edge(node_index, index_to_node[(i, j - 1)])
            node_index += 1

    removed_nodes = [
                        (3, 0), (4, 0),
                        (4, 1), (7, 1),
                        (1, 2), (2, 2), (3, 2),
                        (0, 4), (1, 4), (4, 4), (5, 4), (6, 4), (8, 4),
                        (4, 5),
                        (0, 6), (4, 6),
                        (4, 11),
                        (2, 13), (4, 13), (7, 13)
                    ] + [(i, 9) for i in range(8)]

    remove_nodes_indexes = [index_to_node[node] for node in removed_nodes]
    graph.remove_nodes_from(remove_nodes_indexes)
    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]

    return [(graph, index_to_node[(0, 0)], index_to_node[(8, 13)])]


def build_small_grid():
    global index_to_node
    # graph = nx.grid_2d_graph(5, 5)

    graph = nx.Graph()
    node_index = 0
    index_to_node = {}
    node_to_index = {}
    # set up edges
    for i in range(5):
        for j in range(5):
            graph.add_node(node_index)
            node_to_index[(i, j)] = node_index
            index_to_node[node_index] = (i, j)
            if i > 0:
                graph.add_edge(node_index, node_to_index[(i - 1, j)])
            if j > 0:
                graph.add_edge(node_index, node_to_index[(i, j - 1)])
            node_index += 1

    removed_nodes = [(0, 1), (1, 1), (1, 3), (3, 3)]
    # mat = [[1 if (j, i) in removed_nodes else 0 for i in range (5)] for j in range(5)]

    remove_nodes_indexes = [node_to_index[node] for node in removed_nodes]
    graph.remove_nodes_from(remove_nodes_indexes)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]

    update_index_to_node(index_to_node)
    return 'small grid', graph, node_to_index[(0, 0)], node_to_index[(4, 4)]


def build_small_grid2():
    # graph = nx.grid_2d_graph(5, 5)

    graph = nx.Graph()
    node_index = 0
    index_to_node = {}
    node_to_index = {}
    # set up edges
    for i in range(5):
        for j in range(5):
            graph.add_node(node_index)
            node_to_index[(i, j)] = node_index
            index_to_node[node_index] = (i, j)
            if i > 0:
                graph.add_edge(node_index, node_to_index[(i - 1, j)])
            if j > 0:
                graph.add_edge(node_index, node_to_index[(i, j - 1)])
            node_index += 1

    removed_nodes = [(0, 1), (1, 1), (1, 3), (3, 3)]
    mat = [[1 if (j, i) in removed_nodes else 0 for i in range(5)] for j in range(5)]

    remove_nodes_indexes = [node_to_index[node] for node in removed_nodes]
    graph.remove_nodes_from(remove_nodes_indexes)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]

    return mat, graph, node_to_index[(0, 0)], node_to_index[(4, 4)], index_to_node, node_to_index


def build_small_grid_test():
    # graph = nx.grid_2d_graph(5, 5)

    graph = nx.Graph()
    node_index = 0
    index_to_node = {}
    node_to_index = {}
    # set up edges
    for i in range(5):
        for j in range(5):
            graph.add_node(node_index)
            node_to_index[(i, j)] = node_index
            index_to_node[node_index] = (i, j)
            if i > 0:
                graph.add_edge(node_index, node_to_index[(i - 1, j)])
            if j > 0:
                graph.add_edge(node_index, node_to_index[(i, j - 1)])
            node_index += 1

    removed_nodes = [(0, 1), (1, 1), (1, 3), (3, 3)]
    mat = [[1 if (j, i) in removed_nodes else 0 for i in range(5)] for j in range(5)]

    remove_nodes_indexes = [node_to_index[node] for node in removed_nodes]
    graph.remove_nodes_from(remove_nodes_indexes)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]

    return [(graph, node_to_index[(0, 0)], node_to_index[(4, 4)], index_to_node, node_to_index)]


def build_heuristic_showcase(n):
    s = 0
    t = 4 * n
    path_line = list(range(1, int(n / 2) + 1))
    short_path_line1 = list(range(1 + int(n / 2), int(n / 2 + n / 8)))
    short_path_line2 = list(range(int(n / 2 + n / 8), int(n / 2 + n / 4)))
    blocky = list(range(int(n / 2 + n / 4), n))
    #     print(path_line)
    #     print(short_path_line1)
    #     print(short_path_line2)
    #     print(blocky)
    g = nx.Graph()
    for i in list(range(n + int(n / 8))) + [4 * n]:
        g.add_node(i, constraint_nodes=[i])
    for arr in [path_line, short_path_line1, short_path_line2]:
        for i in range(len(arr) - 1):
            g.add_edge(arr[i], arr[i + 1])

    for i in range(len(blocky)):
        for j in range(i + 1, len(blocky)):
            g.add_edge(blocky[i], blocky[j])

    g.add_edge(s, path_line[0])
    g.add_edge(s, blocky[0])
    g.add_edge(blocky[-1], short_path_line1[0])
    g.add_edge(blocky[-1], short_path_line2[0])
    g.add_edge(short_path_line1[-1], t)
    g.add_edge(short_path_line2[-1], t)
    g.add_edge(path_line[-1], t)

    return f'showcase {n}', g, s, t


def generate_random_grid(height, width, block_p):
    grid = [[(0 if random.uniform(0, 1) > block_p else 1) for i in range(width)] for j in range(height)]
    return generate_grid(grid)


def generate_grid(grid):
    height = len(grid)
    width = len(grid[0])
    path = []
    graph = nx.Graph()
    index_to_node = {}
    node_index = 0
    node_to_index = {}
    # set up edges
    for i in range(height):
        for j in range(width):
            if grid[i][j]:
                continue
            graph.add_node(node_index)
            node_to_index[(i, j)] = node_index
            index_to_node[node_index] = (i, j)
            if i > 0 and not grid[i - 1][j]:
                graph.add_edge(node_index, node_to_index[(i - 1, j)])
            if j > 0 and not grid[i][j - 1]:
                graph.add_edge(node_index, node_to_index[(i, j - 1)])
            node_index += 1

    # choose for path
    while True:
        indexes = range(len(graph.nodes))
        # print(indexes)
        start = list(graph.nodes)[random.choice(indexes)]
        target = list(graph.nodes)[random.choice(indexes)]
        if start == target:
            # print(start, target)
            continue
        try:
            path = nx.shortest_path(graph, source=start, target=target)
            break
        except:
            continue
    # print(path)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]
    # print_mat(grid, index_to_node)
    return grid, graph, start, target, index_to_node


def generate_grids(num_of_runs, height, width, block_p):
    return [generate_random_grid(height, width, block_p) for i in range(num_of_runs)]


def generate_grid2(grid):
    height = len(grid)
    width = len(grid[0])
    path = []
    graph = nx.Graph()
    index_to_node = {}
    node_index = 0
    node_to_index = {}
    # set up edges
    for i in range(height):
        for j in range(width):
            if grid[i][j]:
                continue
            graph.add_node(node_index)
            node_to_index[(i, j)] = node_index
            index_to_node[node_index] = (i, j)
            if i > 0 and not grid[i - 1][j]:
                graph.add_edge(node_index, node_to_index[(i - 1, j)])
            if j > 0 and not grid[i][j - 1]:
                graph.add_edge(node_index, node_to_index[(i, j - 1)])
            node_index += 1

    # choose for path
    while True:
        indexes = range(len(graph.nodes))
        # print(indexes)
        start = list(graph.nodes)[random.choice(indexes)]
        target = list(graph.nodes)[random.choice(indexes)]
        if start == target:
            # print(start, target)
            continue
        try:
            path = nx.shortest_path(graph, source=start, target=target)
            break
        except:
            continue
    # print(path)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]
    # print_mat(grid, index_to_node)
    return grid, graph, start, target, index_to_node, node_to_index


def generate_hard_grids(num_of_runs, height, width, block_p, is_snake=False):
    return [generate_hard_grid(height, width, block_p, is_snake) for i in range(num_of_runs)]


def generate_hard_grid(height, width, block_p, is_snake=False):
    while True:
        try:
            grid = [[(0 if random.uniform(0, 1) > block_p else 1) for i in range(width)] for j in range(height)]
            grid[0][0] = 0
            grid[height - 1][width - 1] = 0
            height = len(grid)
            width = len(grid[0])
            path = []
            graph = nx.Graph()
            index_to_node = {}
            node_index = 0
            node_to_index = {}
            # set up edges
            for i in range(height):
                for j in range(width):
                    if grid[i][j]:
                        continue
                    graph.add_node(node_index)
                    node_to_index[(i, j)] = node_index
                    index_to_node[node_index] = (i, j)
                    if i > 0 and not grid[i - 1][j]:
                        graph.add_edge(node_index, node_to_index[(i - 1, j)])
                    if j > 0 and not grid[i][j - 1]:
                        graph.add_edge(node_index, node_to_index[(i, j - 1)])
                    node_index += 1

            # choose for path
            n = len(index_to_node.keys())
            tries = 200
            start = node_to_index[(0, 0)]
            target = node_to_index[(height - 1, width - 1)]
            path = nx.shortest_path(graph, source=start, target=target)
            # print(path)

            for node in graph.nodes:
                graph.nodes[node]["constraint_nodes"] = list(graph.neighbors(node)) if is_snake else [node]
            break
        except:
            continue
    return grid, graph, start, target, index_to_node


def generate_maze(n, bs):
    mat = [[0] * n] * n
    indexes = flatten(
        [[(i, j) for i in range(n) if (i != 0 or j != 0) and (i != n - 1 or j != n - 1) and mat[i][j] == 0] for j in
         range(n)])
    random.shuffle(indexes)
    for i, j in indexes[:bs]:
        mat_temp = [[1 if i_ == i and j_ == j else mat[i_][j_] for i_ in range(n)] for j_ in range(n)]
        _, graph, _, _, _ = generate_grid(mat_temp)
        if len(list(nx.connected_components(graph))) == 1:
            mat = mat_temp
    grid, graph, start, target, index_to_node = generate_grid(mat)
    return grid, graph, 0, len(index_to_node) - 1, index_to_node


def generate_hypercube(n):
    cube = nx.hypercube_graph(n)
    node_to_index = {}
    i = 0
    for node in cube.nodes:
        cube.nodes[node]["constraint_nodes"] = list(cube.neighbors(node))
        node_to_index[node] = i
        i += 1
    return cube, node_to_index
