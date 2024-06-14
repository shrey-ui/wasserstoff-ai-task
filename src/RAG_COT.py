from sentence_transformers import SentenceTransformer
import numpy  as np 
import pandas as pd 
import requests


# Here it is best if we use a Pre-trained Model
# which is pretrained and specializes in Semantic Search
# as that is the basis of RAG

def get_blog_data(site_url):
	response= requests.get(f"{site_url}/wp-json/wp/v2/posts")
	posts = response.json()

	blog_data= [(post['id'], post['title']['rendered'], post['content']['rendered'])
	 			for post in posts]
	print(blog_data)
	return blog_data

model= SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-dot-v1")

# this is the generation of embeddings part using the selected model


def generate_vector_spaces(blog_content):
	blog_data = [data[2] for data in blog_content]
	embeddings= model.encode(blog_data, convert_to_tensor= True)
	print(embeddings.shape)
	return embeddings

embeddings = generate_vector_spaces(get_blog_data("http://wasserstoff-test-site.local:10003"))

#print(embeddings)