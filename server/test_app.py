import unittest
import json
from app import app, BOOKS
import uuid

class TestBookAPI(unittest.TestCase):
    """测试图书API的单元测试"""
    
    def setUp(self):
        """在每个测试前设置测试环境"""
        self.app = app.test_client()
        self.app.testing = True
        
        # 保存原始图书数据
        self.original_books = BOOKS.copy()
        
        # 添加一些测试数据
        self.test_books = [
            {
                'id': uuid.uuid4().hex,
                'title': 'Test Book 1',
                'author': 'Author One',
                'read': True
            },
            {
                'id': uuid.uuid4().hex,
                'title': 'Test Book 2',
                'author': 'Author Two',
                'read': False
            },
            {
                'id': uuid.uuid4().hex,
                'title': 'Another Test Book',
                'author': 'Author One',
                'read': True
            },
            {
                'id': uuid.uuid4().hex,
                'title': 'Python Programming',
                'author': 'Guido van Rossum',
                'read': False
            }
        ]
        
        BOOKS.extend(self.test_books)
    
    def tearDown(self):
        """在每个测试后清理测试环境"""
        # 恢复原始图书数据
        del BOOKS[:]
        BOOKS.extend(self.original_books)
    
    def test_get_books_with_pagination(self):
        """测试带分页的图书列表获取"""
        response = self.app.get('/books?page=1&per_page=2')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['books']), 2)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['per_page'], 2)
        self.assertGreaterEqual(data['pagination']['total'], 4)
    
    def test_search_books(self):
        """测试图书搜索功能"""
        # 按书名搜索
        response = self.app.get('/books?search=Test')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data['books']), 3)
        
        # 按作者搜索
        response = self.app.get('/books?search=Author One')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data['books']), 2)
    
    def test_filter_books_by_read_status(self):
        """测试按阅读状态过滤图书"""
        # 过滤已读图书
        response = self.app.get('/books?read=true')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        for book in data['books']:
            self.assertTrue(book['read'])
        
        # 过滤未读图书
        response = self.app.get('/books?read=false')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        for book in data['books']:
            self.assertFalse(book['read'])
    
    def test_sort_books(self):
        """测试图书排序功能"""
        # 按书名升序排序
        response = self.app.get('/books?sort_by=title&sort_order=asc')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        if len(data['books']) >= 2:
            self.assertLessEqual(data['books'][0]['title'], data['books'][1]['title'])
        
        # 按作者降序排序
        response = self.app.get('/books?sort_by=author&sort_order=desc')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        if len(data['books']) >= 2:
            self.assertGreaterEqual(data['books'][0]['author'], data['books'][1]['author'])
    
    def test_batch_delete_books(self):
        """测试批量删除图书功能"""
        # 获取测试图书的ID
        book_ids = [book['id'] for book in self.test_books[:2]]
        
        response = self.app.delete('/books/batch', 
                                 data=json.dumps({'book_ids': book_ids}),
                                 content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Deleted 2 out of 2 books', data['message'])
    
    def test_batch_update_read_status(self):
        """测试批量更新阅读状态功能"""
        # 获取测试图书的ID
        book_ids = [book['id'] for book in self.test_books[:2]]
        
        # 批量标记为已读
        response = self.app.put('/books/batch', 
                               data=json.dumps({'book_ids': book_ids, 'read': True}),
                               content_type='application/json')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Updated 2 out of 2 books', data['message'])
    
    def test_combined_filters(self):
        """测试组合使用搜索、过滤和排序功能"""
        response = self.app.get('/books?search=Test&read=true&sort_by=title&sort_order=desc')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)
        
        # 验证所有返回的图书都符合搜索条件和过滤条件
        for book in data['books']:
            self.assertIn('Test', book['title'])
            self.assertTrue(book['read'])

if __name__ == '__main__':
    unittest.main()
