import unittest
import json
from app import app, BOOKS

class TestBooksAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a test book
        self.test_book = {
            'title': 'Test Book',
            'author': 'Test Author',
            'read': False
        }
        
        # Clear existing books and add test book
        BOOKS.clear()
        self.app.post('/books', data=json.dumps(self.test_book), content_type='application/json')
        # Get the test book ID
        response = self.app.get('/books')
        self.test_book_id = response.json['books'][0]['id'] if response.json.get('books') else None

    def test_get_all_books(self):
        response = self.app.get('/books')
        self.assertEqual(response.status_code, 200)
        self.assertIn('books', response.json)
        self.assertGreater(len(response.json['books']), 0)

    def test_get_books_with_filters(self):
        # Test title filter
        response = self.app.get('/books?title=Test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 1)
        self.assertEqual(response.json['books'][0]['title'], 'Test Book')
        
        # Test author filter
        response = self.app.get('/books?author=Test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 1)
        self.assertEqual(response.json['books'][0]['author'], 'Test Author')
        
        # Test read filter
        response = self.app.get('/books?read=false')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 1)
        self.assertEqual(response.json['books'][0]['read'], False)

    def test_get_books_with_sorting(self):
        # Add another book for sorting test
        another_book = {
            'title': 'Another Book',
            'author': 'Another Author',
            'read': True
        }
        self.app.post('/books', data=json.dumps(another_book), content_type='application/json')
        
        # Test ascending sort by title
        response = self.app.get('/books?sort_by=title&sort_order=asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 2)
        self.assertEqual(response.json['books'][0]['title'], 'Another Book')
        self.assertEqual(response.json['books'][1]['title'], 'Test Book')
        
        # Test descending sort by title
        response = self.app.get('/books?sort_by=title&sort_order=desc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 2)
        self.assertEqual(response.json['books'][0]['title'], 'Test Book')
        self.assertEqual(response.json['books'][1]['title'], 'Another Book')

    def test_get_books_with_pagination(self):
        # Add multiple books for pagination test
        for i in range(15):
            book = {
                'title': f'Book {i}',
                'author': f'Author {i}',
                'read': i % 2 == 0
            }
            self.app.post('/books', data=json.dumps(book), content_type='application/json')
        
        # Test first page with 10 items per page
        response = self.app.get('/books?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 10)
        self.assertEqual(response.json['total_books'], 16)  # 1 test book + 15 new books
        self.assertEqual(response.json['total_pages'], 2)
        self.assertEqual(response.json['current_page'], 1)
        
        # Test second page
        response = self.app.get('/books?page=2&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['books']), 6)
        self.assertEqual(response.json['current_page'], 2)

    def test_batch_delete_books(self):
        # Clear existing books to ensure clean state
        BOOKS.clear()
        # Add first test book
        self.app.post('/books', data=json.dumps(self.test_book), content_type='application/json')
        # Add another book for batch test
        another_book = {
            'title': 'Another Book',
            'author': 'Another Author',
            'read': True
        }
        self.app.post('/books', data=json.dumps(another_book), content_type='application/json')
        # Get book IDs
        response = self.app.get('/books')
        self.test_book_id = response.json['books'][0]['id']
        another_book_id = response.json['books'][1]['id']
        
        # Verify initial count
        self.assertEqual(len(response.json['books']), 2)
        
        # Test batch delete
        response = self.app.post('/books/batch', data=json.dumps({
            'book_ids': [self.test_book_id, another_book_id],
            'action': 'delete'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Deleted 2 books', response.json['message'])
        
        # Verify books are deleted
        response = self.app.get('/books')
        self.assertEqual(len(response.json['books']), 0)

    def test_batch_mark_read(self):
        # Clear existing books to ensure clean state
        BOOKS.clear()
        # Add first test book (unread)
        self.app.post('/books', data=json.dumps(self.test_book), content_type='application/json')
        # Add another unread book for batch test
        another_book = {
            'title': 'Another Book',
            'author': 'Another Author',
            'read': False
        }
        self.app.post('/books', data=json.dumps(another_book), content_type='application/json')
        # Get book IDs
        response = self.app.get('/books')
        self.test_book_id = response.json['books'][0]['id']
        another_book_id = response.json['books'][1]['id']
        
        # Verify initial state
        self.assertEqual(response.json['books'][0]['read'], False)
        self.assertEqual(response.json['books'][1]['read'], False)
        
        # Test batch mark as read
        response = self.app.post('/books/batch', data=json.dumps({
            'book_ids': [self.test_book_id, another_book_id],
            'action': 'mark_read'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Marked 2 books as read', response.json['message'])
        
        # Verify books are marked as read
        response = self.app.get('/books')
        self.assertEqual(response.json['books'][0]['read'], True)
        self.assertEqual(response.json['books'][1]['read'], True)

    def test_batch_mark_unread(self):
        # Clear existing books to ensure clean state
        BOOKS.clear()
        # Add first test book (read)
        read_test_book = self.test_book.copy()
        read_test_book['read'] = True
        self.app.post('/books', data=json.dumps(read_test_book), content_type='application/json')
        # Add another read book for batch test
        another_book = {
            'title': 'Another Book',
            'author': 'Another Author',
            'read': True
        }
        self.app.post('/books', data=json.dumps(another_book), content_type='application/json')
        # Get book IDs
        response = self.app.get('/books')
        self.test_book_id = response.json['books'][0]['id']
        another_book_id = response.json['books'][1]['id']
        
        # Verify initial state
        self.assertEqual(response.json['books'][0]['read'], True)
        self.assertEqual(response.json['books'][1]['read'], True)
        
        # Test batch mark as unread
        response = self.app.post('/books/batch', data=json.dumps({
            'book_ids': [another_book_id],
            'action': 'mark_unread'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Marked 1 books as unread', response.json['message'])
        
        # Verify book is marked as unread
        response = self.app.get('/books')
        # Sort books by ID to ensure consistent order
        books = sorted(response.json['books'], key=lambda x: x['id'])
        # Verify only the target book was marked unread
        self.assertEqual(books[0]['read'], True)
        self.assertEqual(books[1]['read'], False)

if __name__ == '__main__':
    unittest.main()