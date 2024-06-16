import requests
import json

if __name__ == "__main__" : 
	to_send= {"wordpress_link" : "http://wasserstoff-test-site.local:10003" , 
			  "query" : "What are some planets that are easily visible in the night sky?"
			  }

	print(json.dumps(to_send))
	response = requests.post("http://localhost:5001/chatbot", json = json.dumps(to_send))

	print(response.text)