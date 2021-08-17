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
