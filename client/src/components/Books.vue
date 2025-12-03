<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <h1>Books</h1>
        <hr><br>
        <alert :message=message v-if="showMessage"></alert>
        
        <!-- Search and Filter Section -->
        <div class="row mb-4">
          <div class="col-md-4">
            <input
              type="text"
              class="form-control"
              placeholder="Search by title..."
              v-model="filters.title"
              @input="onFilterChange">
          </div>
          <div class="col-md-4">
            <input
              type="text"
              class="form-control"
              placeholder="Search by author..."
              v-model="filters.author"
              @input="onFilterChange">
          </div>
          <div class="col-md-4">
            <select
              class="form-control"
              v-model="filters.read"
              @change="onFilterChange">
              <option value="">All</option>
              <option value="true">Read</option>
              <option value="false">Unread</option>
            </select>
          </div>
        </div>

        <!-- Batch Operations Section -->
        <div class="row mb-4">
          <div class="col-md-6">
            <button
              type="button"
              class="btn btn-success btn-sm"
              @click="toggleAddBookModal">
              Add Book
            </button>
            <button
              type="button"
              class="btn btn-danger btn-sm"
              @click="batchDelete"
              :disabled="selectedBooks.length === 0"
              style="margin-left: 10px;">
              Delete Selected
            </button>
            <button
              type="button"
              class="btn btn-warning btn-sm"
              @click="batchMarkRead"
              :disabled="selectedBooks.length === 0"
              style="margin-left: 10px;">
              Mark as Read
            </button>
            <button
              type="button"
              class="btn btn-info btn-sm"
              @click="batchMarkUnread"
              :disabled="selectedBooks.length === 0"
              style="margin-left: 10px;">
              Mark as Unread
            </button>
          </div>
          <div class="col-md-6 text-right">
            <select
              class="form-control d-inline-block"
              style="width: auto;"
              v-model="perPage"
              @change="onPerPageChange">
              <option value="5">5 per page</option>
              <option value="10">10 per page</option>
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
            </select>
          </div>
        </div>

        <!-- Books Table -->
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col" style="width: 50px;">
                <input
                  type="checkbox"
                  v-model="selectAll"
                  @change="onSelectAllChange">
              </th>
              <th scope="col" @click="sort('title')" style="cursor: pointer;">
                Title
                <span v-if="sortBy === 'title'" class="ml-1">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th scope="col" @click="sort('author')" style="cursor: pointer;">
                Author
                <span v-if="sortBy === 'author'" class="ml-1">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th scope="col" @click="sort('read')" style="cursor: pointer;">
                Read?
                <span v-if="sortBy === 'read'" class="ml-1">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th scope="col" style="width: 150px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="book.id">
              <td>
                <input
                  type="checkbox"
                  v-model="selectedBooks"
                  :value="book.id"
                  @change="onSelectChange">
              </td>
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
              <td>
                <span v-if="book.read" class="badge bg-success">Yes</span>
                <span v-else class="badge bg-secondary">No</span>
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

        <!-- Pagination Section -->
        <nav aria-label="Page navigation">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">
                Previous
              </a>
            </li>
            <li
              class="page-item"
              v-for="page in pageNumbers"
              :key="page"
              :class="{ active: page === currentPage }">
              <a class="page-link" href="#" @click.prevent="changePage(page)">
                {{ page }}
              </a>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">
                Next
              </a>
            </li>
          </ul>
          <div class="text-center mt-2">
            Showing {{ (currentPage - 1) * perPage + 1 }} to {{ Math.min(currentPage * perPage, totalBooks) }} of {{ totalBooks }} books
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
      filters: {
        title: '',
        author: '',
        read: ''
      },
      sortBy: 'title',
      sortOrder: 'asc',
      currentPage: 1,
      perPage: 10,
      totalBooks: 0,
      totalPages: 0,
      selectedBooks: []
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
      const params = new URLSearchParams();
      if (this.filters.title) params.append('title', this.filters.title);
      if (this.filters.author) params.append('author', this.filters.author);
      if (this.filters.read) params.append('read', this.filters.read);
      params.append('sort_by', this.sortBy);
      params.append('sort_order', this.sortOrder);
      params.append('page', this.currentPage);
      params.append('per_page', this.perPage);

      const path = `http://localhost:5001/books?${params.toString()}`;
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
          this.totalBooks = res.data.total_books;
          this.totalPages = res.data.total_pages;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    onFilterChange() {
      this.currentPage = 1;
      this.getBooks();
    },
    sort(field) {
      if (this.sortBy === field) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = field;
        this.sortOrder = 'asc';
      }
      this.currentPage = 1;
      this.getBooks();
    },
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.getBooks();
    },
    onPerPageChange() {
      this.currentPage = 1;
      this.getBooks();
    },
    onSelectAllChange() {
      if (this.selectAll) {
        this.selectedBooks = this.books.map(book => book.id);
      } else {
        this.selectedBooks = [];
      }
    },
    onSelectChange() {
      this.selectAll = this.selectedBooks.length === this.books.length;
    },
    batchDelete() {
      if (this.selectedBooks.length === 0) return;
      if (!confirm('Are you sure you want to delete selected books?')) return;
      
      const path = 'http://localhost:5001/books/batch';
      axios.post(path, {
        book_ids: this.selectedBooks,
        action: 'delete'
      })
        .then(() => {
          this.message = 'Books deleted!';
          this.showMessage = true;
          this.selectedBooks = [];
          this.getBooks();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    batchMarkRead() {
      if (this.selectedBooks.length === 0) return;
      
      const path = 'http://localhost:5001/books/batch';
      axios.post(path, {
        book_ids: this.selectedBooks,
        action: 'mark_read'
      })
        .then(() => {
          this.message = 'Books marked as read!';
          this.showMessage = true;
          this.selectedBooks = [];
          this.getBooks();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    batchMarkUnread() {
      if (this.selectedBooks.length === 0) return;
      
      const path = 'http://localhost:5001/books/batch';
      axios.post(path, {
        book_ids: this.selectedBooks,
        action: 'mark_unread'
      })
        .then(() => {
          this.message = 'Books marked as unread!';
          this.showMessage = true;
          this.selectedBooks = [];
          this.getBooks();
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
  computed: {
    selectAll: {
      get() {
        return this.selectedBooks.length === this.books.length && this.books.length > 0;
      },
      set(value) {
        if (value) {
          this.selectedBooks = this.books.map(book => book.id);
        } else {
          this.selectedBooks = [];
        }
      }
    },
    pageNumbers() {
      const pages = [];
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  created() {
    this.getBooks();
  },
};
</script>
