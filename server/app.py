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
        # 处理查询参数
        search = request.args.get('search', '').lower()
        read_status = request.args.get('read', '')
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # 过滤图书
        filtered_books = BOOKS.copy()
        
        # 搜索过滤（书名或作者）
        if search:
            filtered_books = [book for book in filtered_books 
                            if search in book['title'].lower() or search in book['author'].lower()]
        
        # 阅读状态过滤
        if read_status:
            read_bool = read_status.lower() == 'true'
            filtered_books = [book for book in filtered_books if book['read'] == read_bool]
        
        # 排序
        try:
            filtered_books.sort(key=lambda x: x[sort_by], reverse=sort_order.lower() == 'desc')
        except KeyError:
            # 如果排序字段不存在，默认按标题排序
            filtered_books.sort(key=lambda x: x['title'], reverse=sort_order.lower() == 'desc')
        
        # 分页
        total = len(filtered_books)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_books = filtered_books[start:end]
        
        # 构建响应
        response_object['books'] = paginated_books
        response_object['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page  # 计算总页数
        }
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


@app.route('/books/batch', methods=['PUT', 'DELETE'])
def batch_books():
    response_object = {'status': 'success'}
    post_data = request.get_json()
    book_ids = post_data.get('book_ids', [])
    
    if not book_ids:
        response_object['status'] = 'error'
        response_object['message'] = 'No book IDs provided'
        return jsonify(response_object), 400
    
    if request.method == 'DELETE':
        # 批量删除图书
        deleted_count = 0
        for book_id in book_ids:
            if remove_book(book_id):
                deleted_count += 1
        response_object['message'] = f'Deleted {deleted_count} out of {len(book_ids)} books'
    
    if request.method == 'PUT':
        # 批量更新阅读状态
        read_status = post_data.get('read')
        if read_status is None:
            response_object['status'] = 'error'
            response_object['message'] = 'No read status provided'
            return jsonify(response_object), 400
        
        updated_count = 0
        for book in BOOKS:
            if book['id'] in book_ids:
                book['read'] = read_status
                updated_count += 1
        response_object['message'] = f'Updated {updated_count} out of {len(book_ids)} books'
    
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
