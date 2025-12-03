<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <h1>Books</h1>
        <hr>
        <alert :message=message v-if="showMessage"></alert>
        
        <!-- Search and Filter Section -->
        <div class="row mb-3">
          <div class="col-md-4">
            <div class="position-relative">
              <input
                type="text"
                class="form-control"
                placeholder="Search by title or author..."
                v-model="searchQuery"
                @input="handleSearchInput"
                @focus="showSearchSuggestions = true">
              
              <!-- Search Suggestions Dropdown -->
              <div v-if="showSearchSuggestions && (searchSuggestions.length > 0 || searchHistory.length > 0)" class="dropdown-menu show position-absolute w-100 mt-1">
                <!-- Search Suggestions -->
                <template v-if="searchSuggestions.length > 0">
                  <div class="dropdown-header small text-muted">Suggestions</div>
                  <a v-for="suggestion in searchSuggestions" :key="suggestion" 
                     class="dropdown-item" @click="selectSearchSuggestion(suggestion)">
                    {{ suggestion }}
                  </a>
                </template>
                
                <!-- Search History -->
                <template v-if="searchHistory.length > 0">
                  <div v-if="searchSuggestions.length > 0" class="dropdown-divider"></div>
                  <div class="dropdown-header small text-muted">
                    History
                    <button type="button" class="btn btn-link btn-sm p-0 ml-2 text-muted" 
                            @click="clearSearchHistory">
                      Clear
                    </button>
                  </div>
                  <a v-for="item in searchHistory" :key="item" 
                     class="dropdown-item" @click="selectSearchSuggestion(item)">
                    {{ item }}
                  </a>
                </template>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-control" v-model="readFilter" @change="performSearch">
              <option value="all">All Books</option>
              <option value="true">Read</option>
              <option value="false">Unread</option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-control" v-model="sortBy" @change="performSearch">
              <option value="title">Sort by Title</option>
              <option value="author">Sort by Author</option>
              <option value="read">Sort by Read Status</option>
            </select>
            <select class="form-control mt-1" v-model="sortOrder" @change="performSearch">
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </div>
          <div class="col-md-2">
            <button
              type="button"
              class="btn btn-success btn-sm mb-1"
              @click="toggleAddBookModal">
              Add Book
            </button>
            <br>
            <button
              type="button"
              class="btn btn-danger btn-sm mb-1"
              @click="handleBatchDelete"
              :disabled="selectedBooks.length === 0">
              Delete Selected
            </button>
            <br>
            <button
              type="button"
              class="btn btn-primary btn-sm"
              @click="handleBatchMarkRead"
              :disabled="selectedBooks.length === 0">
              Mark as Read
            </button>
            <br>
            <button
              type="button"
              class="btn btn-secondary btn-sm mt-1"
              @click="handleBatchMarkUnread"
              :disabled="selectedBooks.length === 0">
              Mark as Unread
            </button>
          </div>
        </div>

        <!-- Books Table -->
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col" style="width: 50px;">
                <input type="checkbox" @change="toggleSelectAll" v-model="selectAll">
              </th>
              <th scope="col">Title</th>
              <th scope="col">Author</th>

              <th scope="col">Read?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="book.id">
              <td>
                <input type="checkbox" v-model="selectedBooks" :value="book.id">
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

        <!-- Pagination -->
        <div v-if="pagination.pages > 0" class="mt-4">
          <div class="text-center mb-2">
            <select class="form-control d-inline w-auto mr-2" v-model="perPage" @change="performSearch">
              <option value="5">5 per page</option>
              <option value="10">10 per page</option>
              <option value="20">20 per page</option>
            </select>
            <span class="text-muted">
              Showing {{ ((pagination.page - 1) * perPage) + 1 }} to {{ Math.min(pagination.page * perPage, pagination.total) }} of {{ pagination.total }} books
            </span>
          </div>
          
          <nav aria-label="Page navigation" v-if="pagination.pages > 1">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: pagination.page === 1 }">
                <button class="page-link" @click="goToPage(pagination.page - 1)">Previous</button>
              </li>
              <li v-for="pageNum in getPageNumbers()" :key="pageNum" class="page-item" :class="{ active: pageNum === pagination.page }">
                <button class="page-link" @click="goToPage(pageNum)">{{ pageNum }}</button>
              </li>
              <li class="page-item" :class="{ disabled: pagination.page === pagination.pages }">
                <button class="page-link" @click="goToPage(pagination.page + 1)">Next</button>
              </li>
            </ul>
          </nav>
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
      // Search and filter data
      searchQuery: '',
      readFilter: 'all',
      sortBy: 'title',
      sortOrder: 'asc',
      // Search history and suggestions
      searchHistory: [],
      searchSuggestions: [],
      showSearchSuggestions: false,
      searchTimeout: null,
      // Pagination data
      currentPage: 1,
      perPage: 10,
      pagination: {
        page: 1,
        per_page: 10,
        total: 0,
        pages: 0
      },
      // Selected books for batch operations
      selectedBooks: [],
      selectAll: false,
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
    // Search related methods
    loadSearchHistory() {
      const path = 'http://localhost:5000/books/search/history';
      axios.get(path)
        .then((res) => {
          this.searchHistory = res.data.history;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    handleSearchInput() {
      // Clear previous timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // Show suggestions after 300ms delay
      this.searchTimeout = setTimeout(() => {
        this.generateSearchSuggestions();
        this.performSearch();
      }, 300);
    },
    generateSearchSuggestions() {
      if (!this.searchQuery.trim()) {
        this.searchSuggestions = [];
        return;
      }
      
      // Generate suggestions from book titles and authors
      const query = this.searchQuery.toLowerCase();
      const suggestions = new Set();
      
      this.books.forEach(book => {
        if (book.title.toLowerCase().includes(query)) {
          suggestions.add(book.title);
        }
        if (book.author.toLowerCase().includes(query)) {
          suggestions.add(book.author);
        }
      });
      
      this.searchSuggestions = Array.from(suggestions).slice(0, 5); // Show max 5 suggestions
    },
    selectSearchSuggestion(suggestion) {
      this.searchQuery = suggestion;
      this.showSearchSuggestions = false;
      this.performSearch();
    },
    clearSearchHistory() {
      const path = 'http://localhost:5000/books/search/history';
      axios.delete(path)
        .then(() => {
          this.searchHistory = [];
          this.message = 'Search history cleared!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    
    addBook(payload) {
      const path = 'http://localhost:5000/books';
      axios.post(path, payload)
        .then(() => {
          this.performSearch();
          this.message = 'Book added!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.log(error);
          this.performSearch();
        });
    },
    getBooksWithFilters() {
      const params = new URLSearchParams();
      if (this.searchQuery) params.append('search', this.searchQuery);
      if (this.readFilter !== 'all') params.append('read_status', this.readFilter);
      params.append('sort_by', this.sortBy);
      params.append('sort_order', this.sortOrder);
      params.append('page', this.currentPage);
      params.append('per_page', this.perPage);

      const path = `http://localhost:5000/books?${params.toString()}`;
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
          this.pagination = res.data.pagination;
          this.selectedBooks = [];
          this.selectAll = false;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    performSearch() {
      this.currentPage = 1;
      this.getBooksWithFilters();
    },
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.currentPage = page;
        this.getBooksWithFilters();
      }
    },
    getPageNumbers() {
      const pages = [];
      const maxVisiblePages = 5;
      let startPage = Math.max(1, this.pagination.page - Math.floor(maxVisiblePages / 2));
      let endPage = Math.min(this.pagination.pages, startPage + maxVisiblePages - 1);

      if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      return pages;
    },
    toggleSelectAll() {
      if (this.selectAll) {
        this.selectedBooks = this.books.map(book => book.id);
      } else {
        this.selectedBooks = [];
      }
    },
    handleBatchDelete() {
      if (confirm(`Are you sure you want to delete ${this.selectedBooks.length} book(s)?`)) {
        const path = 'http://localhost:5000/books/batch';
        axios.delete(path, {
          data: {
            book_ids: this.selectedBooks
          }
        })
        .then(() => {
          this.performSearch();
          this.message = `${this.selectedBooks.length} book(s) deleted!`;
          this.showMessage = true;
        })
        .catch((error) => {
          console.log(error);
          this.performSearch();
        });
      }
    },
    handleBatchMarkRead() {
      const path = 'http://localhost:5000/books/batch/mark';
      axios.put(path, {
        book_ids: this.selectedBooks,
        read: true
      })
      .then(() => {
        this.performSearch();
        this.message = `${this.selectedBooks.length} book(s) marked as read!`;
        this.showMessage = true;
      })
      .catch((error) => {
        console.log(error);
        this.performSearch();
      });
    },
    handleBatchMarkUnread() {
      const path = 'http://localhost:5000/books/batch/mark';
      axios.put(path, {
        book_ids: this.selectedBooks,
        read: false
      })
      .then(() => {
        this.performSearch();
        this.message = `${this.selectedBooks.length} book(s) marked as unread!`;
        this.showMessage = true;
      })
      .catch((error) => {
        console.log(error);
        this.performSearch();
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
        read,
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
      this.performSearch();
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
          this.performSearch();
          this.message = 'Book removed!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.log(error);
          this.performSearch();
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
          this.performSearch();
          this.message = 'Book updated!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          this.performSearch();
        });
    },
  },
  watch: {
    selectedBooks() {
      this.selectAll = this.books.length > 0 && this.selectedBooks.length === this.books.length;
    }
  },
  created() {
    this.performSearch();
    this.loadSearchHistory();
  },
  mounted() {
    // Close suggestions when clicking outside
    document.addEventListener('click', (event) => {
      const searchContainer = this.$el.querySelector('.position-relative');
      if (searchContainer && !searchContainer.contains(event.target)) {
        this.showSearchSuggestions = false;
      }
    });
  },
};
</script>