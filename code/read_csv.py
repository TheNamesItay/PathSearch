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
