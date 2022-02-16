import csv

CSV_FILENAME = 'test_results.csv'
CSV_FILENAME2 = 'avg_results.csv'

expansion_results = {}
runtime_results = {}
runs_per_params = 10


with open(CSV_FILENAME, 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        row_val = (row[0], row[1], row[2], row[3])
        if row_val in expansion_results.keys():
            expansion_results[row_val] += int(row[4])
            runtime_results[row_val] += float(row[5])
        else:
            expansion_results[row_val] = int(row[4])
            runtime_results[row_val] = float(row[5])

for key in expansion_results.keys():
    expansion_results[key] /= runs_per_params
    runtime_results[key] /= runs_per_params


with open(CSV_FILENAME2, 'a', encoding='UTF8') as csv_file:
    writer = csv.writer(csv_file)
    for key in expansion_results.keys():
        row = list(key) + [str(expansion_results[key])] + [str(runtime_results[key])]
        writer.writerow(row)
