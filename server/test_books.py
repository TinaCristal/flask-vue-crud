import pytest
import json
from app import app, BOOKS, remove_book, find_book
import uuid

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_ping(client):
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.data.decode('utf-8').strip() == '"pong!"'

def test_get_all_books(client):
    response = client.get('/books')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'success'
    assert 'books' in data
    assert 'total' in data
    assert 'page' in data
    assert 'per_page' in data
    assert 'total_pages' in data

def test_search_books(client):
    # 测试按书名搜索
    response = client.get('/books?query=Gatsby')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data['books']) >= 1
    assert any('Great Gatsby' in book['title'] for book in data['books'])
    
    # 测试按作者搜索
    response = client.get('/books?query=Orwell')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data['books']) >= 2  # 1984 和 Animal Farm
    
    # 测试搜索不存在的内容
    response = client.get('/books?query=nonexistentbook')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data['books']) == 0

def test_filter_by_read_status(client):
    # 测试已读
    response = client.get('/books?read=true')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert all(book['read'] == True for book in data['books'])
    
    # 测试未读
    response = client.get('/books?read=false')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert all(book['read'] == False for book in data['books'])

def test_pagination(client):
    # 测试第一页
    response = client.get('/books?page=1&per_page=5')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['page'] == 1
    assert len(data['books']) <= 5
    
    # 测试第二页
    response = client.get('/books?page=2&per_page=5')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['page'] == 2

def test_sorting(client):
    # 测试按书名字母顺序升序
    response = client.get('/books?sort_by=title&sort_order=asc')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    titles = [book['title'] for book in data['books']]
    assert titles == sorted(titles)
    
    # 测试按书名字母顺序降序
    response = client.get('/books?sort_by=title&sort_order=desc')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    titles = [book['title'] for book in data['books']]
    assert titles == sorted(titles, reverse=True)
    
    # 测试按作者排序
    response = client.get('/books?sort_by=author&sort_order=asc')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    authors = [book['author'] for book in data['books']]
    assert authors == sorted(authors)
    
    # 测试按阅读状态排序
    response = client.get('/books?sort_by=read&sort_order=asc')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    # 未读在前，已读在后
    read_status = [book['read'] for book in data['books']]
    assert not any(read_status[i] > read_status[i+1] for i in range(len(read_status)-1))

def test_batch_operations(client):
    # 添加几本书用于测试批量操作
    test_books = [
        {"title": "Test Book 1", "author": "Test Author 1", "read": False},
        {"title": "Test Book 2", "author": "Test Author 2", "read": False},
        {"title": "Test Book 3", "author": "Test Author 3", "read": False}
    ]
    
    book_ids = []
    for book in test_books:
        response = client.post('/books', json=book)
        assert response.status_code == 200
        # 获取新添加的书籍ID
        response = client.get(f'/books?query={book["title"]}')
        data = json.loads(response.data.decode('utf-8'))
        for b in data['books']:
            if b['title'] == book['title'] and b['author'] == book['author']:
                book_ids.append(b['id'])
                break
    
    # 测试批量标记为已读
    response = client.post('/books/batch', json={"book_ids": book_ids, "action": "mark_as_read"})
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'success'
    
    # 验证标记结果
    for book_id in book_ids:
        response = client.get('/books')
        data = json.loads(response.data.decode('utf-8'))
        book = next(b for b in data['books'] if b['id'] == book_id)
        assert book['read'] == True
    
    # 测试批量标记为未读
    response = client.post('/books/batch', json={"book_ids": book_ids, "action": "mark_as_unread"})
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'success'
    
    # 验证标记结果
    for book_id in book_ids:
        response = client.get('/books')
        data = json.loads(response.data.decode('utf-8'))
        book = next(b for b in data['books'] if b['id'] == book_id)
        assert book['read'] == False
    
    # 测试批量删除
    response = client.post('/books/batch', json={"book_ids": book_ids, "action": "delete"})
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'success'
    
    # 验证删除结果
    for book_id in book_ids:
        response = client.get('/books')
        data = json.loads(response.data.decode('utf-8'))
        assert not any(book['id'] == book_id for book in data['books'])

def test_invalid_batch_operations(client):
    # 测试缺少book_ids
    response = client.post('/books/batch', json={"action": "delete"})
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'error'
    
    # 测试缺少action
    response = client.post('/books/batch', json={"book_ids": []})
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'error'
    
    # 测试无效action
    response = client.post('/books/batch', json={"book_ids": [], "action": "invalid_action"})
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['status'] == 'error'

if __name__ == '__main__':
    pytest.main([__file__])