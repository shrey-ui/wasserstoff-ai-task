from sentence_transformers import SentenceTransformer
import numpy  as np 
import pandas as pd 
import requests
import faiss


# Here it is best if we use a Pre-trained Model
# which is pretrained and specializes in Semantic Search
# as that is the basis of RAG



class FAISSVectorDB():
	def __init__(self, site_url, model):
		super().__init__()
		self.wp_site_url = site_url
		self.model_name = model
		self.posts = []
		self.embedding_model= SentenceTransformer(f"sentence-transformers/{model}")
		self.embeddings = {}


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
		self.posts = posts

	# this is the generation of embeddings part using the selected model
	def generate_vector_spaces(self, post):
		blog_data = post['content']['rendered']
		blog_id= post['id']
		if blog_id not in self.embeddings:
			self.embeddings[blog_id] = self.embedding_model.encode(blog_data, convert_to_tensor= True)
		else:
			print("Blog Already has Embedding Included")


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

	def init_vector_db(self):
		indices_to_create = self.create_faiss()
		print(indices_to_create)
		self.save_indices(indices_to_create)
		with open('post_ids.txt', 'w') as hist_id:
			for post_id in self.embeddings:
				hist_id.write(f"{post_id}\n")
		print("FAISS VECTOR DB HAS BEEN CREATED SUCCESSFULLY")

def find_simposts_in_db(db, query, k):
	query_embed= db.embedding_model.encode([query])
	index= db.load_index_db()
	distances, indices = index.search(np.array(query_embed).astype(np.float32), k)
	similar_posts = [db.posts[idx] for idx in indices[0]]
	return similar_posts

if __name__ == "__main__":
	site_url = "http://wasserstoff-test-site.local:10003"
	embedding_model = "multi-qa-MiniLM-L6-dot-v1"
	db = FAISSVectorDB(site_url, embedding_model)
	db.init_vector_db()
	similar_posts = find_simposts_in_db(db, "Which Animals were present during the late Jurassic Period?", 3)
	for post in similar_posts:
		print(post['title']['rendered'])
		print(post['content']['rendered'])
		print("\n\n")
#embeddings = generate_vector_spaces(get_blog_data("http://wasserstoff-test-site.local:10003"))

#print(embeddings)