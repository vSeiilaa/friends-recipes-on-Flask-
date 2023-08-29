from flask import Flask, render_template, request 
from flask import redirect, url_for, flash, get_flashed_messages
import json


# Это callable WSGI-приложение
app = Flask(__name__)

app.secret_key = "secret_key"


@app.route('/')
def route():
    return render_template('index.html')


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
        for book in books:
            if int(book['id']) == int(id):
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
    if len(data['name']) < 2:
        errors['name'] = 'Name is too short!'
    if len(data['summary']) == 0:
        errors['summary'] = "Summary can't be empty!"

    return errors 

