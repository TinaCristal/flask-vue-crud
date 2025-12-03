<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <h1>Books</h1>
        <hr>
        
        <!-- 消息提示 -->
        <alert :message=message v-if="showMessage"></alert>
        
        <!-- 搜索和过滤区域 -->
        <div class="row mb-3">
          <div class="col-md-4">
            <input
              type="text"
              class="form-control"
              v-model="searchQuery"
              placeholder="搜索书名或作者"
              @input="onSearch">
          </div>
          <div class="col-md-3">
            <select class="form-control" v-model="readFilter" @change="onFilter">
              <option value="">所有状态</option>
              <option value="true">已读</option>
              <option value="false">未读</option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-control" v-model="perPage" @change="onPerPageChange">
              <option :value="10">10条/页</option>
              <option :value="20">20条/页</option>
              <option :value="50">50条/页</option>
            </select>
          </div>
          <div class="col-md-3">
            <button
              type="button"
              class="btn btn-success btn-sm me-2"
              @click="toggleAddBookModal">
              Add Book
            </button>
            <!-- 批量操作按钮 -->
            <div class="btn-group" role="group" v-if="selectedBooks.length > 0">
              <button
                type="button"
                class="btn btn-danger btn-sm"
                @click="batchDelete">
                批量删除 ({{ selectedBooks.length }})
              </button>
              <button
                type="button"
                class="btn btn-warning btn-sm"
                @click="batchMarkAsRead">
                标记已读
              </button>
              <button
                type="button"
                class="btn btn-info btn-sm"
                @click="batchMarkAsUnread">
                标记未读
              </button>
            </div>
          </div>
        </div>
        
        <!-- 图书表格 -->
        <table class="table table-hover">
          <thead>
            <tr>
              <th style="width: 50px;">
                <input
                  type="checkbox"
                  v-model="selectAll"
                  @change="onSelectAll">
              </th>
              <th scope="col" @click="sortBy('title')">
                书名
                <span v-if="sortFields.some(sort => sort.field === 'title')" class="sort-indicator">
                  {{ sortFields.find(sort => sort.field === 'title').order === 'asc' ? '▲' : '▼' }}
                  <span class="sort-priority">
                    {{ sortFields.findIndex(sort => sort.field === 'title') + 1 }}
                  </span>
                </span>
              </th>
              <th scope="col" @click="sortBy('author')">
                作者
                <span v-if="sortFields.some(sort => sort.field === 'author')" class="sort-indicator">
                  {{ sortFields.find(sort => sort.field === 'author').order === 'asc' ? '▲' : '▼' }}
                  <span class="sort-priority">
                    {{ sortFields.findIndex(sort => sort.field === 'author') + 1 }}
                  </span>
                </span>
              </th>
              <th scope="col" @click="sortBy('read')">
                阅读状态
                <span v-if="sortFields.some(sort => sort.field === 'read')" class="sort-indicator">
                  {{ sortFields.find(sort => sort.field === 'read').order === 'asc' ? '▲' : '▼' }}
                  <span class="sort-priority">
                    {{ sortFields.findIndex(sort => sort.field === 'read') + 1 }}
                  </span>
                </span>
              </th>
              <th style="width: 150px;"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="book.id">
              <td>
                <input
                  type="checkbox"
                  :value="book.id"
                  v-model="selectedBooks"
                  @change="onSelectChange">
              </td>
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
              <td>
                <span v-if="book.read" class="badge bg-success">已读</span>
                <span v-else class="badge bg-secondary">未读</span>
              </td>
              <td>
                <div class="btn-group" role="group">
                  <button
                    type="button"
                    class="btn btn-warning btn-sm"
                    @click="toggleEditBookModal(book)">
                    Update
                  </button>
                  <button
                    type="button"
                    class="btn btn-danger btn-sm"
                    @click="handleDeleteBook(book)">
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- 分页导航 -->
        <nav aria-label="Page navigation">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="changePage(currentPage - 1)">上一页</button>
            </li>
            <li class="page-item" 
                v-for="page in visiblePages"
                :key="page"
                :class="{ active: currentPage === page }">
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="changePage(currentPage + 1)">下一页</button>
            </li>
          </ul>
          <div class="text-center mt-2">
            <small>显示 {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, total) }} 条，共 {{ total }} 条</small>
          </div>
        </nav>
      </div>
    </div>

    <!-- add new book modal -->
    <div
      ref="addBookModal"
      class="modal fade"
      :class="{ show: activeAddBookModal, 'd-block': activeAddBookModal }"
      tabindex="-1"
      role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add a new book</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="toggleAddBookModal">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="addBookTitle" class="form-label">Title:</label>
                <input
                  type="text"
                  class="form-control"
                  id="addBookTitle"
                  v-model="addBookForm.title"
                  placeholder="Enter title">
              </div>
              <div class="mb-3">
                <label for="addBookAuthor" class="form-label">Author:</label>
                <input
                  type="text"
                  class="form-control"
                  id="addBookAuthor"
                  v-model="addBookForm.author"
                  placeholder="Enter author">
              </div>
              <div class="mb-3 form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="addBookRead"
                  v-model="addBookForm.read">
                <label class="form-check-label" for="addBookRead">Read?</label>
              </div>
              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  @click="handleAddSubmit">
                  Submit
                </button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  @click="handleAddReset">
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeAddBookModal" class="modal-backdrop fade show"></div>

    <!-- edit book modal -->
    <div
      ref="editBookModal"
      class="modal fade"
      :class="{ show: activeEditBookModal, 'd-block': activeEditBookModal }"
      tabindex="-1"
      role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Update</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="toggleEditBookModal">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="editBookTitle" class="form-label">Title:</label>
                <input
                  type="text"
                  class="form-control"
                  id="editBookTitle"
                  v-model="editBookForm.title"
                  placeholder="Enter title">
              </div>
              <div class="mb-3">
                <label for="editBookAuthor" class="form-label">Author:</label>
                <input
                  type="text"
                  class="form-control"
                  id="editBookAuthor"
                  v-model="editBookForm.author"
                  placeholder="Enter author">
              </div>
              <div class="mb-3 form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="editBookRead"
                  v-model="editBookForm.read">
                <label class="form-check-label" for="editBookRead">Read?</label>
              </div>
              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  @click="handleEditSubmit">
                  Submit
                </button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  @click="handleEditCancel">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeEditBookModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      activeAddBookModal: false,
      activeEditBookModal: false,
      addBookForm: {
        title: '',
        author: '',
        read: false,
      },
      books: [],
      editBookForm: {
        id: '',
        title: '',
        author: '',
        read: false,
      },
      message: '',
      showMessage: false,
      // 搜索和过滤
      searchQuery: '',
      readFilter: '',
      // 分页
      currentPage: 1,
      perPage: 10,
      total: 0,
      totalPages: 1,
      // 多列组合排序
      sortFields: [
        { field: 'title', order: 'asc' },
        { field: 'author', order: 'asc' }
      ],
      // 批量操作
      selectedBooks: [],
      selectAll: false,
    };
  },
  computed: {
    visiblePages() {
      const pages = [];
      const total = this.totalPages;
      const current = this.currentPage;
      const showPages = 5;
      
      let start = Math.max(1, current - Math.floor(showPages / 2));
      let end = Math.min(total, start + showPages - 1);
      
      if (end - start + 1 < showPages) {
        start = Math.max(1, end - showPages + 1);
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      return pages;
    }
  },
  components: {
    alert: Alert,
  },
  methods: {
    addBook(payload) {
      const path = 'http://localhost:5001/books';
      axios.post(path, payload)
        .then(() => {
          this.getBooks();
          this.message = 'Book added!';
          this.showMessage = true;
          this.hideMessage();
        })
        .catch((error) => {
          console.log(error);
          this.getBooks();
        });
    },
    getBooks() {
      const params = new URLSearchParams();
      if (this.searchQuery) {
        params.append('query', this.searchQuery);
      }
      if (this.readFilter !== '') {
        params.append('read', this.readFilter);
      }
      params.append('page', this.currentPage);
      params.append('per_page', this.perPage);
      
      // 添加多列组合排序参数
      this.sortFields.forEach(sort => {
        params.append('sort_by', sort.field);
        params.append('sort_order', sort.order);
      });
      
      const path = `http://localhost:5001/books?${params.toString()}`;
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
          this.total = res.data.total;
          this.currentPage = res.data.page;
          this.totalPages = res.data.total_pages;
          // 清除选中状态
          this.selectedBooks = [];
          this.selectAll = false;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    handleAddReset() {
      this.initForm();
    },
    handleAddSubmit() {
      this.toggleAddBookModal();
      const payload = {
        title: this.addBookForm.title,
        author: this.addBookForm.author,
        read: this.addBookForm.read,
      };
      this.addBook(payload);
      this.initForm();
    },
    handleDeleteBook(book) {
      this.removeBook(book.id);
    },
    handleEditCancel() {
      this.toggleEditBookModal(null);
      this.initForm();
      this.getBooks();
    },
    handleEditSubmit() {
      this.toggleEditBookModal(null);
      const payload = {
        title: this.editBookForm.title,
        author: this.editBookForm.author,
        read: this.editBookForm.read,
      };
      this.updateBook(payload, this.editBookForm.id);
    },
    initForm() {
      this.addBookForm.title = '';
      this.addBookForm.author = '';
      this.addBookForm.read = false;
      this.editBookForm.id = '';
      this.editBookForm.title = '';
      this.editBookForm.author = '';
      this.editBookForm.read = false;
    },
    removeBook(bookID) {
      const path = `http://localhost:5001/books/${bookID}`;
      axios.delete(path)
        .then(() => {
          this.getBooks();
          this.message = 'Book removed!';
          this.showMessage = true;
          this.hideMessage();
        })
        .catch((error) => {
          console.error(error);
          this.getBooks();
        });
    },
    toggleAddBookModal() {
      const body = document.querySelector('body');
      this.activeAddBookModal = !this.activeAddBookModal;
      if (this.activeAddBookModal) {
        body.classList.add('modal-open');
      } else {
        body.classList.remove('modal-open');
      }
    },
    toggleEditBookModal(book) {
      if (book) {
        this.editBookForm = {...book};
      }
      const body = document.querySelector('body');
      this.activeEditBookModal = !this.activeEditBookModal;
      if (this.activeEditBookModal) {
        body.classList.add('modal-open');
      } else{
        body.classList.remove('modal-open');
      }
    },
    updateBook(payload, bookID) {
      const path = `http://localhost:5001/books/${bookID}`;
      axios.put(path, payload)
        .then(() => {
          this.getBooks();
          this.message = 'Book updated!';
          this.showMessage = true;
          this.hideMessage();
        })
        .catch((error) => {
          console.error(error);
          this.getBooks();
        });
    },
    hideMessage() {
      setTimeout(() => {
        this.showMessage = false;
      }, 3000);
    },
    // 搜索功能
    onSearch() {
      this.currentPage = 1;
      this.getBooks();
    },
    // 过滤功能
    onFilter() {
      this.currentPage = 1;
      this.getBooks();
    },
    // 分页大小变化
    onPerPageChange() {
      this.currentPage = 1;
      this.getBooks();
    },
    // 改变页码
    changePage(page) {
      if (page < 1 || page > this.totalPages || page === this.currentPage) {
        return;
      }
      this.currentPage = page;
      this.getBooks();
      // 滚动到顶部
      window.scrollTo(0, 0);
    },
    // 多列组合排序功能
    sortBy(field) {
      // 查找当前字段是否已经在排序列表中
      const existingSort = this.sortFields.find(sort => sort.field === field);
      
      if (existingSort) {
        // 如果存在，切换排序顺序
        existingSort.order = existingSort.order === 'asc' ? 'desc' : 'asc';
        // 如果当前是第一列，移到末尾以实现多列排序
        if (this.sortFields[0].field === field) {
          this.sortFields.push(this.sortFields.shift());
        }
      } else {
        // 如果不存在，添加到排序列表开头作为主要排序字段
        this.sortFields.unshift({ field, order: 'asc' });
        // 限制最多3个排序字段
        if (this.sortFields.length > 3) {
          this.sortFields.pop();
        }
      }
      
      this.getBooks();
    },
    // 全选功能
    onSelectAll() {
      if (this.selectAll) {
        this.selectedBooks = this.books.map(book => book.id);
      } else {
        this.selectedBooks = [];
      }
    },
    // 选中状态变化
    onSelectChange() {
      this.selectAll = this.selectedBooks.length === this.books.length;
    },
    // 批量删除
    batchDelete() {
      if (this.selectedBooks.length === 0) return;
      
      if (confirm(`确定要删除选中的 ${this.selectedBooks.length} 本书吗？`)) {
        const payload = {
          book_ids: this.selectedBooks,
          action: 'delete'
        };
        
        axios.post('http://localhost:5001/books/batch', payload)
          .then(() => {
            this.getBooks();
            this.message = `成功删除 ${this.selectedBooks.length} 本书`;
            this.showMessage = true;
            this.hideMessage();
          })
          .catch(error => {
            console.error(error);
          });
      }
    },
    // 批量标记已读
    batchMarkAsRead() {
      if (this.selectedBooks.length === 0) return;
      
      const payload = {
        book_ids: this.selectedBooks,
        action: 'mark_as_read'
      };
      
      axios.post('http://localhost:5001/books/batch', payload)
        .then(() => {
          this.getBooks();
          this.message = `成功标记 ${this.selectedBooks.length} 本书为已读`;
          this.showMessage = true;
          this.hideMessage();
        })
        .catch(error => {
          console.error(error);
        });
    },
    // 批量标记未读
    batchMarkAsUnread() {
      if (this.selectedBooks.length === 0) return;
      
      const payload = {
        book_ids: this.selectedBooks,
        action: 'mark_as_unread'
      };
      
      axios.post('http://localhost:5001/books/batch', payload)
        .then(() => {
          this.getBooks();
          this.message = `成功标记 ${this.selectedBooks.length} 本书为未读`;
          this.showMessage = true;
          this.hideMessage();
        })
        .catch(error => {
          console.error(error);
        });
    },
  },
  created() {
    this.getBooks();
  },
};
</script>

<style scoped>
.sort-indicator {
  margin-left: 5px;
  font-size: 0.8em;
  color: #666;
}

.sort-priority {
  margin-left: 2px;
  font-size: 0.6em;
  color: #999;
}

thead th {
  cursor: pointer;
  user-select: none;
}

thead th:hover {
  background-color: #f8f9fa;
}
</style>