from flask import Flask
from flask import render_template


# Это callable WSGI-приложение
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello again from Flask!'

@app.get('/users')
def users_get():
    return 'GET /users'


@app.post('/users')
def users():
    return 'Users', 302


@app.route('/users/<id>')
def users_html(id):
    return render_template(
        '/users/show.html',
        name=id,
    )

@app.route('/courses/<id>')
def courses(id):
    return f'Course id: {id}'

