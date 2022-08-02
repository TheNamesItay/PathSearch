from state import State
from helper_functions import intersection, diff
import time as t


F = {}  # state -> weak/strong, F value

best_path = []
bound = 0
best_state = 0

MAX_PATH_LEN = 100
# STATE = (CURRENT NODE, PATH, AVAILABLE NODES)
FAILURE = -1

STRENGTH = 0
H_VALUE = 1
G_VALUE = 2


F_VALUE = 1

def get_h_and_g(state):
    global F
    return F[state][H_VALUE], F[state][G_VALUE]


def state_value(state, weak_h, g, weight):
    #     global F
    #     if state not in F.keys():
    #         F[state] = ('weak', weak_h(state), g(state))
    #     return weight * F[state][H_VALUE] + F[state][G_VALUE]
    return weak_h(state), g(state)


def set_to_strong_state_value(state, strong_h, g):
    global F
    if state not in F.keys() or not F[state][STRENGTH] == 'strong':
        F[state] = ('strong', strong_h(state), g(state))
    # return F[state][F_VALUE]


def expand_with_constraints(state, OPEN, CLOSED, G, is_incremental, nothing=-1):
    ret = []
    bccs = state.bccs
    current_v = state.current
    neighbors = G.neighbors(current_v)
    available = state.available_nodes
    next_out_node = bccs[0].out_node if is_incremental else -1
    path = state.path
    new_availables = tuple(diff(available, G.nodes[current_v]["constraint_nodes"]))
    neighbor_pool = intersection(intersection(neighbors, available),
                                 state.bccs[0].nodes) if state.bccs else intersection(neighbors, available)
    for v in neighbor_pool:
        if is_incremental and (next_out_node not in new_availables and v != next_out_node):
            continue
        new_path = path + (v,)
        new_state = State(v, new_path, new_availables)
        if is_incremental:
            new_bccs = bccs[1:].copy() if v == next_out_node else bccs
            new_state.bccs = new_bccs
        if new_state not in OPEN and new_state not in CLOSED:
            ret.append(new_state)

    return ret


def reduce_dimensions(n, d, nodes):
    # TODO: remove all the nodes that opened more dimensions than d
    #     ret = nodes.copy()
    ret = []
    check = False
    for node in nodes:
        check = False
        for i in range(n - d):
            if node[i] == 1:
                check = True
        if not check:
            ret += [node]
    #     print("end reducing: ", nodes)
    return ret


def check_dimension(n, node):
    d = 0
    for i in range(n):
        if node[i] == 1:
            d = n - i
            #             print("checking d: ", node, d)
            return d
    #     print("checking d: ", node, d)
    return d


def save_state(save_dir, q, best_state, bound, OPEN, expansions, pruned, runtime, best=False):
    file_name = save_dir
    file_name += '/saved_state.txt' if not best else '/best_states.txt'
    option = 'a' if best else 'w'
    with open(file_name, option) as f:
        f.write(str(len(best_state.path) - 1))
        f.write('\n')
        f.write(str(runtime))
        f.write('\n')
        f.write(str((q.to_tuple(), best_state.to_tuple(), bound, expansions, pruned, runtime)))
        f.write('\n')
        f.write(str([s.to_tuple() for s in OPEN]))
        f.write('\n')


# def save_best_state(save_dir, q, best_state, bound, OPEN, expansions, pruned, runtime):
#     file_name = save_dir + '/best_states.txt'
#     with open(file_name, 'a') as f:
#         f.write(str(len(best_state.path)-1))
#         f.write('\n')
#         f.write(str(runtime))
#         f.write('\n')
#         f.write(str((q.to_tuple(), best_state.to_tuple(), bound, expansions, pruned, runtime)))
#         f.write('\n')
#         f.write(str([s.to_tuple() for s in OPEN]))
#         f.write('\n')


def expand_with_snake_constraints(state, OPEN, CLOSED, G, is_incremental, hypercube_dimension):
    ret = []
    bccs = state.bccs
    current_v = state.current
    dimension = state.snake_dimension
    neighbors = list(G.neighbors(current_v))
    #     print(neighbors)
    neighbors = reduce_dimensions(hypercube_dimension, min(dimension + 1, hypercube_dimension), neighbors.copy())
    #     print(neighbors)
    available = state.available_nodes
    next_out_node = bccs[0].out_node if is_incremental else -1
    path = state.path
    new_availables = tuple(diff(available, G.nodes[current_v]["constraint_nodes"]))
    neighbor_pool = intersection(intersection(neighbors, available),
                                 state.bccs[0].nodes) if state.bccs else intersection(neighbors, available)
    #     print("++++++++ state ++++++++++++++++")
    #     print(f"state: {state.current}, dimension: {state.snake_dimension}")
    #     print("----------expanded---------------")
    for v in neighbor_pool:
        if is_incremental and (next_out_node not in new_availables and v != next_out_node):
            continue
        new_path = path + (v,)
        new_state = State(v, new_path, new_availables)
        #         print(f"v: {v}, d: {dimension}, v_d: {check_dimension(hypercube_dimension, v)}")
        new_state.update_dimension(max(dimension, check_dimension(hypercube_dimension, v)))
        if is_incremental:
            new_bccs = bccs[1:].copy() if v == next_out_node else bccs
            new_state.bccs = new_bccs
        #         if new_state not in OPEN and new_state not in CLOSED:
        #             print(f"state: {new_state.current}, dimension: {new_state.snake_dimension}")
        ret.append(new_state)
    #     print("---------------------------------")
    return ret


