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
	    "Hackathon": "v1.4.4"
	}


#Принмает данные о новым созданной задачи назначает время аналитики
@app.route('/jira/create/task', methods=['POST'])
def createTask():

    if(request.get_json()):
        data = str(request.get_json())
        data = data.replace('\'','\"')
        data = data.replace(': None',': \"None\"')
        data = data.replace(': True',': \"True\"')
        data = data.replace(': False',': \"False\"')

        
        print('-------------------------------CREATE TASK----------------------------------------')
        print(data)
        DBconnect.insertNewTask(data)
        print('-------------------------------END CREATE TASK----------------------------------------')

        return jsonify({'answer':'success'})

    return jsonify({'answer':'failed'})



#Принмает данные аналитика идет выборка разработчика
@app.route('/jira/update/task', methods=['POST'])
def updateTask():

    if(request.get_json()):
        data = str(request.get_json())
        data = data.replace('\'','\"')
        data = data.replace(': None',': \"None\"')
        data = data.replace(': True',': \"True\"')
        data = data.replace(': False',': \"False\"')

        
        print('-------------------------------UPDATE TASK----------------------------------------')
        print(data)
        DBconnect.updateTaskDevelop(data)
        print('-------------------------------END UPDATE TASK----------------------------------------')

        return jsonify({'answer':'success'})

    return jsonify({'answer':'failed'})



@app.route('/jira/update/sprint', methods=['POST'])
def updateSprint():
    data = request.get_json()
    print(data)

    return jsonify(data)


#Front authorization
@app.route('/authorization', methods=['POST'])
def authorization():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    return jsonify({'answer': DBconnect.checkUser(username,password)})


import execute

#Check rating
@app.route('/rating', methods=['POST'])
def rating():
    return jsonify(execute.sumRating())
    
if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()