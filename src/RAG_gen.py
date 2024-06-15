from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers import RagTokenizer, RagSequenceForGeneration, RagRetriever
from RAG_COT import FAISSVectorDB, find_simposts_in_db
from torch import cuda
import torch
import requests



device= f"cuda:{cuda.current_device()}" if cuda.is_available() else "cpu"

site_url = "http://wasserstoff-test-site.local:10003"
embedding_model = "Alibaba-NLP/gte-large-en-v1.5"
db = FAISSVectorDB(site_url, embedding_model, 128)
db.init_vector_db()

#loads the db - for test purposes

index= db.load_index_db()
embedding_list = list(db.embeddings.values())

# Retrieving Similar posts and then prompting the LLM

def generate_rag_response(query):

	sim_posts = find_simposts_in_db(db, query, 5)
	context = ' '.join(f"{post}\n\n" for post in sim_posts)

	prompt_template = f'''[INST] 
					  You are going to provide answers to certain questions in a concise manner. To help answer
					  these questions you will be provided with a context. You will ONLY use this context to provide
					  the answers. Please don't provide any hint at all that you are using this context for your answer.

					[Question] - {query}

					[Context] - {context}
					
					[/INST]
				'''

	quantization_config = BitsAndBytesConfig(
				load_in_4bit= True, 
				bnb_4bit_quant_type= "nf4",
				bnb_4bit_compute_dtype = "float16"

		)

	auth_token = "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"

	prompt = {
	"inputs": f"{prompt_template}",
	}

	print(prompt_template)

	API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
	headers = {"Authorization": "Bearer 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"}

	response = requests.post(API_URL, headers=headers, json=prompt)
	#print(response.json())
	return response.json()[0]['generated_text'].split("[/INST]")[1]
	

	#print(prompt_template)



query= "Can you name some really big Dinosaurs?"
print(generate_rag_response(query))