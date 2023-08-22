from flask import Flask
from flask import render_template, request

users = ['mike', 'mishel', 'adel', 'keks', 'kamila']

# Это callable WSGI-приложение
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello again from Flask!'


@app.route('/users')
def users_index():

    term = request.args.get('term', default=None)
    if term is None:
        filtered_users = users
        term = ''
    else:
        filtered_users = [u for u in users if term in u]

    return render_template(
        '/users/index.html',
        users=filtered_users,
        search=term
    )


@app.route('/users/<id>')
def users_html(id):
    return render_template(
        '/users/show.html',
        name=id,
    )


@app.route('/courses/<id>')
def courses(id):
    return f'Course id: {id}'

