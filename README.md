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
####A*(problem_graph, start_state, f, goal_check, cutoff, timeout):
####\t  expansions = 0
####\t  state = start_state
####\t  OPEN = [start_state]
####\t  CLOSED = []
####\t  expanded = []
####\t  while True:
####\t\t    if OPEN is empty:
####\t\t\t      return state (should be failure probably)
####\t\t    sort(OPEN, f)
####\t\t    if expansions = cutoff or timeout reached:
####\t\t\t      return state (not sure if should be failure)
####\t\t    if shouldExpand(CLOSED, state, f):
####\t\t\t       CLOSED += [state]
####\t\t\t       nodes = expand(problem_graph, state, expanded)
####\t\t\t       expanded += nodes
####\t\t\t       OPEN += nodes
####\t\t\t       expansion += 1
    
      
      
      
      
      
      
      
      
      
      
      
      
