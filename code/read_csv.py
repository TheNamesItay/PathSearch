# read csv
import csv

CSV_FILENAME = 'test_results.csv'
CSV_FILENAME2 = 'avg_results.csv'
GRAPH_NAME = 0
GRID_SIZE = 1
BLOCKS = 2
WEIGHT = 3
HEURISTIC = 4
EXPANSIONS = 5
RUNTIME = 6
NODES_GENERATED = 7

expansion_results = {}
runtime_results = {}
nodes_generated_results = {}
runs_per_params = 10

# ['Graph', 'Grid Size', 'Blocks', 'A* weight', 'Heuristic', 'Expansions', 'Runtime', 'Generated Nodes']
def read_raw_csv(read_from, write_to):
    with open(read_from, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if not row or row[GRAPH_NAME] == 'Graph':
                continue
            # print(row)
            row_val = (row[GRID_SIZE], row[BLOCKS], row[WEIGHT], row[HEURISTIC])
            if row_val in expansion_results.keys():
                expansion_results[row_val] += int(row[EXPANSIONS])
                runtime_results[row_val] += float(row[RUNTIME])
                nodes_generated_results[row_val] += int(row[NODES_GENERATED])
            else:
                expansion_results[row_val] = int(row[EXPANSIONS])
                runtime_results[row_val] = float(row[RUNTIME])
                nodes_generated_results[row_val] = int(row[NODES_GENERATED])

    for key in expansion_results.keys():
        expansion_results[key] /= runs_per_params
        runtime_results[key] /= runs_per_params
        nodes_generated_results[key] /= runs_per_params

    with open(write_to, 'a', encoding='UTF8') as csv_file:
        writer = csv.writer(csv_file)
        for key in expansion_results.keys():
            row = list(key) + [str(expansion_results[key])] + [str(runtime_results[key])] + [str(nodes_generated_results[key])]
            writer.writerow(row)

def convert_to_latex(file_name_in, file_name_out):
    with open(file_name_out, 'a') as output_file:
        with open(file_name_in, 'r') as csv_file:
            reader = csv.reader(csv_file)
            s_i, s_f_val, s_h_val, s_name, s_expansions, s_runtime, b_i, b_f_val, b_h_val, b_name, b_expansions, b_runtime, inc_runtime = 0,0,0,0,0,0, -1,-1,-1,-1,-1,-1,-1
            for row in reader:
                name = row[4]
                if name == 'spqr incremental':
                    s_i, s_f_val, s_h_val, s_name, s_expansions, s_runtime = row[0], row[1], row[2], row[4], row[5], \
                                                                             row[6]
                elif name == 'bcc incremental':
                    inc_runtime = row[6]
                else:
                    b_i, b_f_val, b_h_val, b_name, b_expansions, b_runtime = row[0], row[1], row[2], row[4], row[5], \
                                                                             row[6]
                if s_i == b_i and s_f_val == b_f_val:
                    line = f"& {5*s_i} & {s_f_val} & {b_expansions} & {b_h_val} & {b_runtime} & {inc_runtime} & {s_expansions} & {s_h_val} & {s_runtime} \\\\"
                    output_file.write(line)
                    output_file.write('\n')

