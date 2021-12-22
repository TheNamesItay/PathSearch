import matplotlib.pyplot as plt
import networkx as nx


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
    # graph = nx.grid_2d_graph(5, 5)

    graph = nx.Graph()
    node_index = 0
    # index_to_node = {}
    # set up edges
    for i in range(5):
        for j in range(5):
            graph.add_node((i, j))
            # index_to_node[(i, j)] = node_index
            if i > 0:
                graph.add_edge((i, j), (i - 1, j))
            if j > 0:
                graph.add_edge((i, j), (i, j - 1))
            node_index += 1

    removed_nodes = [(0, 1), (1, 1), (1, 3), (3, 3)]

    # remove_nodes_indexes = [index_to_node[node] for node in removed_nodes]
    graph.remove_nodes_from(removed_nodes)

    for node in graph.nodes:
        graph.nodes[node]["constraint_nodes"] = [node]

    return [(graph, (0, 0), (4, 4))]


