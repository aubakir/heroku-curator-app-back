from flask import Flask, jsonify, request, json
from flask_cors import CORS
import os
from flask import send_from_directory


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/favicon.png')

@app.route('/')
def hello():
	return {
	    "Hackathon": "v0.1"
	}



if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()