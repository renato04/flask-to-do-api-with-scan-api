#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__, static_url_path = "")
# app.config['SERVER_NAME'] = '0.0.0.0:5000'
auth = HTTPTokenAuth(scheme='Bearer')

my_secret_token = "my-secret-token"

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@auth.verify_token
def verify_token(token):
    if token == my_secret_token:
        return my_secret_token

@auth.error_handler
def unauthorized():

    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    
@app.errorhandler(400)
def not_found(error):

    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):

    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def make_public_task(task):

    new_task = {}

    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id = task['id'], _external = True)
        else:
            new_task[field] = task[field]

    return new_task

@app.route('/')
def index():
    return "Hello, World!"


@app.route('/todo/api/v1.0/login', methods = ['POST'])
def login():
    if (request.json["user"] == "user" and request.json["password"] == "password"):
        return jsonify({"token": my_secret_token})
    else:
        abort(401)
    
@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
@auth.login_required
def get_tasks():
    return jsonify( { 'tasks': list(map(make_public_task, tasks)) } )

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['GET'])
@auth.login_required
def get_task(task_id):

    task = filter(lambda t: t['id'] == task_id, tasks)

    if len(task) == 0:
        abort(404)

    return jsonify( { 'task': make_public_task(task[0]) } )

@app.route('/todo/api/v1.0/tasks', methods = ['POST'])
@auth.login_required
def create_task():

    if not request.json or not 'title' in request.json:
        abort(400)

    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }

    tasks.append(task)

    return jsonify( { 'task': make_public_task(task) } ), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['PUT'])
@auth.login_required
def update_task(task_id):

    task = filter(lambda t: t['id'] == task_id, tasks)

    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)

    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])

    return jsonify( { 'task': make_public_task(task[0]) } )
    
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['DELETE'])
@auth.login_required
def delete_task(task_id):

    task = filter(lambda t: t['id'] == task_id, tasks)

    if len(task) == 0:
        abort(404)

    tasks.remove(task[0])

    return jsonify( { 'result': True } )
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)