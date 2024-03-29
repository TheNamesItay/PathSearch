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
let P be path of bi-connected components that include a path from current node to target in the availables nodes graph,  
h(state) = size of set of nodes which are *not* pairwise exclusive in bcc for bcc in P

to calculate the pairs we have 4 main methods:
- brute force
- flow: 
    regular flow: if there is no flow from (s and x) to (y and t) then theres no path from s to t through x and then y. 
    3-flow: using linear programming, calc 3 flows. s->x, x->y, y->t
    calc flow to check if theres a path through x,y then through y,x. if there isnt, its an ex pair.
- SPQR: 
    using the spqr tree data stracture, we can extract the pairs in linear time.
  



## A* algorithm  
state = (current node, path, available nodes)  
#### A*(problem_graph, start_state, f, goal_check, cutoff, timeout):
expansions = 0  
state = start_state  
OPEN = [start_state]
CLOSED = []
expanded = []

while True:  

if OPEN is empty:  
return state (should be failure probably)

if expansions = cutoff or timeout reached:  
return state (not sure if should be failure)

sort(OPEN, f)  
state = smart_pop(OPEN)

if goal reached:  
return state (not sure if should be failure)

CLOSED += [state]  
nodes = expand(problem_graph, state, expanded)  
expanded += nodes  
OPEN += nodes  
expansion += 1
    
      
      
      
      
      
      
      
      
      
      
      
      
