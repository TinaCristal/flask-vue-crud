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
    }
]

# Store search history
SEARCH_HISTORY = []

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
        # Get query parameters
        search = request.args.get('search', '').lower()
        read_status = request.args.get('read_status')
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Filter books
        filtered_books = BOOKS.copy()
        
        # Search by title or author
        if search:
            filtered_books = [book for book in filtered_books if 
                               search in book['title'].lower() or 
                               search in book['author'].lower()]
            
            # Add to search history
            if search not in SEARCH_HISTORY:
                SEARCH_HISTORY.insert(0, search)
                # Keep only last 10 searches
                if len(SEARCH_HISTORY) > 10:
                    SEARCH_HISTORY.pop()
        
        # Filter by read status
        if read_status is not None:
            read_status_bool = read_status.lower() == 'true'
            filtered_books = [book for book in filtered_books if book['read'] == read_status_bool]

        # Sort books
        if sort_by in ['title', 'author', 'read']:
            filtered_books.sort(key=lambda x: x[sort_by].lower() if sort_by != 'read' else x[sort_by])
            if sort_order.lower() == 'desc':
                filtered_books.reverse()

        # Pagination
        total = len(filtered_books)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_books = filtered_books[start_index:end_index]
        
        response_object['books'] = paginated_books
        response_object['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page  # Calculate total pages
        }
    return jsonify(response_object)


@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
@app.route('/books/batch', methods=['DELETE', 'PUT'])  # Add batch endpoint
@app.route('/books/batch/mark', methods=['PUT'])  # Add batch mark endpoint
@app.route('/books/search/history', methods=['GET', 'DELETE'])  # Add search history endpoint with DELETE
def book_operations(book_id=None):
    response_object = {'status': 'success'}
    
    if request.path.startswith('/books/batch'):
        # Batch operations
        post_data = request.get_json()
        book_ids = post_data.get('book_ids', [])
        
        if request.method == 'DELETE':
            # Batch delete
            deleted_count = 0
            for book_id in book_ids:
                if remove_book(book_id):
                    deleted_count += 1
            response_object['message'] = f'{deleted_count} books deleted!'
        elif request.method == 'PUT' and request.path.endswith('/mark'):
            # Batch mark as read/unread
            read_status = post_data.get('read', False)
            updated_count = 0
            for book in BOOKS:
                if book['id'] in book_ids:
                    book['read'] = read_status
                    updated_count += 1
            response_object['message'] = f'{updated_count} books marked as {"read" if read_status else "unread"}!'
    
    elif book_id:
        # Single book operations
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
    
    elif request.path.startswith('/books/search/history'):
        # Search history
        if request.method == 'GET':
            response_object['history'] = SEARCH_HISTORY
        elif request.method == 'DELETE':
            # Clear search history
            SEARCH_HISTORY.clear()
            response_object['message'] = 'Search history cleared!'
    
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
