import requests
from bs4 import BeautifulSoup as bs
import base64
from collections import Counter
import random

# This .py file aims to create a WordPress Blog which will
# help us in creating a RAG based ChatBot. 
# It will ccreate a corpus of documents.

# Load the text file (assuming it's saved locally)
for corpus in os.listdir("./corpus/"):
	with open(f'{corpus}', 'r', encoding='utf-8') as file:
		text = file.read()

	# Split the text into chunks
	# The Chunks will have a random length - to mimic real world examples
	def split_text(text):
		chunk_size= int(random.random()*100)+ 1000
		words = text.split(' ')
		for i in range(0, len(words), chunk_size):
			yield ' '.join(words[i:i+chunk_size])

	# WordPress site and authentication details
	# This is the Local site running
	site_url = 'http://wasserstoff-test-site.local:10003'
	username = 'wasserstoff'
	password = 'JPOe kBFT KQQZ MPrg 89Yi A9jR'

	# Generate Basic Auth token
	token = base64.b64encode(f'{username}:{password}'.encode())
	headers = {
		'Authorization': f'Basic {token.decode("utf-8")}',
		'Content-Type': 'application/json'
	}

	# Post chunks as individual posts
	# For Title of the Post we have the following methodology - 
	# Title  =  Guttenberg Post - {Post Number} - {15 most common words in post}

	header_num= 0
	for chunk in split_text(text):
		word_counter= Counter(chunk.split(" "))
		common15 = word_counter.most_common(15)
		
		header_str = ""
		for word, count in common15:
			header_str+= f"{word} "

		
		post = {
			'title': f'Guttenberg post {header_num} - {header_str}',
			'content': chunk,
			'status': 'publish'
		}
		header_num += 1
		response = requests.post(f'{site_url}/wp-json/wp/v2/posts', headers=headers, json=post)
		print(response.json())
		#print(f"Created post: {response.json()['title']}")