def max_weighted_a_star(G, start_state, is_goal, h, g, is_incremental=False, expand=expand_with_constraints, weight=1,
                        cutoff=-1, timeout=-1, hypercube_dimension=-1, save_dir=-1):
    #     global F
    global state_index

    def get_state_value(state):
        return state_value(state, h, g, weight=weight)

    state_index = 0
    F = {}
    start_time = t.time()
    h_vals = []
    nodes_chosen = []
    lens = []
    OPEN = [start_state]
    CLOSED = []
    expansions = 0
    while OPEN:
        # if expansions != 0 and expansions % 1000 == 0:
        #     print(expansions)

        q = max(OPEN, key=get_state_value)
        OPEN.remove(q)
        if expansions % 1000 == 0:
            h_val, g_val = get_h_and_g(q)
            print(f"state pulled from Open: H_val: {h_val}, g_val: {g_val}, f_val: {h_val + g_val}")
            save_state(save_dir, q, q, bound, OPEN, expansions, 0, t.time() - start_time)

        h_vals += [get_state_value(q)]
        lens += [len(q.path)]
        nodes_chosen += [q.current]

        if expansions > cutoff > -1 or t.time() - start_time > timeout > -1:
            return q, (expansions, t.time() - start_time, h_vals, lens, nodes_chosen, len(OPEN) + len(CLOSED))
        if is_goal(q):
            return q, (expansions, t.time() - start_time, h_vals, lens, nodes_chosen, len(OPEN) + len(CLOSED))
        OPEN += expand(q, OPEN, CLOSED, G, is_incremental, hypercube_dimension)
        expansions += 1
        CLOSED += [q]
    return -1, (expansions, t.time() - start_time, h_vals, lens, nodes_chosen, len(OPEN) + len(CLOSED))


def cbsearch(G, state, h, g, is_goal, expand, is_incremental, hypercube_dimension, weight, count):
    global F, best_state, bound, lock

    def get_state_value(state):
        return state_value(state, h, g, weight=weight)

    state_f_val = get_state_value(state)

    if count % 1000 == 0:
        print(state_f_val)

    if state_f_val > bound:
        if is_goal(state):
            #             lock.acquire()
            best_state = max([best_state, state], key=lambda s: len(s.path))
            bound = len(best_state.path)

        #             lock.release()
        #             print("sttate check")
        #             state.print()
        #             best_state = state
        #             bound = state_f_val
        #             print(bound)

        else:
            for s in expand(state, [], [], G, is_incremental, hypercube_dimension):
                cbsearch(G, s, h, g, is_goal, expand, is_incremental, hypercube_dimension, weight, count + 1)


# def max_dfbnb(G, start_state, is_goal, h, g, is_incremental=False, expand=expand_with_snake_constraints, weight=1, cutoff=-1, timeout=-1, hypercube_dimension=-1):
#     global F
#     global best_state
#     global lock


#     state_index = 0
#     F = {}
#     bound = 42
#     best_state = start_state
#     start_time = t.time()
# #     h_vals = []
# #     nodes_chosen = []
# #     lens = []

#     cbsearch(G, start_state, h, g, is_goal, expand, is_incremental, hypercube_dimension, weight, 0)
# #     best_state.print()
#     return best_state, t.time() - start_time


def max_dfbnb_iterative(G, start_state, is_goal, h, g, is_incremental=False, expand=expand_with_snake_constraints,
                        weight=1, cutoff=-1, timeout=-1, hypercube_dimension=-1, save_dir=-1):
    #     global F
    global state_index
    global best_state

    def get_state_value(state):
        return state_value(state, h, g, weight=weight)

    bounds = {3: 3, 4: 5, 5: 11, 6: 23, 7: 45, 8: 93, 9: 187, 10: 365, 11: 691, 12: 1343, 13: 2593}
    bound = bounds[hypercube_dimension]

    best_state = start_state

    #     OPEN = np.zeros((bound * 2, hypercube_dimension))
    #     print(arr)

    state_index = 0
    #     F = {}
    start_time = t.time()
    #     h_vals = []
    #     nodes_chosen = []
    #     lens = []
    #     OPEN[0][0] = start_state
    OPEN = [start_state]
    #     CLOSED = []
    expansions = 0
    pruned = 0

    while OPEN:
        # if expansions != 0 and expansions % 1000 == 0:
        #     print(expansions)
        #         q = OPEN[depth][place]
        q = OPEN.pop()
        h_val, g_val = get_state_value(q)
        q_val = weight * h_val + g_val

        if expansions % 10000 == 0:
            #             h_val, g_val = get_h_and_g(q)
            print(f"state pulled from Open: H_val: {h_val}, g_val: {g_val}, f_val: {h_val + g_val}")
            save_state(save_dir, q, best_state, bound, OPEN, expansions, pruned, t.time() - start_time)

        if expansions > cutoff > -1 or t.time() - start_time > timeout > -1:
            print('--------wtf------')
            return best_state, (expansions, t.time() - start_time, [0], [0], [0], pruned)

        if q_val <= bound:
            pruned += 1
        else:

            #             h_vals += [q_val]
            #             lens += [len(q.path)]
            #             nodes_chosen += [q.current]

            if is_goal(q):
                bound = q_val
                best_state = q
                print(f'found path: {bound - 1}')
                save_state(save_dir, q, best_state, bound, OPEN, expansions, pruned, t.time() - start_time, best=True)
            else:
                OPEN += expand(q, OPEN, [], G, is_incremental, hypercube_dimension)
                #                 if len(expanded) == 0:
                #                     print(f'open len: {len(OPEN)}')
                #                     print(f'depth: {len(q.path)}')
                #                 else:
                #                     OPEN += expanded
                expansions += 1
    #                 CLOSED += [q]
    return best_state, (expansions, t.time() - start_time, [0], [0], [0], pruned)
