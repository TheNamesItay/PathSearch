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







## A* algorithm
#### A*(problem_graph, start_state, f, goal_check, cutoff, timeout):
####  expansions = 0
####  state = start_state
####  OPEN = [start_state]
####  CLOSED = []
####  expanded = []
####  while True:
####    if OPEN is empty:
####      return state (should be failure probably)
####    sort(OPEN, f)
####    if expansions = cutoff or timeout reached:
####      return state (not sure if should be failure)
####    if shouldExpand(CLOSED, state, f):
####       CLOSED += [state]
####       nodes = expand(problem_graph, state, expanded)
####       expanded += nodes
####       OPEN += nodes
####       expansion += 1
    
      
      
      
      
      
      
      
      
      
      
      
      
