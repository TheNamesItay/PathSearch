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
h(state) = sum of degree(bcc) for bcc in P



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
    
## Exclusion Pairs Heuristic Algorithm
state = (current node, path, available nodes) 

####exclusion_pair_heuristic_in_b_component(b_component, exclusion_pair_bound)
    h_val := b_component.size
    exclusion_pair_graph := create_exclusion_pair_graph(b_component, exclusion_pair_bound)
    while exclusion_pair_graph is not empty:
        clique := get_clique(exclusion_pair_graph)
        h_val := h_val - (clique.size - 1)
        remove_clique(clique, exclusion_pair_graph)
    return h_val

      
      
      
      
      
      
      
      
      
