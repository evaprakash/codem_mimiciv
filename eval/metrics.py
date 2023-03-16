import pandas as pd

#Load results and original data
df = pd.read_csv('/Users/evaprakash/Downloads/cs324/data_filtered_medicines.csv')
results_df = pd.read_csv('/Users/evaprakash/Downloads/cs324/helm/zero_shot_results.csv')

ground_truth = []
predictions = []

at_least_one = {"correct": 0, "total": 0}
all = {"correct": 0, "total": 0}
splits = {"I50": {"correct": 0, "total": 0}, "I25": {"correct": 0, "total": 0}, "N18": {"correct": 0, "total": 0}, "J44": {"correct": 0, "total": 0}}

#Collect GT codes
for index, row in df.iterrows():
	codes = row["icd_codes"].split(" ")
	code_roots = []
	for code in codes:
		code_roots.append(code[:3])
	ground_truth.append(code_roots)
at_least_one["total"] = len(ground_truth)
all["total"] = len(ground_truth)

#Evaluate predicted codes
for index, row in results_df.iterrows():
	pred = row["pred"].split("Answer:")[1].strip()
	print(pred)
	gt = ground_truth[index]
	print(gt)
	all_correct = True
	at_least_one_correct = False
	for code in gt:
		if code in pred:
			at_least_one_correct = True
			splits[code]["correct"] += 1
		else:
			all_correct = False
		splits[code]["total"] += 1
	at_least_one["correct"] += int(at_least_one_correct)
	all["correct"] += int(all_correct)
	print("Done ", index)

#Print results
print(splits)
print("EM: ", float(all["correct"])/all["total"])
print("At least one code matches: ", float(at_least_one["correct"])/at_least_one["total"])
print("I50 accuracy: ", float(splits["I50"]["correct"])/splits["I50"]["total"])
print("I25 accuracy: ", float(splits["I25"]["correct"])/splits["I25"]["total"])
print("N18 accuracy: ", float(splits["N18"]["correct"])/splits["N18"]["total"])
print("J44 accuracy: ", float(splits["J44"]["correct"])/splits["J44"]["total"])
