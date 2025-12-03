import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS


BOOKS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': '1984',
        'author': 'George Orwell',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Hobbit',
        'author': 'J.R.R. Tolkien',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Lord of the Rings',
        'author': 'J.R.R. Tolkien',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Catcher in the Rye',
        'author': 'J.D. Salinger',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Da Vinci Code',
        'author': 'Dan Brown',
        'read': True
    }
]

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


def remove_book(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            BOOKS.remove(book)
            return True
    return False


def find_book(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            return book
    return None


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book added!'
    else:
        # Get query parameters for filtering, sorting, and pagination
        title = request.args.get('title', '').lower()
        author = request.args.get('author', '').lower()
        read = request.args.get('read')
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Filter books
        filtered_books = BOOKS
        if title:
            filtered_books = [book for book in filtered_books if title in book['title'].lower()]
        if author:
            filtered_books = [book for book in filtered_books if author in book['author'].lower()]
        if read is not None:
            filtered_books = [book for book in filtered_books if str(book['read']).lower() == read.lower()]

        # Sort books
        if sort_by in ['title', 'author', 'read']:
            reverse = sort_order == 'desc'
            filtered_books.sort(key=lambda x: x[sort_by], reverse=reverse)

        # Paginate books
        total_books = len(filtered_books)
        total_pages = (total_books + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_books = filtered_books[start:end]

        response_object['books'] = paginated_books
        response_object['total_books'] = total_books
        response_object['total_pages'] = total_pages
        response_object['current_page'] = page
        response_object['per_page'] = per_page

    return jsonify(response_object)


@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)


@app.route('/books/batch', methods=['POST'])
def batch_books():
    response_object = {'status': 'success'}
    post_data = request.get_json()
    book_ids = post_data.get('book_ids', [])
    action = post_data.get('action')

    if not book_ids or not action:
        response_object['status'] = 'error'
        response_object['message'] = 'Missing book_ids or action'
        return jsonify(response_object), 400

    if action == 'delete':
        deleted_count = 0
        for book_id in book_ids:
            if remove_book(book_id):
                deleted_count += 1
        response_object['message'] = f'Deleted {deleted_count} books'
    elif action == 'mark_read':
        updated_count = 0
        for book_id in book_ids:
            book = find_book(book_id)
            if book and not book['read']:
                book['read'] = True
                updated_count += 1
        response_object['message'] = f'Marked {updated_count} books as read'
    elif action == 'mark_unread':
        updated_count = 0
        for book_id in book_ids:
            book = find_book(book_id)
            if book and book['read']:
                book['read'] = False
                updated_count += 1
        response_object['message'] = f'Marked {updated_count} books as unread'
    else:
        response_object['status'] = 'error'
        response_object['message'] = 'Invalid action'
        return jsonify(response_object), 400

    return jsonify(response_object)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
