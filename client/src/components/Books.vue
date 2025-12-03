<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <h1>Books</h1>
        <hr><br>
        <alert :message=message v-if="showMessage"></alert>
        
        <!-- 搜索和过滤区域 -->
        <div class="row mb-4">
          <div class="col-md-4">
            <div class="position-relative">
              <input
                type="text"
                class="form-control"
                placeholder="搜索书名或作者..."
                v-model="searchQuery"
                @input="onSearchChange"
                @focus="displaySearchHistory"
                @blur="hideSearchHistory"
              >
              <!-- 搜索历史下拉框 -->
              <div 
                v-if="showSearchHistory && searchHistory.length > 0" 
                class="position-absolute w-100 mt-1 bg-white border rounded shadow-sm z-10"
                style="max-height: 200px; overflow-y: auto;"
              >
                <div 
                  v-for="(history, index) in searchHistory" 
                  :key="index"
                  class="p-2 cursor-pointer hover:bg-light"
                  @click="selectSearchHistory(history)"
                >
                  <small>{{ history }}</small>
                  <button 
                    type="button" 
                    class="close float-right"
                    @click.stop="removeSearchHistory(index)"
                  >
                    <span aria-hidden="true">&times;</span>
                  </button>
                </div>
                <div class="p-2 border-top">
                  <button 
                    type="button" 
                    class="btn btn-sm btn-link p-0"
                    @click="clearSearchHistory"
                  >
                    清除历史记录
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-control" v-model="readFilter" @change="onFilterChange">
              <option value="">全部状态</option>
              <option value="true">已读</option>
              <option value="false">未读</option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-control" v-model="sortBy" @change="onSortChange">
              <option value="title">按书名排序</option>
              <option value="author">按作者排序</option>
              <option value="read">按阅读状态排序</option>
            </select>
            <select class="form-control mt-1" v-model="sortOrder" @change="onSortChange">
              <option value="asc">升序</option>
              <option value="desc">降序</option>
            </select>
          </div>
          <div class="col-md-2">
            <button
              type="button"
              class="btn btn-success btn-sm"
              @click="toggleAddBookModal">
              Add Book
            </button>
          </div>
        </div>
        
        <!-- 批量操作区域 -->
        <div class="row mb-3" v-if="selectedBooks.length > 0">
          <div class="col-md-12">
            <div class="btn-group" role="group">
              <button
                type="button"
                class="btn btn-danger btn-sm"
                @click="batchDeleteBooks">
                批量删除 ({{ selectedBooks.length }})
              </button>
              <button
                type="button"
                class="btn btn-primary btn-sm"
                @click="batchMarkAsRead(true)">
                批量标记为已读
              </button>
              <button
                type="button"
                class="btn btn-secondary btn-sm"
                @click="batchMarkAsRead(false)">
                批量标记为未读
              </button>
              <button
                type="button"
                class="btn btn-light btn-sm"
                @click="clearSelection">
                取消选择
              </button>
            </div>
          </div>
        </div>
        
        <!-- 图书列表 -->
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col" style="width: 50px;">
                <input
                  type="checkbox"
                  v-model="selectAll"
                  @change="toggleSelectAll"
                >
              </th>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">Read?</th>
              <th scope="col" style="width: 150px;"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="book.id">
              <td>
                <input
                  type="checkbox"
                  v-model="selectedBooks"
                  :value="book.id"
                >
              </td>
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
              <td>
                <span v-if="book.read" class="text-success">Yes</span>
                <span v-else class="text-danger">No</span>
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
        
        <!-- 分页控件 -->
        <div class="row" v-if="pagination.total > 0">
          <div class="col-md-12">
            <nav aria-label="Page navigation">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: pagination.page === 1 }">
                  <button class="page-link" @click="changePage(pagination.page - 1)">
                    上一页
                  </button>
                </li>
                <li class="page-item" 
                    v-for="pageNum in pagination.pages" 
                    :key="pageNum"
                    :class="{ active: pagination.page === pageNum }">
                  <button class="page-link" @click="changePage(pageNum)">
                    {{ pageNum }}
                  </button>
                </li>
                <li class="page-item" :class="{ disabled: pagination.page === pagination.pages }">
                  <button class="page-link" @click="changePage(pagination.page + 1)">
                    下一页
                  </button>
                </li>
              </ul>
              <div class="text-center mt-2">
                显示 {{ (pagination.page - 1) * pagination.per_page + 1 }} - 
                {{ Math.min(pagination.page * pagination.per_page, pagination.total) }} 
                条，共 {{ pagination.total }} 条
                <select class="form-control form-control-sm d-inline-block ml-2" 
                        style="width: auto" 
                        v-model="pagination.per_page"
                        @change="onPerPageChange">
                  <option value="5">5条/页</option>
                  <option value="10">10条/页</option>
                  <option value="20">20条/页</option>
                  <option value="50">50条/页</option>
                </select>
              </div>
            </nav>
          </div>
        </div>
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
        read: [],
      },
      books: [],
      editBookForm: {
        id: '',
        title: '',
        author: '',
        read: [],
      },
      message: '',
      showMessage: false,
      // 搜索和过滤
      searchQuery: '',
      readFilter: '',
      // 排序
      sortBy: 'title',
      sortOrder: 'asc',
      // 分页
      pagination: {
        page: 1,
        per_page: 10,
        total: 0,
        pages: 0
      },
      // 批量操作
      selectedBooks: [],
      selectAll: false,
      // 搜索历史
      searchHistory: [],
      maxHistorySize: 10,
      showSearchHistory: false
    };
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
        })
        .catch((error) => {
          console.log(error);
          this.getBooks();
        });
    },
    getBooks() {
      // 构建查询参数
      const params = new URLSearchParams();
      if (this.searchQuery) params.append('search', this.searchQuery);
      if (this.readFilter) params.append('read_status', this.readFilter);
      params.append('sort_by', this.sortBy);
      params.append('sort_order', this.sortOrder);
      params.append('page', this.pagination.page);
      params.append('per_page', this.pagination.per_page);
      
      const path = `http://localhost:5001/books?${params.toString()}`;
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
          this.pagination = res.data.pagination;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    
    // 搜索变化处理
    onSearchChange() {
      this.pagination.page = 1; // 搜索后回到第一页
      this.addToSearchHistory(this.searchQuery);
      this.getBooks();
    },
    
    // 过滤变化处理
    onFilterChange() {
      this.pagination.page = 1; // 过滤后回到第一页
      this.getBooks();
    },
    
    // 排序变化处理
    onSortChange() {
      this.pagination.page = 1; // 排序后回到第一页
      this.getBooks();
    },
    
    // 每页显示数量变化处理
    onPerPageChange() {
      this.pagination.page = 1; // 改变每页数量后回到第一页
      this.getBooks();
    },
    
    // 改变页码
    changePage(pageNum) {
      if (pageNum < 1 || pageNum > this.pagination.pages) return;
      this.pagination.page = pageNum;
      this.getBooks();
    },
    
    // 添加到搜索历史
    addToSearchHistory(query) {
      if (!query.trim()) return;
      
      // 移除已存在的相同查询
      this.searchHistory = this.searchHistory.filter(item => item !== query.trim());
      
      // 添加到历史记录开头
      this.searchHistory.unshift(query.trim());
      
      // 限制历史记录数量
      if (this.searchHistory.length > this.maxHistorySize) {
        this.searchHistory = this.searchHistory.slice(0, this.maxHistorySize);
      }
    },
    
    // 显示搜索历史
    displaySearchHistory() {
      this.showSearchHistory = true;
    },
    
    // 隐藏搜索历史
    hideSearchHistory() {
      // 延迟隐藏，以便点击历史项时能触发点击事件
      setTimeout(() => {
        this.showSearchHistory = false;
      }, 200);
    },
    
    // 选择搜索历史项
    selectSearchHistory(history) {
      this.searchQuery = history;
      this.showSearchHistory = false;
      this.onSearchChange();
    },
    
    // 移除单个搜索历史项
    removeSearchHistory(index) {
      this.searchHistory.splice(index, 1);
    },
    
    // 清除所有搜索历史
    clearSearchHistory() {
      this.searchHistory = [];
    },
    
    // 切换全选
    toggleSelectAll() {
      if (this.selectAll) {
        this.selectedBooks = this.books.map(book => book.id);
      } else {
        this.selectedBooks = [];
      }
    },
    
    // 清除选择
    clearSelection() {
      this.selectedBooks = [];
      this.selectAll = false;
    },
    
    // 批量删除图书
    batchDeleteBooks() {
      if (this.selectedBooks.length === 0) return;
      
      if (confirm(`确定要删除选中的 ${this.selectedBooks.length} 本图书吗？`)) {
        const path = 'http://localhost:5001/books/batch';
        axios.delete(path, { 
          data: { book_ids: this.selectedBooks }
        })
          .then(() => {
            this.getBooks();
            this.clearSelection();
            this.message = `成功删除 ${this.selectedBooks.length} 本图书`;
            this.showMessage = true;
          })
          .catch((error) => {
            console.error(error);
            this.getBooks();
          });
      }
    },
    
    // 批量标记阅读状态
    batchMarkAsRead(readStatus) {
      if (this.selectedBooks.length === 0) return;
      
      const path = 'http://localhost:5001/books/batch';
      axios.put(path, { 
        book_ids: this.selectedBooks,
        read: readStatus
      })
        .then(() => {
          this.getBooks();
          this.clearSelection();
          const statusText = readStatus ? '已读' : '未读';
          this.message = `成功标记 ${this.selectedBooks.length} 本图书为${statusText}`;
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          this.getBooks();
        });
    },
    handleAddReset() {
      this.initForm();
    },
    handleAddSubmit() {
      this.toggleAddBookModal();
      let read = false;
      if (this.addBookForm.read[0]) {
        read = true;
      }
      const payload = {
        title: this.addBookForm.title,
        author: this.addBookForm.author,
        read, // property shorthand
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
      this.getBooks(); // why?
    },
    handleEditSubmit() {
      this.toggleEditBookModal(null);
      let read = false;
      if (this.editBookForm.read) read = true;
      const payload = {
        title: this.editBookForm.title,
        author: this.editBookForm.author,
        read,
      };
      this.updateBook(payload, this.editBookForm.id);
    },
    initForm() {
      this.addBookForm.title = '';
      this.addBookForm.author = '';
      this.addBookForm.read = [];
      this.editBookForm.id = '';
      this.editBookForm.title = '';
      this.editBookForm.author = '';
      this.editBookForm.read = [];
    },
    removeBook(bookID) {
      const path = `http://localhost:5001/books/${bookID}`;
      axios.delete(path)
        .then(() => {
          this.getBooks();
          this.message = 'Book removed!';
          this.showMessage = true;
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
        this.editBookForm = book;
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
        })
        .catch((error) => {
          console.error(error);
          this.getBooks();
        });
    },
  },
  created() {
    this.getBooks();
  },
  
  watch: {
    // 监听已选图书变化，更新全选状态
    selectedBooks: {
      handler() {
        this.selectAll = this.selectedBooks.length > 0 && this.selectedBooks.length === this.books.length;
      },
      deep: true
    },
    
    // 监听图书列表变化，更新全选状态
    books: {
      handler() {
        this.selectAll = this.selectedBooks.length > 0 && this.selectedBooks.length === this.books.length;
      },
      deep: true
    }
  },
};
</script>
