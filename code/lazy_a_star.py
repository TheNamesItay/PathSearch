import time as t
from helper_functions import intersection, diff

F = {}  # state -> weak/strong, F value

MAX_PATH_LEN = 100
# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
FAILURE = -1

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2
STRENGTH = 0
F_VALUE = 1

# DATA = (expansions, runtime, nodes_extracted_heuristic_values, nodes_extracted_path_len)
EXPANSIONS = 0
RUNTIME = 1
H_VALS = 2
LENS = 3



def state_value(state, weak_h, g):
    global F
    if state not in F.keys():
        F[state] = ('weak', weak_h(state) + g(state))
    return F[state][F_VALUE]


def set_to_strong_state_value(state, strong_h, g):
    global F
    if state not in F.keys() or not F[state][STRENGTH] == 'strong':
        F[state] = ('strong', strong_h(state) + g(state))
    # return F[state][F_VALUE]


def expand_with_constraints(state, OPEN, CLOSED, G):
    ret = []
    if state is None:
        return ret
    current_v = state[CURRENT_NODE]
    neighbors = G.neighbors(current_v)
    available = state[AVAILABLE_NODES]
    path = state[PATH]
    for v in intersection(neighbors, available):
        new_path = path + (v,)
        new_availables = tuple(diff(available, G.nodes[current_v]["constraint_nodes"]))
        new_state = (v, new_path, new_availables)
        if new_state not in OPEN and new_state not in CLOSED:
            ret.append(new_state)
    return ret


def max_lazy_a_star(G, start_state, is_goal, weak_h, strong_h, g, expand=expand_with_constraints):
    def get_state_value(state):
        return state_value(state, weak_h, g)

    OPEN = [start_state]
    CLOSED = []
    q = None
    expansions = 0
    while OPEN:
        found = False
        while not found:
            q = max(OPEN, key=get_state_value)
            # if we computed the weak heuristic, we need to compute the strong heuristic
            if F[q][STRENGTH] == 'strong':
                OPEN.remove(q)
                found = True
            else:
                set_to_strong_state_value(q, strong_h, g)
        if is_goal(q):
            return q
        OPEN += expand(q, OPEN, CLOSED, G)
        expansions += 1
        CLOSED += [q]


def max_a_star(G, start_state, is_goal, h, g, expand=expand_with_constraints):
    global F
    def get_state_value(state):
        return state_value(state, h, g)
    F = {}
    start_time = t.time()
    h_vals = []
    lens = []
    OPEN = [start_state]
    CLOSED = []
    expansions = 0
    while OPEN:
        if expansions % 100 == 0:
            print(expansions, end='\r')

        q = max(OPEN, key=get_state_value)
        OPEN.remove(q)

        h_vals += [get_state_value(q)]
        lens += [len(q[PATH])]

        if is_goal(q):
            return q, (expansions, t.time() - start_time, h_vals, lens)
        OPEN += expand(q, OPEN, CLOSED, G)
        expansions += 1
        CLOSED += [q]
    return -1, (expansions, t.time() - start_time, h_vals, lens)