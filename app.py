from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for

import json
import os
import time


app = Flask(__name__)


todo_db_file = 'todo.txt'
todo_list = []


def todo_load():
    with open(todo_db_file, 'r') as f:
        content = f.read()
        return json.loads(content)


def todo_save():
    with open(todo_db_file, 'w') as f:
        s = json.dumps(todo_list)
        f.write(s)


def todo_add(task):
    todo_id = 0
    if len(todo_list) > 0:
        t = todo_list[-1]
        todo_id = t['id'] + 1
    todo = {
        'id': todo_id,
        'task': task,
        'timestamp': time.time(),
    }
    todo_list.append(todo)


def todo_delete(todo_id):
    todo_id = int(todo_id)
    for i, t in enumerate(todo_list):
        if t['id'] == todo_id:
            del todo_list[i]
            return True
    return False


def todo_init_db():
    # create empty JSON list at first time
    path = todo_db_file
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('[]')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/todo/list')
def todos():
    todos = todo_load()
    return json.dumps(todos, indent=2)


@app.route('/todo/add', methods=['POST'])
def add():
    t = request.form['todo']
    todo_add(t)
    todo_save()
    return redirect(url_for('index'))


@app.route('/todo/delete/<todo_id>/')
def delete(todo_id):
    todo_delete(todo_id)
    todo_save()
    return redirect(url_for('index'))


if __name__ == '__main__':
    todo_init_db()
    app.run(debug=True)
