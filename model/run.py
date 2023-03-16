#ADAPTED FROM https://github.com/stanford-crfm/helm/blob/main/demo.py 

import getpass
import numpy as np
import pandas as pd
from helm.common.authentication import Authentication
from helm.common.perspective_api_request import PerspectiveAPIRequest, PerspectiveAPIRequestResult
from helm.common.request import Request, RequestResult
from helm.common.tokenization_request import TokenizationRequest, TokenizationRequestResult
from helm.proxy.accounts import Account
from helm.proxy.services.remote_service import RemoteService

#Load data
#df = pd.read_csv('/Users/evaprakash/Downloads/cs324/data_filtered_medicines.csv')
df = pd.read_csv('remaining.csv')
results_df = pd.DataFrame()

# An example of how to use the request API.
api_key = getpass.getpass(prompt="Enter a valid API key: ")
auth = Authentication(api_key=api_key)
service = RemoteService("https://crfm-models.stanford.edu")

# Access account and show my current quotas and usages
account: Account = service.get_account(auth)
print(account.usages)

#Create few-shot prompt prefix
few_shot_prompt_prefix = "Please read the following clinical notes about a patient's illness.\n\n\"Patient complaints: chest pain\nMedicines: Acetaminophen, Sildenafil, Levothyroxine Sodium, Aspirin, Insulin\"\n\nWhat are the medical ICD-10 codes corresponding to the illness? Choose at least one of the following:\nI50\nI25\nN18\nJ44\nAnswer: J44, I50"
few_shot_prompt_prefix += "\n\nPlease read the following clinical notes about a patient's illness.\n\n\"Patient complaints: Nonhealing ulcers\nMedicines: Isosorbide Mononitrate (Extended Release), Heparin, Gabapentin, Citalopram, Metoprolol Tartrate\"\n\nWhat are the medical ICD-10 codes corresponding to the illness? Choose at least one of the following:\nI50\nI25\nN18\nJ44\nAnswer: N18, I25"

#Run model on data
results = []
hadm_ids = []
# Make a request
for index, row in df.iterrows():
	echo_prompt=True	
	prompt = few_shot_prompt_prefix + "\n\nPlease read the following clinical notes about a patient's illness.\n\n\"Patient complaints: " + row["chief_complaints"] + "\nMedicines: " + row["drugs"] + "\"\n\nWhat are the medical ICD-10 codes corresponding to the illness? Choose at least one of the following:\nI50\nI25\nN18\nJ44\nAnswer: "
	request = Request(model="openai/text-davinci-003", prompt=prompt, echo_prompt=echo_prompt, max_tokens=20)
	request_result: RequestResult = service.make_request(auth, request)
	r = request_result.completions[0].text
	results.append(r)
	np.save('running_results.npy', np.array(results))
	hadm_ids.append(row["hadm_id"])

#Save results
results_df["hadm_id"] = hadm_ids
results_df["pred"] = results
results_df.to_csv('few_shot_results_remaining.csv', index=False)
