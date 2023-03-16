import numpy as np
import pandas as pd
from collections import defaultdict
import random

N = 5000

#Load MIMIC IV data (clinical notes and diagnoses)
discharge_df = pd.read_csv('discharge.csv')
diagnoses_df = pd.read_csv('diagnoses_icd.csv')  
prescriptions_df = pd.read_csv('prescriptions.csv')  

#Extract ICD-10 codes
diagnoses_df = diagnoses_df.query("icd_version == 10")

#Extract four major chronic health conditions
diagnoses_df = diagnoses_df[diagnoses_df.icd_code.str.contains('(I50)+|(N18)+|(J44)+|(I25)+', regex=True, na=False)]
diagnoses_df['icd_root'] = diagnoses_df['icd_code'].str[:3]

#Filter clinical notes
icd_10_hadm_ids = random.sample(list(set(diagnoses_df["hadm_id"].values.tolist())), N)
discharge_df = discharge_df[discharge_df["hadm_id"].isin(icd_10_hadm_ids)]

#Load filtered hadm and subject ids into new data frame
hadm_to_subject_id = dict()
for index, entry in diagnoses_df.iterrows():
	if (entry["hadm_id"] in hadm_to_subject_id):
		continue
	else:
		hadm_to_subject_id[entry["hadm_id"]] = entry["subject_id"]
icd_10_subject_ids = [hadm_to_subject_id[hadm_id] for hadm_id in icd_10_hadm_ids]
query_df = pd.DataFrame()
query_df["hadm_id"] = icd_10_hadm_ids
query_df["subject_id"] = icd_10_subject_ids

#Add ICD codes to new data frame
hadm_to_icd = dict()
for i in icd_10_hadm_ids:
	icd_codes = diagnoses_df.loc[diagnoses_df['hadm_id'] == i, 'icd_code'].values.tolist()
	icd_code_string = ""
	for code in icd_codes:
		icd_code_string += code + " "
	hadm_to_icd[i] = icd_code_string.strip()
icd_10_codes = [hadm_to_icd[hadm_id] for hadm_id in icd_10_hadm_ids]
query_df["icd_codes"] = icd_10_codes

#Collect chief complaints
hadm_ids = []
for hadm in discharge_df["hadm_id"].values:
	hadm_ids.append(hadm)
hadm_to_chief_complaints = dict()
n = 0
for text in discharge_df["text"].values:
	lines = text.split("\n")
	if "Chief Complaint:" not in lines:
		hadm_to_chief_complaints[hadm_ids[n]] = "None"
		n += 1
		continue
	c = lines[lines.index("Chief Complaint:") + 1]
	if not any(x.isalpha() for x in c):
		hadm_to_chief_complaints[hadm_ids[n]] = "None"
		n += 1
		continue	
	hadm_to_chief_complaints[hadm_ids[n]] = c.strip()
	n += 1
icd_10_chief_complaints = []
for hadm_id in icd_10_hadm_ids:
	if hadm_id not in hadm_to_chief_complaints:
		icd_10_chief_complaints.append("None")
	else:
		icd_10_chief_complaints.append(hadm_to_chief_complaints[hadm_id])
query_df["chief_complaints"] = icd_10_chief_complaints
query_df.to_csv('data_filtered.csv', index=False)

#Collect medicines
n = 0
hadm_to_drugs = dict()
for hadm in icd_10_hadm_ids:
	drugs = prescriptions_df.loc[prescriptions_df['hadm_id'] == hadm, 'drug'].values.tolist()
	if (len(drugs) == 0):
		hadm_to_drugs[hadm] = "None"
		n += 1
		continue
	drug_string = ""
	drugs = list(set(drugs))
	if (len(drugs) >= 5):
		drugs = random.sample(drugs, 5)
	for d in range(len(drugs)):
		if (d == len(drugs) - 1):
			drug_string += drugs[d]
		else:
			drug_string += drugs[d] + ", "
	n += 1
	hadm_to_drugs[hadm] = drug_string
icd_10_drugs = [hadm_to_drugs[hadm_id] for hadm_id in icd_10_hadm_ids]
query_df["drugs"] = icd_10_drugs

#Save filtered data
query_df.to_csv('data_filtered_medicines.csv', index=False)
