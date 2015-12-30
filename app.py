from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import make_response
from flask import session

import todo
from todo import Todo,User,db


app = Flask(__name__)
DATABASE = 'todos.db'
SECRET_KEY = 'todo'

app.config.from_object(__name__)


@app.route('/')
def index():
    # user_id = request.cookies.get('user_id')
    user_id = session.get('user_id')
    # if session may not sign out
    todos = None
    if user_id:
        todos = Todo.query.filter(Todo.user_id == int(user_id),Todo.complete == False).all()
        print todos
    return render_template('index.html', user_id = user_id, todos = todos)


@app.route('/sign',methods=['POST', 'GET'])
def sign():
    if request.method == 'POST':
        userdata = request.form.to_dict()
        if len(userdata['username']) < 3:
            flash("the length of username should be more than 2 bytes.please rename.")
        elif userdata['password'] != userdata['password']:
            flash(" Your password are different,please input again. ")
        else:
            # since all the conditions are suitable,we can create a new user now.
            #newUser = User(username=userdata['username'],password=userdata['password'],email=userdata['email'])
            del userdata['password1']
            newUser = User(**userdata)
            todo.db.session.add(newUser)
            try:
                todo.db.session.commit()
            except:
                flash("This username is existed, please rename...")
                todo.db.session.rollback()

            flash("you have sign in the TODO , now we will jump to your home page...")
            response = make_response(redirect(url_for('index')))
            response.set_cookie('user_id', str(newUser.id))
            session['user_id'] = newUser.id
            print session
            return response
    return render_template('sign.html')


@app.route('/logout', methods=['POST','GET'])
def logout():
    response = make_response(redirect(url_for('index')))
    # response.set_cookie('sessionID','',expires=0)
    response.delete_cookie('user_id')
    session.__delitem__('user_id')
    # print request.cookies
    print session
    flash('you have logged out')
    return response


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='POST':
        user_data = request.form.to_dict()
        print user_data
        # query={'username': user_data.get('username')}
        print user_data.get('username')
        # user=User.query.filter(**query).first()
        # filter() got an unexpected keyword argument 'username'
        # TypeError:filter() got an unexpected keyword argument 'username'

        user =User.query.filter(User.username == user_data['username']).first())
        # if all(), it will throw AttributeError: 'BaseQuery' object has no attribute 'password'
        if user:
            if user.password == user_data['password']:
                flash('log in successful.')
                reponse = make_response(redirect(url_for('index')))
                reponse.set_cookie('user_id', str(user.id))

                session['user_id'] = user.id
                print "session:", session
                # print "session.SessionID ",session.SessionID
                return reponse
         else:
            flash('the user is not exist. ')
    return render_template('login.html')


@app.route('/add/', methods=['POST'])
def add():
    user_id = session.get('user_id')
    # user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    else:
        t = request.form['todo']
        # use unicode(), not str(), for Chinese chars
        newTodo = todo.Todo(task=unicode(t),user_id=int(user_id))
        todo.db.session.add(newTodo)
        todo.db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<todo_id>/')
def delete(todo_id):
    # user_id = request.cookies.get('user_id')
    user_id = session.get('user_id')
    t = todo.Todo.query.get(int(todo_id))
    if t.user_id == int(user_id):
        # todo.db.session.delete(t)
        t.complete = True
        flash('Congratulations, you have finish this task and now you can check it. ')
        todo.db.session.commit()
    else:
        flash("sorry,you can't delete others' task...")
    return redirect(url_for(index))


@app.route('/check')
def check():
    # user_id = request.cookies.get('user_id')
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    else:
        user = User.query.get(int(user_id))
        todos = Todo.query.filter(Todo.user_id == int(user_id),Todo.complete == True).all()
        return render_template('check.html',todos=todos, username=user.username)

if __name__ == '__main__':
    app.run(debug=True)
