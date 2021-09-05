# PathSearch

## Heuristics
state = (graph, current node, path)

#### availables:
h(state) = number of nodes that were not dropped by a constraint

#### reachables:
h(state) = number of available nodes that has a path to node
i.e for each node, check how many nodes it can reach

#### bi-connected components:
let P be path of bi-connected components that include a path from current node to target in the availables nodes graph,  
h(state) = sum of sizeof(bcc) for bcc in P

#### bi-connected component degrees::
let P be path of bi-connected components that include a path from current node to target in the availables nodes graph,  
h(state) = sum of degree(bcc) for bcc in P

#### exclusion pairs::
(u,v) is an exclusion pair for graph g, nodes x,y if theres no path in g from x to y through u,v




## A* algorithm
####A*(problem_graph, start_state, f, goal_check, cutoff, timeout):
expansions = 0  
state = start_state  
OPEN = [start_state]
CLOSED = []
expanded = []

while True:  

if OPEN is empty:  
return state (should be failure probably)

sort(OPEN, f)

if expansions = cutoff or timeout reached:  
return state (not sure if should be failure)

if shouldExpand(CLOSED, state, f):  
CLOSED += [state]  
nodes = expand(problem_graph, state, expanded)  
expanded += nodes  
OPEN += nodes  
expansion += 1
    
      
      
      
      
      
      
      
      
      
      
      
      
