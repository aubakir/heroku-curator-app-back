from flask import Flask, jsonify, request, json
from flask_cors import CORS
import json



# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
 
@app.route('/')
def hello():
	return {
	    "Hackathon": "v0.1"
	}


#Check api
@app.route("/health/live", methods=["GET"])
def health_live():
    response = app.response_class(
        response=json.dumps({"status": "success"}),
        status=200,
        mimetype='application/json'
    )
    return response

#Check api
@app.route("/health/ready", methods=["GET"])
def health_ready():
    response = app.response_class(
        response=json.dumps({"status": "success"}),
        status=200,
        mimetype='application/json'
    )
    return response


#Check api
@app.route("/hackathon", methods=["GET"])
def check_asuritib():
    response = app.response_class(
        response=json.dumps({'answer':'hackathon'}),
        status=200,
        mimetype='application/json'
    )
    return response

import os
from threading import Thread


if __name__ == '__main__':
  
    app.run(host='0.0.0.0',port=3000,threaded=True)
    # app.run(host='0.0.0.0',port=3333,threaded=True)
