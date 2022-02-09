from helper_functions import intersection, diff, random
import time as t

F = {}  # state -> weak/strong, F value

MAX_PATH_LEN = 100
# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
FAILURE = -1

# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
CURRENT_NODE = 0
PATH = 1
AVAILABLE_NODES = 2
STRENGTH = 0
H_VALUE = 1
G_VALUE = 2



# F_VALUE = 1

def get_h_and_g(state):
    global F
    return F[state][H_VALUE], F[state][G_VALUE]


def state_value(state, weak_h, g, weight):
    global F
    if state not in F.keys():
        F[state] = ('weak', weak_h(state), g(state))
    return weight * F[state][H_VALUE] + F[state][G_VALUE]   #TODO: check when to add the weight


def set_to_strong_state_value(state, strong_h, g):
    global F
    if state not in F.keys() or not F[state][STRENGTH] == 'strong':
        F[state] = ('strong', strong_h(state), g(state))
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


def max_weighted_lazy_a_star(G, start_state, is_goal, weak_h, strong_h, g, expand=expand_with_constraints, weight=1):
    global F

    def get_state_value(state):
        return state_value(state, weak_h, g, weight)

    F = {}
    start_time = t.time()
    h_vals = []
    lens = []
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
        if expansions % 1000 == 0:
            h_val, g_val = get_h_and_g(q)
            print(f"e-{expansions} state pulled from Open: H_val: {h_val}, g_val: {g_val}, f_val: {h_val + g_val}")

        h_vals += [get_state_value(q)]
        lens += [len(q[PATH])]
        if is_goal(q):
            return q, (expansions, t.time() - start_time, h_vals, lens)
        OPEN += expand(q, OPEN, CLOSED, G)
        expansions += 1
        CLOSED += [q]


def max_weighted_a_star(G, start_state, is_goal, h, g, expand=expand_with_constraints, weight=1):
    global F

    def get_state_value(state):
        return state_value(state, h, g, weight=weight)

    F = {}
    start_time = t.time()
    h_vals = []
    nodes_chosen = []
    lens = []
    OPEN = [start_state]
    CLOSED = []
    expansions = 0
    while OPEN:
        if expansions != 0 and expansions % 100 == 0:
            print(expansions)

        q = max(OPEN, key=get_state_value)
        OPEN.remove(q)
        # if expansions % 1000 == 0:
        #     h_val, g_val = get_h_and_g(q)
        #     print(f"state pulled from Open: H_val: {h_val}, g_val: {g_val}, f_val: {h_val + g_val}")

        h_vals += [get_state_value(q)]
        lens += [len(q[PATH])]
        nodes_chosen += [q[CURRENT_NODE]]

        if is_goal(q):
            return q, (expansions, t.time() - start_time, h_vals, lens, nodes_chosen)
        OPEN += expand(q, OPEN, CLOSED, G)
        expansions += 1
        CLOSED += [q]
    return -1, (expansions, t.time() - start_time, h_vals, lens, nodes_chosen)


def max_a_star_ret_states(G, start_state, is_goal, cutoff, h=lambda a: random.randint(0, 1000), expand=expand_with_constraints):
    OPEN = [(start_state, h(start_state))]
    CLOSED = []
    expansions = 0

    while OPEN:
        if expansions > cutoff > 0:
            return [x[1] for x in CLOSED + OPEN]

        q = max(OPEN, key=lambda x: x[1][0])
        OPEN.remove(q)
        if not is_goal(q[0]):
            OPEN += [(x, h(x)) for x in expand(q[0], OPEN, CLOSED, G)]
        CLOSED += [q]
        expansions += 1
    return [x[1] for x in CLOSED + OPEN]
