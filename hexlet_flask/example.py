from flask import Flask, render_template, request 
from flask import redirect, url_for, flash, get_flashed_messages
import json


# Это callable WSGI-приложение
app = Flask(__name__)

app.secret_key = "secret_key"


@app.route('/')
def route():
    return render_template('index.html')


@app.get('/users')
def get_users():
    search_word = request.args.get('term', default=None)

    with open('users.txt', 'r') as repo:
        users = [json.loads(r) for r in repo.readlines()]

        filtered_users, search_word = user_search(users, search_word)
        messages = get_flashed_messages(with_categories=True)
        print(messages)

        return render_template(
            '/users/index.html',
            users=filtered_users,
            search=search_word,
            messages=messages
        )


@app.get('/users/<id>')
def get_user(id):
    with open('users.txt', 'r') as repo:
        users = [json.loads(r) for r in repo.readlines()]
        for user in users:
            if int(user['id']) == int(id):
                return render_template(
                '/users/show.html',
                user=user
                )
        return render_template('404.html'), 404


@app.post('/users/')
def post_user():
    with open('users.txt', 'a') as repo:
        user = request.form.to_dict()

        errors = validate(user)

        if errors:
            return render_template(
                'users/new_user.html',
            user=user,
            errors=errors
            ), 422

        user['id'] = generate_user_id('users.txt')
        repo.write(json.dumps(user))
        repo.write("\n")
        flash('User has been created', 'success')

        return redirect(url_for('get_users'), code=302)
    

@app.get('/users/new')
def create_user():
    user = {'name': '', 'email': ''}
    errors = []
    return render_template(
        'users/new_user.html',
        user=user,
        errors=errors)

@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
  return render_template("404.html")


def generate_user_id(file):
    with open(file, 'r') as repo:
        try:
            return json.loads(repo.readlines()[-1])['id'] + 1
        except IndexError:
            return 0
        
def user_search(users, search_word):
    search_word = request.args.get('term', default=None)
    if search_word is None:
        filtered_users = users
        search_word = ''
    else:
        filtered_users = [
            u for u in users if 
            (search_word.lower() in u['name'].lower() or 
             search_word.lower() in u['email'].lower())
             ]
    return filtered_users, search_word

def validate(data):
    errors = {}
    if len(data['name']) < 2:
        errors['name'] = 'Name is too short!'
    if '@' not in data['email']:
        errors['email'] = 'Invalid email format!'

    return errors 

