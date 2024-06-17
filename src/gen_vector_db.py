from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy  as np 
import pandas as pd 
import requests
import faiss
import re



# Class which completely handles the creation of the VectorDB
# Uses FAISS of course
# Model to generate embeddings and chunk_size can be chosen dynamically
# Using Alibaba-NLP/gte-large-en-v1.5 to generate embeddings
# This is the best performing lightweight embedding-gen on HuggingFace
# https://huggingface.co/spaces/mteb/leaderboard



class FAISSVectorDB():
	def __init__(self, site_url, model, chunk_size):
		super().__init__()
		self.wp_site_url = site_url
		self.model_name = model
		self.posts = []
		self.chunks_list = []
		self.chunk_size = chunk_size
		self.embedding_model= SentenceTransformer(f"{model}", trust_remote_code=True)
		self.embeddings = {}

	def split_text(self, text):
	    words = text.split()
	    for i in range(0, len(words), self.chunk_size):
	        yield ' '.join(words[i:i+self.chunk_size])

	# Downloads Blog Data
	def get_blog_data(self, site_url):

		posts = []

		page = 1

		while True:
			response= requests.get(f"{site_url}/wp-json/wp/v2/posts", params={"per_page" : 100, "page" : page})
			page+=1
			if response.status_code!= 200:
				print("WP Site Blog Data has been ingested")
				break
			posts.extend(response.json())
			blog_data= [(post['id'], post['title']['rendered'], post['content']['rendered'])
						for post in posts]


			if len(response.json()) < 100:
				break
			#print(blog_data)
		print(f"No of Posts got - {len(posts)}")
		self.posts = posts

	# this is the generation of embeddings part using the selected model
	def generate_vector_spaces(self, post):
		blog_data = post['content']['rendered']
		blog_id= post['id']

		# Here we reintroduce chunking - this is because of 2 reasons
		# 1. The blog size we have is relatively large (~1000 words). 

		# 2. To answer a lot of questions smaller chunks will enable the LLM
		# 		to provide more concise answers


		if blog_id not in self.embeddings:
			chunks= self.split_text(blog_data)
			for chunk in chunks:
				self.chunks_list.append(chunk)
				self.embeddings[len(self.embeddings.keys())] = self.embedding_model.encode(re.sub('\W+', '', chunk))
		else:
			print("Blog Already has Embedding Included")
    
    # creates FAISS Vector DB indices

	def create_faiss(self):
		self.get_blog_data(self.wp_site_url)
		for post in self.posts:
			self.generate_vector_spaces(post)

		
		
		#print(list(self.embeddings.values()))
		embed_len= len(list(self.embeddings.values())[0])
		index= faiss.IndexFlatL2(embed_len)
		np_embed= np.array(list(self.embeddings.values())).astype(np.float32)
		index.add(np_embed)
			
		
		return index

		#else:
		#	print("Recheck your data")

	def save_indices(self, indices, filename= "faiss_emb_indices.index"):
		faiss.write_index(indices, filename)
		print("Indices saved")

	def load_index_db(self, filename = "faiss_emb_indices.index"):
		return faiss.read_index(filename)

	# main function that creates the db

	def init_vector_db(self):
		indices_to_create = self.create_faiss()
		print(indices_to_create)
		self.save_indices(indices_to_create)
		with open('post_ids.txt', 'w') as hist_id:
			for chunk_id in self.embeddings:
				hist_id.write(f"{chunk_id}\n")
		print("FAISS VECTOR DB HAS BEEN CREATED SUCCESSFULLY")

	# Function resp. for updating embeddings when a new post is published

	def add_to_vector_db(self, content, filename= "faiss_emb_indices.index"):

		chunks= self.split_text(content)
		for chunk in chunks:
			self.chunks_list.append(chunk)
			self.embeddings[len(self.embeddings.keys())] = self.embedding_model.encode(re.sub('\W+', '', chunk))
		
		embed_len= len(list(self.embeddings.values())[0])
		index= faiss.IndexFlatL2(embed_len)
		np_embed= np.array(list(self.embeddings.values())).astype(np.float32)
		index.add(np_embed)
		faiss.write_index(index, filename)
		


# function that retrieves similar posts

def find_simposts_in_db(db, query, k):
	query_embed= db.embedding_model.encode([query])
	index= db.load_index_db()
	distances, indices = index.search(np.array(query_embed).astype(np.float32), k)
	similar_chunks = [db.chunks_list[idx] for idx in indices[0]]
	return similar_chunks

if __name__ == "__main__":

	 # for testing purposes
	site_url = "http://wasserstoff-test-site.local:10003"
	embedding_model = "Alibaba-NLP/gte-large-en-v1.5"
	chunk_size= 256
	db = FAISSVectorDB(site_url, embedding_model, chunk_size)
	db.init_vector_db()
	similar_posts = find_simposts_in_db(db, "Which Animals were present during the late Jurassic Period?", 5)
	for post in similar_posts:
		print(post, end = "\n\n\n")
		print(post['title']['rendered'])
		print(post['content']['rendered'])
		print("\n\n")
	embeddings = generate_vector_spaces(get_blog_data("http://wasserstoff-test-site.local:10003"))

	print(embeddings)