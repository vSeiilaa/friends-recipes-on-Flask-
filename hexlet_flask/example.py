from flask import Flask, render_template, request, session 
from flask import redirect, url_for, flash, get_flashed_messages
import json
from hashlib import sha256
import os


# Это callable WSGI-приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret'


@app.route('/')
def route():
    messages = get_flashed_messages(with_categories=True)
    current_user = session.get('user')
    return render_template(
        'index.html',
        messages=messages,
        current_user=current_user,
        )


@app.get('/books')
def books_get():
    search_word = request.args.get('term', default=None)

    with open('books.txt', 'r') as repo:
        books = [json.loads(r) for r in repo.readlines()]

        filtered_books, search_word = search(books, search_word)
        messages = get_flashed_messages(with_categories=True)
        print(messages)

        return render_template(
            '/books/index.html',
            books=filtered_books,
            search=search_word,
            messages=messages
        )


@app.get('/books/<id>')
def book_get(id):
    with open('books.txt', 'r') as repo:
        books = [json.loads(r) for r in repo.readlines()]
        book = find(id, books)
        if book:
            return render_template(
                '/books/show.html',
                book=book
                )
        return render_template('404.html'), 404


@app.post('/books/')
def book_post():
    with open('books.txt', 'a') as repo:
        book = request.form.to_dict()

        errors = validate(book)

        if errors:
            return render_template(
                'books/new_book.html',
            book=book,
            errors=errors
            ), 422

        book['id'] = generate_id('books.txt') # type: ignore
        repo.write(json.dumps(book))
        repo.write("\n")
        flash('Book has been added', 'success')

        return redirect(url_for('books_get'), code=302)
    

@app.get('/books/new')
def book_create():
    book = {'name': '', 'summary': ''}
    errors = []
    return render_template(
        'books/new_book.html',
        book=book,
        errors=errors)


@app.get('/books/<id>/edit')
def book_edit(id):
    with open('books.txt', 'r') as repo:
        books = [json.loads(r) for r in repo.readlines()]
        errors = []
        book = find(id, books)
        if book:
            return render_template(
                '/books/edit.html',
                book=book,
                errors=errors
                )
        return render_template('404.html'), 404


@app.post('/books/<id>/patch')
def book_patch(id):
    data = request.form.to_dict()
    errors = validate(data)

    if errors:
        with open('books.txt', 'r') as repo:
            books = [json.loads(r) for r in repo.readlines()]
            book = find(id, books)

            return render_template(
                'schools/edit.html',
                book=book,
                errors=errors,
                ), 422
        

    replace_line('books.txt', id, data)

    flash('Book has been successfully updated!', 'success')

    return redirect(url_for('books_get'))


@app.post('/books/<id>/delete')
def book_delete(id):

    with open('books.txt', 'r') as old, open('books.txt', 'w') as new:
        lines = old.readlines()
        new.writelines(lines[0:int(id)])
        new.writelines(lines[int(id)+1:])

        flash('Book has been deleted', 'success')
        return redirect(url_for('books_get'))


@app.post('/session/new')
def new_session():
    data = request.form.to_dict()
    with open('users.txt', 'r') as repo:
        users = [json.loads(r) for r in repo.readlines()]
        user = get_user(data, users)

        if user:
            session['user'] = user
            return redirect(url_for('route'))
        else:
            flash('Wrong password or name.')
            return redirect(url_for('route'))


@app.route('/session/delete', methods=['DELETE', 'POST'])
def delete_session():
    session.clear()
    return redirect(url_for('route'))


@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


def generate_id(file):
    with open(file, 'r') as repo:
        try:
            return json.loads(repo.readlines()[-1])['id'] + 1
        except IndexError:
            return 0
        

def search(data, search_word):
    search_word = request.args.get('term', default=None)
    if search_word is None:
        filtered_data = data
        search_word = ''
    else:
        filtered_data = [
            u for u in data if 
            (search_word.lower() in u['name'].lower() or 
             search_word.lower() in u['summary'].lower())
             ]
    return filtered_data, search_word


def validate(data):
    errors = {}
    print(data)
    if len(data['name']) < 2:
        errors['name'] = 'Name is too short!'
    if len(data['summary']) == 0:
        errors['summary'] = "Summary can't be empty!"

    return errors 

def find(id, data):
    for d in data:
        if int(d['id']) == int(id):
            return d
    return False

def replace_line(file, id, new_content):
    # temporary function for editing the content in txt file by 
    # overwriting the entire file.
    # To be replaced with the proper database
    id = int(id)
    new_content['id'] = id
    
    repo = open(file, 'r').readlines()

    repo[id] = json.dumps(new_content)
    out = open(file, 'w')
    out.writelines(repo)
    out.close()


def get_user(form_data, repo):
    name = form_data['name']
    password = sha256(form_data['password'].encode()).hexdigest()
    for user in repo:
        if user['name'] == name and user['password'] == password:
            return user