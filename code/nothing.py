# ex_pairs = {}
    # for x, y in possible_pairs:
    #     # print("possible pairs len: ",len(possible_pairs))
    #     success1, solution1 = flow_linear_programming(s, x, y, t, g_di)
    #     if success1:
    #         possible_pairs = delete_not_possible_pairs(possible_pairs, solution1, s, x, y, t, g_di)
    #     else:
    #         print('failed with ', x, y)
    #     success2, solution2 = flow_linear_programming(s, y, x, t, g_di)
    #     if success2:
    #         possible_pairs = delete_not_possible_pairs(possible_pairs, solution2, s, x, y, t, g_di)
    #     if not success1 and not success2:
    #         ex_pairs[x] = y

    # ex_pairs = {
    #     x: y for x, y in possible_pairs
    #     if not flow_linear_programming(s, x, y, t, g_di)
    #        and not flow_linear_programming(s, y, x, t, g_di)
    # }
    # print("ex_pairs len: ", len(ex_pairs))
    # ep = list(ex_pairs.items())
    # counter = 0
    # if len(ep) > 0:
    #     print(len(ep))
    # for x, y in ep:



def count_nodes_bcc(state, G, target):
    _, _, relevant_comps, _, _, _ = bcc_thingy(state, G, target)
    if relevant_comps == -1:
        return -1  # if theres no path
    ret = 1
    for comp in relevant_comps:
        ret += len(comp) - 1
    return ret




    #     try:
    #         ex_pairs.pop(x)
    #         counter += 1
    #     except Exception as e:
    #         pass
    #     try:
    #         ex_pairs.pop(y)
    #     except Exception as e:
    #         pass
    #     try:
    #         ex_pairs.pop(get_key(x, ex_pairs))
    #     except Exception as e:
    #         pass
    #     try:
    #         ex_pairs.pop(get_key(y, ex_pairs))
    #     except Exception as e:
    #         pass
    # print("new len: ", counter)
    # print(ep)
    # print(ep[0])
    # print(index_to_node[ep[0][0]], index_to_node[ep[0][1]])