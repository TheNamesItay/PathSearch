# PathSearch

## Heuristics
state = (graph, current node, path)

#### availables:
h(state) = number of nodes that were not dropped by a constraint

#### reachables:
h(state) = number of available nodes that has a path to node
i.e for each node, check how many nodes it can reach

#### largest connected group:
h(state) = largest connected component between the available nodes
#### largest connected group degree:
