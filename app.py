from flask import Flask, jsonify, request, json
from flask_cors import CORS
import os
from flask import send_from_directory
import DBconnect

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='favicon.png')

@app.route('/', methods=['GET'])
def hello():
	return {
	    "Hackathon": "v0.1"
	}



@app.route('/jira', methods=['POST'])
def jira():
    data = request.get_json()
    
    
    return jsonify(data)


@app.route('/authorization', methods=['POST'])
def authorization():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    return jsonify({'answer': DBconnect.checkUser(username,password)})


if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()