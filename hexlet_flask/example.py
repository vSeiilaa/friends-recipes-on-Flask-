from flask import Flask, render_template, request, redirect, url_for
import json


# Это callable WSGI-приложение
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello again from Flask!'


@app.get('/users')
def users_index():
    with open('users.txt', 'r') as repo:
        users = [json.loads(r) for r in repo.readlines()]

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

        return render_template(
            '/users/index.html',
            users=filtered_users,
            search=search_word
        )


@app.get('/users/<id>')
def user_html(id):
    return render_template(
        '/users/show.html',
        name=id,
    )


@app.post('/users/')
def user_post():
    with open('users.txt', 'a') as repo:
        user = request.form.to_dict()
        user['id'] = user_id('users.txt')
        repo.write(json.dumps(user))
        repo.write("\n")
        return redirect(url_for('users_index'), code=302)
    

@app.get('/users/new')
def users_new():
    new_user = {'name': '', 'email': ''}

    return render_template(
        'users/new_user.html',
        user=new_user)

def user_id(file):
    with open(file, 'r') as repo:
        try:
            return json.loads(repo.readlines()[-1])['id'] + 1
        except IndexError:
            return 0