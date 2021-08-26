import networkx as nx
import time as t
import matplotlib.pyplot as plt
import random
from orginized.helper_functions import *


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
            print(combined)
            return True
        ret = False
        for path in paths[m]:
            if paths_disjoint(path[1:], combined):
                ret = can_combine_paths(m+1, paths, combined + path[1:])
            if ret:
                break
        return ret

    segments = [[in_node, x1], [x1, x2], [x2, out_node]]
    paths = []
    for seg in segments:
        paths += [find_disjoint_paths(graph, seg)]

    return can_combine_paths(0, paths, [in_node])


def shimony_pairs(graph, in_node, out_node):
    counter = 1 # first pair is in and out nodes
    for x1 in graph.nodes:
        if x1 == in_node or x1 == out_node:
            continue
        for x2 in graph.nodes:
            if x2 == in_node or x2 == out_node or x2 == x1:
                continue
            if is_legit_shimony_pair(graph, in_node, out_node, x1, x2):
                print(x1, x2)
                counter += 1
    return counter


# graph = nx.Graph()
#
# graph.add_node(1)
# graph.add_node(2)
# graph.add_node(3)
# graph.add_node(4)
# graph.add_node(5)
# graph.add_node(6)
#
# graph.add_edge(1,2)
# graph.add_edge(3,2)
# graph.add_edge(3,4)
# graph.add_edge(5,4)
# graph.add_edge(5,6)
#
# graph.add_edge(1,6)
#
# print(random.uniform(0,1))

grid = generate_grid(10, 10, 0.2)
print(list(grid.nodes))

display_grid([], grid)
