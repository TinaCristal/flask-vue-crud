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
        'title': 'Animal Farm',
        'author': 'George Orwell',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Catcher in the Rye',
        'author': 'J. D. Salinger',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Brave New World',
        'author': 'Aldous Huxley',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Lord of the Rings',
        'author': 'J. R. R. Tolkien',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'The Hobbit',
        'author': 'J. R. R. Tolkien',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'read': False
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
        # 处理搜索、分页、排序参数
        query = request.args.get('query', '')
        read_status = request.args.get('read')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        sort_by_fields = request.args.getlist('sort_by') or ['title']
        sort_orders = request.args.getlist('sort_order') or ['asc']

        # 过滤图书
        filtered_books = BOOKS
        if query:
            query = query.lower()
            filtered_books = [book for book in filtered_books 
                             if query in book['title'].lower() or query in book['author'].lower()]
        
        if read_status is not None:
            read_status = read_status.lower() == 'true'
            filtered_books = [book for book in filtered_books if book['read'] == read_status]

        # 排序图书 - 支持多列组合排序
        valid_sort_fields = ['title', 'author', 'read']
        # 只保留有效的排序字段
        valid_sort_fields_with_orders = []
        for i, field in enumerate(sort_by_fields):
            if field in valid_sort_fields:
                # 对应排序顺序，如果没有则使用默认asc
                order = sort_orders[i] if i < len(sort_orders) else 'asc'
                valid_sort_fields_with_orders.append((field, order))
        
        if valid_sort_fields_with_orders:
            # 按多个字段排序，先按第一个字段，再按第二个，以此类推
            filtered_books.sort(key=lambda x: tuple(x[field] for field, _ in valid_sort_fields_with_orders),
                               reverse=valid_sort_fields_with_orders[0][1] == 'desc')

        # 分页处理
        total = len(filtered_books)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_books = filtered_books[start:end]

        response_object['books'] = paginated_books
        response_object['total'] = total
        response_object['page'] = page
        response_object['per_page'] = per_page
        response_object['total_pages'] = (total + per_page - 1) // per_page
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
        return jsonify(response_object)
    
    # 执行批量操作
    if action == 'delete':
        for book_id in book_ids:
            remove_book(book_id)
        response_object['message'] = f'Deleted {len(book_ids)} books'
    elif action == 'mark_as_read':
        for book_id in book_ids:
            book = find_book(book_id)
            if book:
                book['read'] = True
        response_object['message'] = f'Marked {len(book_ids)} books as read'
    elif action == 'mark_as_unread':
        for book_id in book_ids:
            book = find_book(book_id)
            if book:
                book['read'] = False
        response_object['message'] = f'Marked {len(book_ids)} books as unread'
    else:
        response_object['status'] = 'error'
        response_object['message'] = 'Invalid action'
    
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
