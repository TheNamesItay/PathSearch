def snake_ex_pairs_incremental(state, G, target, algorithm):
    # print('hi')
    current_node = state.current
    if current_node == target:
        return 1
    if not state.bccs:
        #         print('start 1')
        state.bccs = snake_calc_comps(state, G, target, algorithm)
    #         state.print()
    # print('end 1')
    # insert as object
    else:
        bccs = state.bccs
        current_comp_in = bccs[0].in_node
        if current_comp_in != current_node:
            # print('!!!!!!!!!!!!!!!!!!!!!', current_node in bccs[0].nodes)
            first_comp_nodes = bccs[0].nodes
            p_availables = list(intersection(state.available_nodes, first_comp_nodes)) + [current_node]
            pseudo_state = State(current_node, [state.path[-2], current_node], p_availables)
            pseudo_target = bccs[0].out_node
            pseudo_G = G.subgraph(first_comp_nodes)
            # print('start 2')
            extra_comps = snake_calc_comps(pseudo_state, pseudo_G, pseudo_target, algorithm)
            # print('end 1')
            # state.print()
            # state.print_bccs()
            if isinstance(extra_comps, int):
                return extra_comps
            state.bccs = extra_comps + bccs[1:]
            # insert as object
    # state.print()
    #     state.print_bccs()
    relevant_nodes = 1 + sum([c.h - 1 for c in state.bccs])
    return relevant_nodes


def snake_calc_comps(state, G, target, algorithm):
    #     state.print()
    #     print("target:", target)
    _, _, relevant_comps, _, reach_nested, current_node = bcc_thingy(state, G, target)
    #     print(relevant_comps)
    if relevant_comps == -1:
        #         print("relevant comps = -1")
        return -1  # no path
    n = len(relevant_comps)
    if n == 0:
        #         print("no relevant comps")
        return 0
    cut_nodes = [(current_node, target)] if n == 1 else [(current_node,
                                                          list(intersection(relevant_comps[0], relevant_comps[1]))[
                                                              0])] + [(list(
        intersection(relevant_comps[i - 1], relevant_comps[i]))[0], list(
        intersection(relevant_comps[i + 1], relevant_comps[i]))[0]) for i in range(1, n - 1)] + [(list(
        intersection(relevant_comps[n - 2], relevant_comps[n - 1]))[0], target)]
    subgraphs = [reach_nested.subgraph(snake_exclusion_set_spqr(reach_nested.subgraph(comp), in_node, out_node)) for
                 comp, (in_node, out_node) in zip(relevant_comps, cut_nodes)]
    comps_hs = [BiCompEntry(in_node, out_node, comp, algorithm(comp, in_node, out_node)) for (in_node, out_node), comp
                in zip(cut_nodes, subgraphs)]

    return comps_hs


def snake_ex_pairs_using_spqr_prune(state, G, target, is_incremental=False, x_filter=False, y_filter=False,
                                    in_neighbors=False, out_neighbors=False):
    if is_incremental:
        return snake_ex_pairs_incremental(state, G, target,
                                          lambda g, i, o: get_max_nodes_spqr_new(g, i, o, x_filter, y_filter,
                                                                                 in_neighbors, out_neighbors))
    return snake_ex_pairs(state, G, target, lambda g, i, o: get_max_nodes_spqr_new(g, i, o))


def snake_ex_pairs_using_rec_spqr(state, G, target, is_incremental=False, x_filter=False, y_filter=False,
                                  in_neighbors=False, out_neighbors=False):
    if is_incremental:
        return snake_ex_pairs_incremental(state, G, target,
                                          lambda g, i, o: get_max_nodes_recursive_snake(g, i, o, y_filter,
                                                                                        in_neighbors))
    return snake_ex_pairs(state, G, target, lambda g, i, o: get_max_nodes_recursive_snake(g, i, o))


# def snake_ex_pairs_using_spqr_prune_y(state, G, target, is_incremental=False):
#     if is_incremental:
#         return snake_ex_pairs_incremental(state, G, target, lambda g, i, o: get_max_nodes_spqr_y(g, i, o))
#     return snake_ex_pairs(state, G, target, lambda g,i,o: get_max_nodes_spqr_y(g, i, o))


def snake_ex_pairs(state, G, target, algorithm):
    current_node = state.current
    if current_node == target:
        return 1
    comp_hs = snake_ex_pairs_incremental(state, G, target, algorithm)
    if isinstance(comp_hs, int) and comp_hs <= 0:
        return comp_hs
    relevant_nodes = 1 + sum([c.h - 1 for c in comp_hs])
    return relevant_nodes