import networkx as nx
from heuristics import bcc_thingy, flow_linear_programming, get_dis_pairs, get_vertex_disjoint_directed, has_flow
import random
from helper_functions import *
import time as t

levels = 10
runs = 20
n = 200
jump = 200
nodes = list(range(n + 1))

# pairs = [(1,2), (2,3)]
#
# print(max_disj_set_naive(nodes, pairs))
# print(max_disj_set_lp(nodes, pairs))

lp_avgs = []
n_avgs = []
X = []

for i in range(levels):
    p_max = jump * (i + 1)
    naive_res = []
    naive_runtime = 0
    lp_res = []
    lp_runtime = 0

    pairs_lst = []

    for i in range(runs):
        pairs = []
        for p in range(p_max):
            x = random.randint(0, n)
            y = random.randint(0, n)
            if x == y or (x, y) in pairs or (y, x) in pairs:
                continue
            pairs += [(x, y)]
        pairs_lst += [pairs]

    p_lens = [len(p) for p in pairs_lst]

    start_time = t.time()
    for p in pairs_lst:
        r_lp = max_disj_set_lower_bound(nodes, p)
        lp_res += [r_lp]
    lp_runtime = t.time() - start_time

    start_time = t.time()
    for p in pairs_lst:
        r_naive = max_disj_set_naive(nodes, p)
        naive_res += [r_naive]
    naive_runtime = t.time() - start_time

    zipped_res = list(zip(naive_res, lp_res))
    lp_score = 0
    naive_score = 0
    lp_n_diff = 0
    n_sum = 0
    lp_sum = 0

    for nr, lpr in zipped_res:
        # lp_score += 1 if lpr > nr else 0
        # naive_score += 1 if lpr < nr else 0
        lp_n_diff += lpr - nr
        n_sum += nr
        lp_sum += lpr

    lp_n_diff = lp_n_diff / runs
    n_avg = n_sum / runs
    lp_avg = lp_sum / runs

    p_lens_avg = sum(p_lens) / runs

    print(f'RUNS - {runs}')
    print(f'NAIVE    - \tAVG={n_avg} \truntime={naive_runtime}')
    print(f'LP       - \tAVG={lp_avg} \truntime={lp_runtime}')
    print(f'AVG lp - naive = {lp_n_diff}')
    print(f'avg NUM OF PAIRS - {p_lens_avg}')

    lp_avgs += [lp_avg]
    n_avgs += [n_avg]
    X += [p_lens_avg]

plt.plot(X, lp_avgs)
plt.plot(X, n_avgs)
plt.show()

# X = [99.1, 197.75, 297.1, 394.35, 491.65, 588.0, 684.9, 779.85, 874.3, 969.0]
# plt.plot(X, [0.16900014877319336, 0.16796612739562988, 0.12503838539123535, 0.10303330421447754, 0.09506797790527344,
#              0.10998249053955078, 0.0870048999786377, 0.08199858665466309, 0.08804583549499512, 0.08721160888671875])
# plt.plot(X, [8.29439401626587, 25.10199546813965, 51.923659563064575, 81.98089075088501, 104.20804929733276,
#              129.7682502269745, 154.1645655632019, 181.04891538619995, 206.59335064888, 227.19769048690796])
# plt.show()


# n = [1, 2, 3, 4, 5, 6, 7]
# p = [
#     [1, 2],
#     [1, 3],
#     [1, 4],
#     [1, 5],
#     [2, 3],
#     [2, 4],
#     [3, 4],
# ]
# max_disj_set_lower_bound(n, p)