from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import json
import requests
import os
import RAG_gen
import gen_vector_db
import pickle

app_chatbot = Flask(__name__)

def build_cors_preflight_response():
	response = make_response()
	response.headers.add("Access-Control-Allow-Origin", "*")
	response.headers.add("Access-Control-Allow-Headers", "*")
	response.headers.add("Access-Control-Allow-Methods", "*")

	return response

def build_cors_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


try:
	with open("db_list.pkl", 'rb') as db_list_pkl:
		website_db = pickle.load(db_list_pkl)
except Exception as e:
	print(f"{e}")
	website_db = {}
	print("Initializing API")



@app_chatbot.route('/update-vector-db', methods = ["POST"])
def update_vector_db():
	
	try:
		if request.content_type != "application/json":
			return build_cors_actual_response(make_response(jsonify({"error": "Content-type must be application/json"})))

		print(request.method)
		# referer= request.headers.get("Referer")
		# if not referer:
		# 	return jsonify({"error" : "No Referer found"}), 400

		post_data = request.get_json()
		wordpress_site_url = post_data.get('site_url')
		post_title = post_data.get('post_title' , '')
		post_cont = post_data.get('post_content', '')

		combined_content = f"{post_title} {post_cont}"

		# wordpress_site_url = referer.split('/')[2]
		# wordpress_site_url = f"http://{wordpress_site_url}"

		if wordpress_site_url in website_db:
			website_db[wordpress_site_url].add_to_vector_db(combined_content)

		return jsonify({"message" : "Vector DB Update was successful - Embeddings Created & Added"}), 200		

	except Exception as e:
		return jsonify({"message": f"Error - Vector DB update was unsuccessful - {e}"}), 500




@app_chatbot.route('/chatbot' , methods = ['POST', 'OPTIONS'])
def chatbot():
	if request.method == "OPTIONS" : 
		print(request.method)
		return build_cors_preflight_response()
	elif request.method == "POST":
	
		if request.content_type != "application/json":
			
			return build_cors_actual_response(make_response(jsonify({"error": "Content-type must be application/json"})))

		print(request.method)


		wordpress_site = json.loads(request.get_json())['wordpress_link']
		query = json.loads(request.get_json())['query']
		if wordpress_site not in website_db:
			embedding_model = "Alibaba-NLP/gte-large-en-v1.5"
			chunk_size= 256

			print("New Website Detected - Creating Embeddings")
			db = gen_vector_db.FAISSVectorDB(wordpress_site, embedding_model, chunk_size)
			db.init_vector_db()
			website_db[wordpress_site] = db
			with open("db_list.pkl" , 'wb') as db_list_pkl_save:
				pickle.dump(website_db, db_list_pkl_save)

		db_to_get= website_db[wordpress_site]
		
		if query != "":
			similar_posts = gen_vector_db.find_simposts_in_db(db_to_get, query, 10)
			response = RAG_gen.generate_rag_response(db_to_get, query, similar_posts)

			json_resp = json.dumps({"chatbot_response" : response})

			return json_resp
		else:
			json_resp = json.dumps({"chatbot_response" : "Please check your query. It is not what I expected!"})
			return json_resp


if __name__ == "__main__":
	from waitress import serve
	serve(app_chatbot, host= 'localhost', port = 5001)