from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers import RagTokenizer, RagSequenceForGeneration, RagRetriever
from src.gen_vector_db import FAISSVectorDB, find_simposts_in_db
from torch import cuda
import torch
import requests



# Retrieving Similar posts and then prompting the LLM
# Please Note that this function does COT and RAG together
# There is a new method of combining RAG and COT - Retrieval Augmented Thoughts (RAT)
# https://medium.com/@bijit211987/rag-chain-of-thought-retrieval-augmented-thoughts-rat-3d3489517bf0

# In RAT a Zero Shot COT is the first step and the RAG based Context is used
# to improve the Step-by-Step process rather than just using RAG based Context
# to change the final answer.

# RAT also gives the opportunity to the LLM to decide what extent of RAG Context
# it should be inflluenced by.

def generate_rag_response(db, query, sim_posts):

	#sim_posts = find_simposts_in_db(db, query, 10)
	context = ' '.join(f"{post}\n\n" for post in sim_posts)

	# ZERO SHOT COT

	initial_prompt = f'''[INST] 
					Try to answer this question/instruction with step-by-step thoughts 
					and make the answer structural. Respond to the instruction directly. DO NOT add
					any additional explanations and introducements in the answer. 

					[Question] - {query}

					Explain your Reasoning Step-by-Step on why you came to the conclusion. 
					
					[/INST]
	'''


	zero_COT_prompt = {
	"inputs": f"{initial_prompt}",
	"parameters" : {
		"max_new_tokens" : 250, 
		"temperature" : 0.2

	}
	}

	print(initial_prompt)

	API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
	headers = {"Authorization": "Bearer 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"}

	response_COT = requests.post(API_URL, headers=headers, json=zero_COT_prompt)

	zero_COT_ans= response_COT.json()[0]['generated_text'].split("[/INST]")[1]

	print(zero_COT_ans)

	# GIVING ZERO SHOT COT OUTPUT AND ADDING RAG BASED CONTEXT

	prompt_template = f'''[INST] 
					Try to answer this question/instruction with step-by-step thoughts 
					and make the answer structural. Respond to the instruction directly. DO NOT add
					any additional explanations and introducements in the answer. 

					[Question] - {query}

					Explain your Reasoning Step-by-Step on why you came to the conclusion. 
					
					[/INST]

					ANSWER- {zero_COT_ans}

					[INST]

					I want to check if your answer is correct. Here is some additional context for you.

					[CONTEXT] - {context}

					You need to check if your answer is correct and if you find some errors or ignorance of
					necessary details you need to modify your answer. If you think the context does not add
					anything - output the original answer. Give a step by step explanation.
					[/INST]

				'''



	auth_token = "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"

	prompt = {
	"inputs": f"{prompt_template}",
	"parameters" : {
		"max_new_tokens" : 1000, 
		"temperature" : 0.2

	}
	}

	print(prompt_template)

	response = requests.post(API_URL, headers=headers, json=prompt)
	
	return response.json()[0]['generated_text'].split("[/INST]")[2]
	

	#print(prompt_template)



if __name__ == "__main__":

	
	# for test purposes

	site_url = "http://wasserstoff-test-site.local:10003"
	embedding_model = "Alibaba-NLP/gte-large-en-v1.5"
	db = FAISSVectorDB(site_url, embedding_model, 128)
	db.init_vector_db()

	#loads the db - for test purposes

	index= db.load_index_db()
	embedding_list = list(db.embeddings.values())

	query= "Name some birds found in the Himalayas in India?"
	print(generate_rag_response(db,query))