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


def weak_h(state):
    return 0


def strong_h(state):
    return 0


def g(state):
    return 0


def is_goal(state):
    return F[state] == 0 or len(state[PATH]) == MAX_PATH_LEN


def state_value(state):
    if state not in F.keys():
        F[state] = ('weak', weak_h(state) + g(state))
    return F[state][F_VALUE]


def set_to_strong_state_value(state):
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


def max_lazy_a_star(G, start_state, f, is_goal, expand=expand_with_constraints):
    OPEN = [start_state]
    CLOSED = []
    q = None
    expansions = 0
    while OPEN:
        found = False
        while not found:
            q = max(OPEN, key=state_value)
            if is_goal(q):
                return q
            # if we computed the weak heuristic, we need to compute the strong heuristic
            if F[q][STRENGTH] == 'strong':
                OPEN.remove(q)
                found = True
            else:
                set_to_strong_state_value(q)
        OPEN += expand(q, OPEN, CLOSED, G)
        expansions += 1
        CLOSED += [q]
